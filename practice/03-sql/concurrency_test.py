#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""concurrency_test.py · 超借 bug 并发复现脚本（阶段 3 练习 3 / 里程碑 ⑦）

===============================================================================
这个脚本要验证什么
===============================================================================
场景：B001 的 stock = 1、available = 1，让 5 个读者【同时】借这本书。
唯一正确的结果是：1 个 201（借到）+ 4 个 400（库存不足）。

它验证的是「并发下库存算得对不对」，也就是这两件事必须同时成立：
    ① 行锁 SELECT ... FOR UPDATE  —— 让并发请求【排队】
    ② 会话隔离级别 READ COMMITTED —— 让排队后重算 COUNT 能读到【最新已提交】数据
只做 ① 不做 ②：请求确实排队了，但排队后 COUNT 读到的是事务开始时的旧快照 → 照样超借。
只做 ② 不做 ①：每条语句都读最新数据，但没有任何东西阻止两个事务同时读到「还能借」→ 照样超借。
结论一句话：锁管排队，隔离级别管读得准，缺一不可。

------------------------------------------------------------------------------
修复前应该看到什么（bug 复现成功）
------------------------------------------------------------------------------
    读者 R001 -> 201  {"id":1,...}
    读者 R002 -> 201  {"id":2,...}
    读者 R003 -> 201  {"id":3,...}
    读者 R004 -> 201  {"id":4,...}
    读者 R005 -> 400  {"detail":"库存不足"}
    成功借出次数 = 4        ← 只要 > 1 就是 bug（1 本书被借走多次）
    🐛 判定：超借！
    （并发数不同可能是 2~4 个 201，取决于机器速度，只要 > 1 就说明有 bug）

------------------------------------------------------------------------------
修复后应该看到什么
------------------------------------------------------------------------------
    读者 R001 -> 201
    读者 R002 -> 400
    读者 R003 -> 400
    读者 R004 -> 400
    读者 R005 -> 400
    成功借出次数 = 1
    ✅ 判定：正确
    库存守恒校验 diff = 0

------------------------------------------------------------------------------
怎么跑
------------------------------------------------------------------------------
    # 0) 先装依赖，并确认阶段 4 的借书接口已经能调通、MySQL 里有 library 库
    pip install -r practice/requirements.txt

    # 1) 改下面【配置区】里的 MySQL 密码（其它一般不用改）

    # 2) 后端要开着（另开一个窗口）：
    cd practice/04-library-api
    uvicorn main:app --reload

    # 3) 跑并发测试（默认 5 并发）
    python concurrency_test.py
    python concurrency_test.py --concurrency 10
    python concurrency_test.py --token eyJhbGciOi...      # 阶段 5 开了鉴权后需要

说明：
  * 重置测试数据是【用 pymysql 直连数据库】做的，不依赖后端提供任何调试接口。
  * 脚本不会碰别的数据，只动 --book-id 这一本书的借阅记录和预约记录。
  * 退出码：0 = 结果正确；1 = 超借或环境有问题（方便接进 CI / 一键验证）。
===============================================================================
"""

from __future__ import annotations

import argparse
import concurrent.futures
import sys
import time
from typing import Any

import pymysql
import requests

# =============================================================================
# 配置区 —— 按你的环境改这里
# =============================================================================

# 后端地址（uvicorn 默认 8000）
BASE_URL: str = "http://127.0.0.1:8000"

# 借书接口路径（阶段 4 的 routers/borrows.py 里定义）
BORROW_PATH: str = "/api/borrows/borrow"

# 阶段 5 开了鉴权之后，把管理员登录拿到的 access_token 粘在这里。
# 留空字符串 = 不发 Authorization 请求头（阶段 4 还没鉴权时就是这样）。
TOKEN: str = ""

# 拿来做实验的图书编号：脚本会把它重置成 stock=1 / available=1
BOOK_ID: str = "B001"

# MySQL 连接参数 —— ★ 只需要改 password（以及必要时 user / port）
MYSQL_CONFIG: dict[str, Any] = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "CHANGE_ME",       # ← 改成你自己的 MySQL 密码
    "database": "library",
    "charset": "utf8mb4",
}

# 实验用的总库存（默认 1：最容易复现超借）
TEST_STOCK: int = 1

# 单个 HTTP 请求的超时时间（秒）
REQUEST_TIMEOUT: int = 15

# =============================================================================


def _connect() -> pymysql.connections.Connection:
    """返回一个自动提交的 MySQL 连接。"""
    return pymysql.connect(autocommit=True, **MYSQL_CONFIG)


def _force_utf8_stdout() -> None:
    """把标准输出/错误切成 UTF-8。

    为什么需要：Windows 的 cmd / PowerShell 默认编码是 GBK（cp936），
    一旦把输出重定向到文件或管道（`python concurrency_test.py > log.txt`、CI 里跑），
    print 一个 emoji（✅/❌/🐛）就会抛 UnicodeEncodeError 把脚本打断。
    这里统一改成 UTF-8 + errors="replace"，最坏情况只是显示成问号，不会崩。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 —— 老版本 Python / 特殊流：改不了就算了
            pass


def reset_test_data(reader_count: int) -> None:
    """把测试数据重置成「干净且一致」的起点。

    做四件事：
      1. 确认测试图书存在（不存在就建一本，stock = TEST_STOCK）
      2. 删掉这本书的全部借阅记录与预约记录（避免历史数据干扰）
      3. 把 stock / available 都设成 TEST_STOCK
      4. 确保 R001..R00N 这些读者存在（外键要求 users 表里得有他们）

    直接连 MySQL 改，不依赖后端提供任何调试接口 —— 调试接口是生产环境的大忌。
    """
    with _connect() as conn, conn.cursor() as cur:
        # 1) 图书必须存在
        cur.execute("SELECT id FROM books WHERE id = %s", (BOOK_ID,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO books (id, isbn, title, author, category, price, stock, available)"
                " VALUES (%s, NULL, %s, '并发测试用书', '测试', 0.00, %s, %s)",
                (BOOK_ID, f"并发测试用书 {BOOK_ID}", TEST_STOCK, TEST_STOCK),
            )
            print(f"[重置] 测试图书 {BOOK_ID} 不存在，已自动创建")

        # 2) 清掉这本书的借阅记录和预约记录
        cur.execute("DELETE FROM borrow_records WHERE book_id = %s", (BOOK_ID,))
        deleted_borrows = cur.rowcount
        cur.execute("DELETE FROM reservations WHERE book_id = %s", (BOOK_ID,))
        deleted_reservations = cur.rowcount

        # 3) 库存重置
        cur.execute(
            "UPDATE books SET stock = %s, available = %s, is_deleted = 0 WHERE id = %s",
            (TEST_STOCK, TEST_STOCK, BOOK_ID),
        )

        # 4) 读者要存在，否则外键约束会让借书接口报 500
        for i in range(1, reader_count + 1):
            cur.execute(
                "INSERT IGNORE INTO users (id, name, role, password_hash)"
                " VALUES (%s, %s, 'reader', '')",
                (f"R{i:03d}", f"压测读者{i}"),
            )

    print(
        f"[重置] {BOOK_ID}: stock = available = {TEST_STOCK}；"
        f"清掉借阅记录 {deleted_borrows} 条、预约记录 {deleted_reservations} 条；"
        f"确保 R001~R{reader_count:03d} 存在"
    )


def borrow(index: int) -> tuple[int, int, str, float]:
    """第 index 个读者借书，返回 (读者序号, HTTP 状态码, 响应体摘要, 耗时秒)。"""
    url = f"{BASE_URL.rstrip('/')}{BORROW_PATH}"
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        # Bearer 后面必须有一个空格，少一个空格后端会当成格式错误 → 401
        headers["Authorization"] = f"Bearer {TOKEN}"

    body = {"bookId": BOOK_ID, "readerId": f"R{index:03d}"}   # camelCase 是给前端的别名
    started = time.perf_counter()
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=REQUEST_TIMEOUT)
        elapsed = time.perf_counter() - started
        text = " ".join(resp.text.split())[:90]
        return index, resp.status_code, text, elapsed
    except requests.RequestException as exc:
        elapsed = time.perf_counter() - started
        return index, -1, f"{type(exc).__name__}: {exc}", elapsed


def fetch_db_state() -> dict[str, int]:
    """读数据库现状：这本书的 stock / available、在借数、ready 预约数、守恒差值。"""
    with _connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT stock, available FROM books WHERE id = %s", (BOOK_ID,))
        row = cur.fetchone()
        stock, available = (int(row[0]), int(row[1])) if row else (0, 0)

        cur.execute(
            "SELECT COUNT(*) FROM borrow_records WHERE book_id = %s AND return_date IS NULL",
            (BOOK_ID,),
        )
        borrowed = int(cur.fetchone()[0])

        cur.execute(
            "SELECT COUNT(*) FROM reservations WHERE book_id = %s AND status = 'ready'",
            (BOOK_ID,),
        )
        reserved = int(cur.fetchone()[0])

    return {
        "stock": stock,
        "available": available,
        "borrowed": borrowed,
        "reserved": reserved,
        "should_be_available": max(stock - borrowed - reserved, 0),
        "diff": (stock - available) - borrowed - reserved,
    }


def explain_status(code: int) -> str:
    """把状态码翻译成一句人话，帮新手快速定位卡在哪一步。"""
    hints = {
        -1: "连不上后端：uvicorn 起了吗？BASE_URL 对吗？",
        400: "库存不足（这正是修复成功时该出现的结果）",
        401: "鉴权失败：阶段 5 开了鉴权，请用 --token 传管理员 Token",
        403: "权限不足：这个接口需要读者/管理员角色",
        404: "接口不存在：阶段 4 的借书接口还没写？或者路径写错了",
        422: "参数校验失败：请求体字段名对不上（应该是 bookId / readerId）",
        500: "后端抛异常了：多半是 sync_book / 事务逻辑没写完，去看 uvicorn 的日志",
        501: "接口还没实现（脚手架里的 TODO 占位）",
    }
    return hints.get(code, "")


def main() -> int:
    # 命令行参数可以覆盖模块级配置，所以这里要声明 global
    global BASE_URL, TOKEN, BOOK_ID, TEST_STOCK

    _force_utf8_stdout()

    parser = argparse.ArgumentParser(
        description="超借 bug 并发复现脚本（阶段 3 练习 3）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--concurrency", type=int, default=5, help="并发请求数")
    parser.add_argument("--base-url", default=BASE_URL, help="后端地址")
    parser.add_argument("--token", default=TOKEN, help="Bearer Token（阶段 5 需要）")
    parser.add_argument("--book-id", default=BOOK_ID, help="测试用图书编号")
    parser.add_argument("--stock", type=int, default=TEST_STOCK, help="测试用总库存")
    parser.add_argument("--no-reset", action="store_true", help="跳过数据重置（自己手动准备数据）")
    args = parser.parse_args()

    # 命令行参数覆盖模块级配置
    BASE_URL, TOKEN, BOOK_ID, TEST_STOCK = args.base_url, args.token, args.book_id, args.stock

    n = args.concurrency
    if n < 2:
        print("⚠️  并发数 < 2 复现不出并发问题，请用 --concurrency 5 以上")
        return 1

    print("=" * 74)
    print("超借 bug 并发复现测试")
    print("=" * 74)
    print(f"后端地址   : {BASE_URL}{BORROW_PATH}")
    print(f"测试图书   : {BOOK_ID}（stock = {TEST_STOCK}）")
    print(f"并发数     : {n}")
    print(f"携带 Token : {'是' if TOKEN else '否（阶段 4 还没鉴权）'}")
    print("-" * 74)

    # ---------- 1. 重置数据 ----------
    if not args.no_reset:
        try:
            reset_test_data(n)
        except pymysql.Error as exc:
            print(f"❌ 连不上 MySQL（{exc}）")
            print("   请检查 MYSQL_CONFIG 里的 user / password / port，以及是否已执行 schema.sql")
            return 1
    print("-" * 74)

    # ---------- 2. 并发借书 ----------
    print(f"🚀 同时发起 {n} 个借书请求……\n")
    wall_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as pool:
        results = list(pool.map(borrow, range(1, n + 1)))
    wall = time.perf_counter() - wall_start

    seen_success = 0
    for index, code, body, cost in results:
        if code == 201:
            seen_success += 1
            # 前 TEST_STOCK 个 201 是正常的，再多的就是超借（用 🐛 标出来）
            flag = "✅" if seen_success <= TEST_STOCK else "🐛"
        elif code in (400, 409):
            flag = "⚠️ "
        else:
            flag = "❌"
        print(f"{flag} 读者 R{index:03d} -> {code:<4} {cost * 1000:6.0f} ms  {body}")

    # ---------- 3. 统计与判定 ----------
    successes = sum(1 for _, code, _, _ in results if code == 201)
    rejected = sum(1 for _, code, _, _ in results if code in (400, 409))

    print("\n" + "=" * 74)
    print(f"成功借出次数（201） = {successes}")
    print(f"被拒绝次数（400/409）= {rejected}")
    print(f"总耗时               = {wall * 1000:.0f} ms")

    # 把非预期状态码的原因打出来，省得新手对着一串 401/501 发懵
    weird = sorted({code for _, code, _, _ in results if code not in (201, 400, 409)})
    if weird:
        print("-" * 74)
        print("⚠️  出现了非预期状态码，逐个解释：")
        for code in weird:
            print(f"   {code} → {explain_status(code)}")

    # ---------- 4. 库存守恒校验 ----------
    print("-" * 74)
    try:
        state = fetch_db_state()
        print(
            f"数据库现状：stock={state['stock']}  available={state['available']}  "
            f"未归还={state['borrowed']}  ready 预约={state['reserved']}"
        )
        print(
            f"按公式应有可借数 = {state['should_be_available']}；"
            f"守恒校验 diff = {state['diff']}"
        )
    except pymysql.Error as exc:
        print(f"⚠️  守恒校验跳过（读库失败：{exc}）")
        state = None

    # ---------- 5. 结论 ----------
    print("=" * 74)
    if successes > TEST_STOCK:
        print(f"🐛 判定：超借！{TEST_STOCK} 本书被借走了 {successes} 次。")
        print("   原因：MySQL 默认 REPEATABLE READ，事务内第一次非锁定读就把 Read View 定死；")
        print("        即使拿到行锁，锁内重新 COUNT 读到的还是旧快照，锁等于白加。")
        print("   修复：① 借书事务第一句就 SELECT ... FOR UPDATE（routers/borrows.py）")
        print("         ② engine 上挂 READ COMMITTED 事件监听器（database.py 已给）")
        ok = False
    elif successes == TEST_STOCK:
        print(f"✅ 判定：正确！{TEST_STOCK} 本书只被借出 {successes} 次，其余都被拦住了。")
        ok = True
    else:
        print(f"❓ 判定：借出 {successes} 次 < 库存 {TEST_STOCK}，并发没竞争起来或接口有问题。")
        print("   试着把 --concurrency 调大，或检查是不是所有请求都失败了（看上面的状态码）。")
        ok = False

    if state is not None and state["diff"] != 0:
        print(f"⚠️  库存守恒校验 diff = {state['diff']}（应为 0）：available 已经和事实表对不上了，")
        print("   检查是不是哪里写了 available += 1 / -= 1，或者该调 sync_book() 的地方没调。")
        ok = False

    print("-" * 74)
    print("对照组检查表（面试要能口述）：")
    print("  只加 FOR UPDATE       → 请求排队了，但 COUNT 读旧快照 → 照样超借")
    print("  只改 READ COMMITTED   → 读得新了，但没人拦并发     → 照样超借")
    print("  FOR UPDATE + RC       → 锁管排队，隔离级别管读得准 → 唯一正确解")
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
