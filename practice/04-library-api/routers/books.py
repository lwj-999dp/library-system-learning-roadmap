# -*- coding: utf-8 -*-
"""routers/books.py · 图书 CRUD 接口（TODO，阶段 4 练习 1）

对应文档
--------
docs/04-FastAPI与SQLAlchemy.md 练习 1 的 app/routers/books.py（结构、状态码、白名单都在那里）

这个文件要做什么
----------------
5 个接口，全部以 `/api/books` 开头：

| 方法   | 路径                | 作用             | 成功码 | 该抛的错误                     |
|--------|---------------------|------------------|:------:|--------------------------------|
| GET    | `/api/books`        | 列表：分页+搜索+排序 | 200 | —                              |
| GET    | `/api/books/{id}`   | 详情             | 200    | 404 图书不存在                  |
| POST   | `/api/books`        | 新增             | 201    | 409 编号已存在 / 422 参数非法   |
| PATCH  | `/api/books/{id}`   | 修改（部分字段）  | 200    | 404 不存在 / 400 新库存 < 在借数 |
| DELETE | `/api/books/{id}`   | **软删除**       | 204    | 404 不存在 / 400 还有未还的借阅 |

必须遵守
--------
1. 所有查询都带 `Book.is_deleted == 0`（软删除的代价：漏一处就是 bug）
2. 全部用 `select()` 2.0 风格，禁止 `db.query(`
3. 出参一律 `response_model=`（防止 `password_hash` 之类的字段漏出去）
4. 排序字段**必须走白名单**，绝不把用户输入拼进 `order_by`（SQL 注入 + 500）
5. `available` 只能由 `crud.sync_book()` 算，前端传什么都不许信
6. 删除是 `is_deleted = 1`，**绝不 `DELETE FROM`**（有借阅历史的书会报 ERROR 1451）

阶段 5 加固（做完鉴权再回来加，先别急着加，否则阶段 4 测不了）
------------------------------------------------------------
    from security import require_admin, require_reader
    # 读接口：user: User = Depends(require_reader)     → 未登录 401
    # 写接口：admin: User = Depends(require_admin)     → 读者 403

验收标准
--------
- [ ] `GET /api/books?page_size=99999` → **422**（被 `le=100` 挡住）
- [ ] `POST /api/books` 传 `stock:"abc"` → **422**，不是 500
- [ ] `GET /api/books/{不存在的id}` → **404**
- [ ] `DELETE /api/books/B001` → **204**，MySQL 里 `is_deleted = 1` 且数据还在
- [ ] `GET /api/books?keyword=Python&sort=-available&page=1&page_size=10` 正常工作
- [ ] 打开 `SQL_ECHO=true`，自己数一次「借一本书」发了几条 SQL（练习 2 的验收）
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from crud import count_borrowed, run_maintenance, sync_book
from database import get_db
from models import Book
from schemas import BookCreate, BookListOut, BookOut, BookUpdate

# 阶段 5 再打开这一行：
# from security import require_admin, require_reader

router = APIRouter(prefix="/api/books", tags=["图书"])

# 排序白名单（★ 只允许用户传 key，拼 SQL 的永远是这里的表达式）
# ⚠️ 必须放在函数里或者 models.py 写完之后再放模块级：
#    模块级引用 Book.title 会在 import 阶段执行 —— 你还没补 models.py 的字段时，
#    `uvicorn main:app` 会直接起不来（AttributeError）。
#
# 参考形状（照这个写进 list_books 里）：
#     SORT_MAP = {
#         "title": Book.title.asc(),
#         "-title": Book.title.desc(),
#         "created_at": Book.created_at.asc(),
#         "-created_at": Book.created_at.desc(),
#         "available": Book.available.asc(),
#         "-available": Book.available.desc(),
#     }
#     ... .order_by(SORT_MAP[sort])


@router.get("", response_model=BookListOut, summary="图书列表（分页 + 搜索 + 排序）")
def list_books(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，上限 100"),
    keyword: str | None = Query(None, max_length=50, description="书名/作者/ISBN 模糊搜索"),
    category: str | None = Query(None, max_length=50, description="分类精确匹配"),
    sort: Literal[
        "title", "-title", "created_at", "-created_at", "available", "-available"
    ] = Query("-created_at", description="排序字段，带 - 前缀表示倒序"),
):
    """图书列表：分页 + 模糊搜索 + 分类过滤 + 白名单排序。

    TODO ①：按顺序做这五步：
        0. `run_maintenance(db)` —— 惰性维护挂读接口最前面（阶段 4 练习 3；没做就注释掉）
        1. 基础语句：`stmt = select(Book).where(Book.is_deleted == 0)`
        2. keyword 非空时加 `or_(Book.title.like(like), Book.author.like(like), Book.isbn.like(like))`，
           like 写成 `f"%{keyword}%"`；category 非空时加 `Book.category == category`
        3. `total` 单独查一次：
           `db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()`
           ⚠️ 不要用 `len(items)` —— 那样 total 永远等于当前页条数
        4. `.order_by(SORT_MAP[sort]).offset((page - 1) * page_size).limit(page_size)`
           `.scalars().all()`   ← 别忘了 `.scalars()`
        5. `return BookListOut(total=total, page=page, page_size=page_size, items=rows)`

    注意 page_size 已经用 `le=100` 卡住了上限，别把 Query 约束删掉 —— 否则
    `?page_size=999999` 一次就能把数据库拖垮。
    """
    raise NotImplementedError("TODO: routers/books.list_books() —— 分页+搜索+白名单排序（见函数内 5 步）")


@router.get("/{book_id}", response_model=BookOut, summary="图书详情")
def get_book(book_id: str, db: Session = Depends(get_db)):
    """按编号查一本书。

    TODO ②：
        book = db.get(Book, book_id)
        查不到 **或** `book.is_deleted` → `raise HTTPException(404, detail="图书不存在")`
        （软删除的书对外必须表现为「不存在」）
    """
    raise NotImplementedError("TODO: routers/books.get_book() —— db.get + 404")


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED, summary="新增图书")
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    """新增图书（阶段 5 之后这个接口要管理员权限）。

    TODO ③：
        1. `db.get(Book, payload.id)` 已存在 → `HTTPException(409, detail="图书编号已存在")`
        2. `book = Book(**payload.model_dump(), available=payload.stock)`
           ★ 新书全部可借：available 由后端给，请求模型里根本没有这个字段
        3. `db.add(book)` → `db.commit()` → `db.refresh(book)` → `return book`
           为什么要 refresh：让 created_at / updated_at 这类 server_default 的值回到对象上
    """
    raise NotImplementedError("TODO: routers/books.create_book() —— 409 查重 + available=stock")


@router.patch("/{book_id}", response_model=BookOut, summary="修改图书（只改传上来的字段）")
def update_book(book_id: str, payload: BookUpdate, db: Session = Depends(get_db)):
    """PATCH 语义：只改前端真正传上来的字段。

    TODO ④：
        1. 查书，查不到或已删除 → 404
        2. `for field, value in payload.model_dump(exclude_unset=True).items(): setattr(...)`
           `exclude_unset=True` 是 PATCH 的关键：区分「没传」和「显式传了 null」
        3. 如果改了 stock（`if "stock" in payload.model_fields_set:`）：
           a. 新库存 < 当前在借数 → `HTTPException(400, detail="新库存小于当前在借数，改不了")`
              （用 `crud.count_borrowed(db, book_id)` 判断）
           b. `crud.sync_book(db, book_id)`  ★ 改了 stock 必须重算 available
        4. `db.commit()` → `db.refresh(book)` → `return book`

    ⚠️ 绝不要在这里写 `book.available = payload.stock` 这类「直接赋值」。
    """
    raise NotImplementedError("TODO: routers/books.update_book() —— exclude_unset + sync_book")


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="下架图书（软删除）")
def delete_book(book_id: str, db: Session = Depends(get_db)):
    """软删除（下架）图书，成功返回 204，没有响应体。

    TODO ⑤：
        1. 查书，查不到或已删除 → 404
        2. `crud.count_borrowed(db, book_id) > 0` → `HTTPException(400, detail="还有未归还的借阅，不能删除")`
        3. `book.is_deleted = True`；`book.available = 0`（下架的书不可再借）
        4. `db.commit()`，函数**不要 return 任何东西**（204 不能有响应体）

    ⚠️ 绝不能写 `db.delete(book)` / `DELETE FROM books`：
       ① 有借阅历史的书会被外键挡住，报 ERROR 1451
       ② 借阅记录会变成孤儿，历史查不出来
       ③ 删错了没法恢复
    想验证这一点：直接在 MySQL 里 `DELETE FROM books WHERE id='B001'` 看报什么错。
    """
    raise NotImplementedError("TODO: routers/books.delete_book() —— is_deleted=True 软删除")
