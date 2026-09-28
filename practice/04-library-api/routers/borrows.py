# -*- coding: utf-8 -*-
"""routers/borrows.py · 借书 / 还书接口（TODO ★ 行锁在这里，阶段 3 的 bug 在这里修好）

对应文档
--------
docs/03-数据库与SQL.md 练习 3「超借 bug 复现与修复」（原理 + 修复前/后对照）
docs/04-FastAPI与SQLAlchemy.md 练习 2 的 app/crud.py `borrow_book` / `return_book`、app/routers/borrows.py

这个文件要做什么
----------------
| 方法 | 路径                    | 作用          | 成功码 | 失败                     |
|------|-------------------------|---------------|:------:|--------------------------|
| POST | `/api/borrows/borrow`   | 借书 ★核心    | 201    | 400 库存不足 / 重复借 / 404 图书不存在 |
| POST | `/api/borrows/return`   | 还书          | 200    | 400 记录不存在或已归还 / 403 还别人的书 |
| GET  | `/api/borrows`          | 借阅记录列表  | 200    | —                        |

★★★ 借书接口是【全文档高潮】，必须做到三件事
--------------------------------------------
① **锁定读放在事务的第一句**：`select(Book).where(...).with_for_update()` → SQL 里的 `FOR UPDATE`
② 锁内重新统计「未归还数 + ready 预约数」，判断能不能借（不要信任何缓存值）
③ 通过后再 `INSERT` 借阅记录 → `db.flush()` → `crud.sync_book()` → `db.commit()`

为什么 ① 和 ② 缺一不可：
    * 只加行锁：请求确实排队了，但 MySQL 默认 REPEATABLE READ 下，
      排队后重算 COUNT 读到的还是**事务开始时的旧快照** → 照样超借
      （快照读会绕过行锁！）
    * 只改 READ COMMITTED（database.py 已经挂好）：每条语句读到最新数据，
      但没有任何东西阻止两个事务同时读到「还能借」→ 照样超借（丢失更新）
    * **锁负责排队，隔离级别负责读得准，两者一起才有正确结果。**

⚠️ 还有一个隐蔽的坑：事务里只要先出现**任意一条普通 SELECT**
   （查用户、`db.refresh()`、参数校验触发的查询），Read View 就提前定死了。
   所以借书接口里不要在锁定读之前查任何东西。

验收标准
--------
- [ ] 借出一本 → `available` 减 1；归还一本 → 加 1
- [ ] 同一读者对同一本书借两次 → **400**
- [ ] `available = 0` 时借书 → **400 库存不足**
- [ ] `SQL_ECHO=true` 时能亲眼看到借书的第一条 SQL 带 `FOR UPDATE`
- [ ] `python ../03-sql/concurrency_test.py` 修复前 ≥2 个 201，修复后只有 1 个 201
- [ ] 守恒校验 `SELECT SUM(stock-available) - COUNT(在借) - COUNT(ready预约)` 恒为 0
"""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from crud import DEFAULT_LOAN_DAYS, count_borrowed, count_reserved, run_maintenance, sync_book
from database import get_db
from models import Book, BorrowRecord, Reservation
from schemas import BorrowCreate, BorrowOut, ReturnCreate

# 阶段 5 再打开这两行：
# from security import require_reader
# from models import User

router = APIRouter(prefix="/api/borrows", tags=["借阅"])


@router.post("/borrow", response_model=BorrowOut, status_code=status.HTTP_201_CREATED,
             summary="借书 ★ 先加行锁再判断库存")
def borrow(payload: BorrowCreate, db: Session = Depends(get_db)):
    """借书。成功 201 返回借阅记录；业务不满足 400。

    TODO ①（★ 全项目最重要的一段代码）：按顺序写，顺序错了 bug 就回来了。

        # 第 1 句就必须是锁定读！它生成 SQL: SELECT ... FOR UPDATE
        book = db.execute(
            select(Book)
            .where(Book.id == payload.book_id, Book.is_deleted == 0)
            .with_for_update()          # ★ 没有它，5 并发就是 4~5 个 201
        ).scalar_one_or_none()
        if book is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="图书不存在")

        # 同一读者不能对同一本书有两条未归还记录（否则一个人能刷满库存）
        dup = db.execute(
            select(func.count()).select_from(BorrowRecord).where(
                BorrowRecord.user_id == payload.reader_id,
                BorrowRecord.book_id == payload.book_id,
                BorrowRecord.return_date.is_(None),
            )
        ).scalar_one()
        if dup:
            db.rollback()
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="你已借阅此书且未归还")

        # 锁内判断库存：READ COMMITTED 保证这里读到的是别人刚提交的记录
        if book.stock - count_borrowed(db, payload.book_id) - count_reserved(db, payload.book_id) <= 0:
            db.rollback()               # 先放掉行锁，再报错
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="库存不足")

        today = date.today()
        record = BorrowRecord(
            user_id=payload.reader_id, book_id=payload.book_id,
            borrow_date=today, due_date=today + timedelta(days=DEFAULT_LOAN_DAYS),
            return_date=None, renew_count=0,
        )
        db.add(record)
        db.flush()                      # ★ 必须先 flush，sync_book 才 COUNT 得到这一条
        sync_book(db, payload.book_id)  # ★ 唯一的库存计算入口
        db.commit()
        db.refresh(record)
        return record

    易错点自查：
      * 用了 `db.get(Book, ...)` 而不是 `select(...).with_for_update()` → 没有锁，超借
      * `with_for_update()` 前还有一句普通 SELECT → 快照提前定死，等于没锁
      * 忘了 `db.flush()` 就调 `sync_book()` → 新记录还没进事务，COUNT 少 1，available 偏大
      * 手动写 `book.available -= 1` → 违反「唯一库存入口」铁律
      * 判断条件写成 `book.available <= 0` → 用的是可能过期的字段值，要以事实表重算为准

    阶段 5 加固（做完鉴权再回来加）：
      * 加 `user: User = Depends(require_reader)`：普通读者只能 `user.id`，忽略 body 里的 readerId；
        管理员可以代借（这时才用 payload.reader_id）
      * 注意：`practice/03-sql/concurrency_test.py` 用同一个 Token 传不同 readerId，
        所以它需要**管理员 Token** 才能跑（管理员可代借）
    """
    raise NotImplementedError(
        "TODO: routers/borrows.borrow() —— 第一句 with_for_update() 行锁 + 锁内重算 + flush + sync_book"
    )


@router.post("/return", response_model=BorrowOut, summary="还书")
def return_book(payload: ReturnCreate, db: Session = Depends(get_db)):
    """还书：填上 `return_date`，再重算库存。

    TODO ②：
        record = db.execute(
            select(BorrowRecord)
            .where(BorrowRecord.id == payload.record_id,
                   BorrowRecord.return_date.is_(None))     # 已还的不能再还
            .with_for_update()                              # ★ 并发还书也要排队
        ).scalar_one_or_none()
        if record is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="借阅记录不存在或已归还")
        if record.user_id != payload.reader_id:             # ★ 水平越权拦截
            db.rollback()
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="不能操作他人的借阅记录")

        record.return_date = date.today()
        db.flush()
        sync_book(db, record.book_id)      # ★ 归还后必须重算（available 会 +1）
        db.commit()
        db.refresh(record)
        return record

    ⚠️ 还书也要加锁：两个并发还书如果不排队，sync_book 重算可能读到旧快照。
    ⚠️ 阶段 5：`record.user_id != payload.reader_id` 里的 reader_id 应改成
       `Depends(require_reader)` 拿到的 `user.id`（管理员可代还），
       否则读者改一下 body 里的 readerId 就能还别人的书。
    """
    raise NotImplementedError("TODO: routers/borrows.return_book() —— 锁定读 + 校验归属 + sync_book")


@router.get("", summary="借阅记录列表（惰性维护挂这里）")
def list_borrows(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    only_active: bool = Query(True, description="只看未归还的"),
):
    """借阅记录列表：分页返回，带上推导出来的状态。

    TODO ③（可选）：
        0. `run_maintenance(db)` —— 读接口最频繁，惰性维护挂这里性价比最高
        1. 基础语句 `select(BorrowRecord)`；`only_active` 为真时加
           `.where(BorrowRecord.return_date.is_(None))`
        2. 按 `BorrowRecord.id.desc()` 排序，`offset/limit` 分页，`.scalars().all()`
        3. 返回 `{"total": ..., "page": ..., "page_size": ..., "items": rows}`
           （阶段 5 加固：普通读者只能看自己的 → 强制加
            `.where(BorrowRecord.user_id == user.id)`，绝不能从查询参数取 user_id！）

    ⚠️ 不要在这里 for 循环访问 `record.book.title` —— 那是 N+1（1 + N 条 SQL）。
       要用关联数据就用 `.options(selectinload(BorrowRecord.book))` 压成 2 条。
    """
    raise NotImplementedError("TODO: routers/borrows.list_borrows() —— 分页 + run_maintenance")


# 说明：Reservation（预约）相关接口不在本脚手架的 TODO 清单里，
# 想练手可以照着 docs/03 的公式自己加：
#   POST /api/borrows/reserve  → 建 pending 预约
#   POST /api/borrows/pickup   → ready → fulfilled（借走）
#   POST /api/borrows/cancel   → 取消（若原来是 ready，必须 sync_book 把占位还回去）
