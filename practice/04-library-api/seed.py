# -*- coding: utf-8 -*-
"""seed.py · 演示数据脚本（★ 完整，不需要你改）

对应文档
--------
docs/05-鉴权与安全.md 练习 2（用户要有真实 bcrypt 哈希才能登录）

怎么跑
------
    cd practice/04-library-api
    copy .env.example .env      # 先填好数据库密码
    python seed.py

依赖说明
--------
本脚本会调用 `security.hash_password()`（阶段 5 练习 1 的 TODO）。
**请先把它实现出来**，否则会看到 `NotImplementedError: TODO: security.hash_password`。

它做什么
--------
1. 建 4 个演示账号（密码全部用 bcrypt 哈希后入库，库里绝不会出现明文）
2. 建 5 本演示图书（用 ON DUPLICATE KEY UPDATE，可重复执行，**幂等**）
3. 打印账号密码和校验 SQL，方便你马上登录 / 对账

为什么用原生 SQL 而不是 ORM
---------------------------
建表的权威脚本是 practice/03-sql/schema.sql，seed 只负责灌数据。
用 `text()` + 绑定参数走原生 SQL，好处是**不依赖 models.py 写完没有**，
你可以在阶段 4 刚开工时就把账号准备好。
（顺带演示：`text()` 里永远用 `:name` 绑定参数，绝不拼字符串 —— 那是 SQL 注入。）
"""

from __future__ import annotations

import sys

from sqlalchemy import text

from database import engine
from security import hash_password

# -----------------------------------------------------------------------------
# 演示账号：⚠️ 这些是**教学用弱密码**，只在本机练手，绝不要用到真实环境
# -----------------------------------------------------------------------------
DEMO_USERS: list[dict[str, str]] = [
    {"id": "A001", "name": "管理员", "phone": "13800000001", "role": "admin", "password": "Admin@12345"},
    {"id": "R001", "name": "张三", "phone": "13800000002", "role": "reader", "password": "Reader@12345"},
    {"id": "R002", "name": "李四", "phone": "13800000003", "role": "reader", "password": "Reader@12345"},
    {"id": "R003", "name": "王五", "phone": "13800000004", "role": "reader", "password": "Reader@12345"},
]

DEMO_BOOKS: list[dict[str, object]] = [
    {"id": "B001", "isbn": "9787115428028", "title": "Python 编程：从入门到实践",
     "author": "Eric Matthes", "publisher": "人民邮电出版社", "category": "编程", "price": 89.80, "stock": 1},
    {"id": "B002", "isbn": "9787111544937", "title": "深入理解计算机系统",
     "author": "Randal Bryant", "publisher": "机械工业出版社", "category": "计算机", "price": 139.00, "stock": 3},
    {"id": "B003", "isbn": "9787111213826", "title": "算法导论",
     "author": "Thomas Cormen", "publisher": "机械工业出版社", "category": "计算机", "price": 128.00, "stock": 2},
    {"id": "B004", "isbn": "9787020002207", "title": "红楼梦",
     "author": "曹雪芹", "publisher": "人民文学出版社", "category": "文学", "price": 59.70, "stock": 5},
    {"id": "B005", "isbn": "9787544270878", "title": "解忧杂货店",
     "author": "东野圭吾", "publisher": "南海出版公司", "category": "文学", "price": 39.50, "stock": 2},
]

_UPSERT_USER = text(
    """
    INSERT INTO users (id, name, phone, role, password_hash, is_deleted)
    VALUES (:id, :name, :phone, :role, :password_hash, 0)
    ON DUPLICATE KEY UPDATE
        name = :name, phone = :phone, role = :role,
        password_hash = :password_hash, is_deleted = 0
    """
)

_UPSERT_BOOK = text(
    """
    INSERT INTO books (id, isbn, title, author, publisher, category, price, stock, available, is_deleted)
    VALUES (:id, :isbn, :title, :author, :publisher, :category, :price, :stock, :available, 0)
    ON DUPLICATE KEY UPDATE
        isbn = :isbn, title = :title, author = :author, publisher = :publisher,
        category = :category, price = :price, stock = :stock,
        available = :available, is_deleted = 0
    """
)

_COUNT_BORROWED = text(
    "SELECT COUNT(*) FROM borrow_records WHERE book_id = :book_id AND return_date IS NULL"
)

_COUNT_RESERVED = text(
    "SELECT COUNT(*) FROM reservations WHERE book_id = :book_id AND status = 'ready'"
)

_CONSERVATION_CHECK = text(
    """
    SELECT (SELECT IFNULL(SUM(stock - available), 0) FROM books WHERE is_deleted = 0)
         - (SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL)
         - (SELECT COUNT(*) FROM reservations  WHERE status = 'ready') AS diff
    """
)


def seed_users() -> int:
    """插入 / 更新演示用户，返回实际处理的条数。"""
    with engine.begin() as conn:
        for user in DEMO_USERS:
            # bcrypt 一次约 200~300 ms，4 个账号约 1 秒，属正常
            conn.execute(
                _UPSERT_USER,
                {
                    "id": user["id"],
                    "name": user["name"],
                    "phone": user["phone"],
                    "role": user["role"],
                    "password_hash": hash_password(user["password"]),
                },
            )
    return len(DEMO_USERS)


def seed_books() -> int:
    """插入 / 更新演示图书，available 按公式重算（幂等，可重复跑）。

    ⚠️ 这里的 available 是按 `stock - 未归还借阅数 - ready 预约数` 算出来的
       （和 crud.sync_book() 同一个公式）。seed 脚本故意用原生 SQL + 手动算，
       好处是**不依赖 models.py / crud.py 写完没有**，阶段 4 一开始就能准备数据。
       正式业务代码里，这个公式**只允许出现在 crud.sync_book() 一处**。
    """
    with engine.begin() as conn:
        for book in DEMO_BOOKS:
            borrowed = conn.execute(_COUNT_BORROWED, {"book_id": book["id"]}).scalar_one()
            reserved = conn.execute(_COUNT_RESERVED, {"book_id": book["id"]}).scalar_one()
            available = max(int(book["stock"]) - int(borrowed) - int(reserved), 0)
            conn.execute(_UPSERT_BOOK, {**book, "available": available})
    return len(DEMO_BOOKS)


def verify() -> int:
    """跑一次库存守恒校验，返回 diff（正常应该是 0）。"""
    with engine.begin() as conn:
        diff = conn.execute(_CONSERVATION_CHECK).scalar_one()
    return int(diff or 0)


def main() -> int:
    # Windows 上输出重定向到文件/管道时编码可能是 GBK，print emoji 会崩，这里统一成 UTF-8
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass

    print("=" * 70)
    print("灌入演示数据（可重复执行，幂等）")
    print("=" * 70)

    try:
        users = seed_users()
    except NotImplementedError:
        print("❌ security.hash_password() 还是 TODO，先完成它再跑 seed.py")
        print("   对应文档：docs/05-鉴权与安全.md 练习 2 的 app/security.py")
        return 1
    except Exception as exc:  # noqa: BLE001 —— 数据库连不上时给出人话提示
        print(f"❌ 数据库操作失败：{exc}")
        print("   请检查：① MySQL 起了吗 ② .env 里的 DATABASE_URL 对吗")
        print("          ③ 有没有先执行 practice/03-sql/schema.sql")
        return 1

    books = seed_books()
    diff = verify()

    print(f"✅ 用户 {users} 个、图书 {books} 本 已就绪")
    print("-" * 70)
    print("演示账号（密码只在这里出现，数据库里只有 $2b$12$... 哈希）：")
    for user in DEMO_USERS:
        print(f"   {user['id']}  {user['name']:<4} {user['role']:<6} 密码 {user['password']}")
    print("-" * 70)
    print(f"库存守恒校验 diff = {diff}（应为 0；不为 0 说明以前有地方手改过 available）")
    print("登录示例：")
    print('   curl -s -X POST http://127.0.0.1:8000/api/auth/login \\')
    print('        -d "username=A001&password=Admin@12345"')
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
