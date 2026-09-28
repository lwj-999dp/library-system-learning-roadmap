# -*- coding: utf-8 -*-
"""schemas.py · Pydantic 出入参模型（TODO）

对应文档
--------
docs/04-FastAPI与SQLAlchemy.md 「B. Pydantic v2」+ 练习 1 的 app/schemas.py
docs/05-鉴权与安全.md 练习 2 的 schemas.py（鉴权相关模型）

这个文件要做什么
----------------
把「前端传进来的东西」（请求模型）和「后端返回出去的东西」（响应模型）**分开定义**。
Pydantic 负责在数据进数据库之前就挡掉脏数据 —— 非法输入返回 **422**，不是 500。

两条铁律（面试常问，也是安全底线）
----------------------------------
1. **请求模型里绝不能出现 `available` / `role` / `is_deleted` / `password_hash`**
   —— 这些只能由后端决定。前端传了 `available`，库存就被前端控制了。
2. **响应模型里绝不能出现 `password_hash`**
   —— 字段不存在，就物理上不可能泄露。

基类 `ApiModel` 已经写好（camelCase 别名 + 支持从 ORM 对象构造），你只管写子类。

验收标准
--------
- [ ] `POST /api/books` 传 `{"id":"B003","title":"测试","stock":"abc"}` → **422**（不是 500）
- [ ] `POST /api/books` 传 `{"id":"B003","title":"测试","stock":1,"available":999}` → available 被忽略
- [ ] `GET /api/books` 出参里所有字段都是 camelCase（`pageSize`、`coverUrl`、`createdAt`）
- [ ] 任何接口的返回里都搜不到 `password_hash`
- [ ] `BookOut.model_validate(book_orm)` 能直接从 ORM 对象构造成功（靠 from_attributes）
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """全项目 Schema 基类（已给出，不用改）。

    * `alias_generator=to_camel`：后端写 `book_id`，JSON 里自动是 `bookId`（前端习惯）
    * `populate_by_name=True`：两种写法都接受
    * `from_attributes=True`：可以直接 `BookOut.model_validate(book_orm)`
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# =============================================================================
# 图书相关
# =============================================================================


class BookCreate(ApiModel):
    """新增图书的请求体。

    需要的字段：
        id         str，必填，格式 ^B\\d{3,}$（示例 B001）
        isbn       str | None，默认 None，max_length=20
        title      str，必填，min_length=1，max_length=200
        author     str，默认 ''，max_length=100
        publisher  str，默认 ''，max_length=100
        category   str，默认 ''，max_length=50
        price      Decimal，默认 Decimal("0.00")，ge=0，le=99999（★ 金额用 Decimal 不用 float）
        cover_url  str，默认 ''，max_length=255
        stock      int，必填，ge=0，le=100000

    ⚠️ 故意【没有】available —— 新书可借数由后端算（= stock），前端不许决定库存。
    提示：`Field(..., pattern=r"^B\\d{3,}$")` 管格式，`Field(ge=, le=)` 管范围。
    """

    # TODO ①：补字段


class BookUpdate(ApiModel):
    """修改图书的请求体（PATCH 语义：只改传上来的字段）。

    需要的字段（**全部可选**，默认 None）：
        title / author / category / price / stock

    提示：默认 None 表示「没传就不改」；配合路由里的
         `payload.model_dump(exclude_unset=True)` 才能区分「没传」和「显式传了 null」。
    ⚠️ 同样没有 available：改了 stock 之后由 crud.sync_book() 重算。
    """

    # TODO ②：补字段


class BookOut(ApiModel):
    """图书出参。

    需要的字段 = BookCreate 的全部 + 下面这些「只有后端算得出来」的：
        id / isbn / title / author / publisher / category / price / cover_url
        stock      int
        available  int        ← 只在这里出现
        created_at datetime
        updated_at datetime
    """

    # TODO ③：补字段


class BookListOut(ApiModel):
    """分页列表出参。

    需要的字段：
        total      int            总条数（★ 单独 SELECT COUNT(*) 查，不是 len(items)）
        page       int
        page_size  int            JSON 里是 pageSize
        items      list[BookOut]
    """

    # TODO ④：补字段


# =============================================================================
# 借阅相关
# =============================================================================


class BorrowCreate(ApiModel):
    """借书请求体（JSON 里是 bookId / readerId）。

    需要的字段：
        book_id    str，必填，min_length=1，max_length=16
        reader_id  str，必填，min_length=1，max_length=16
                   ⚠️ 阶段 5 加固后：普通读者只能借给自己（reader_id 从 Token 取），
                      管理员才能代借 —— 见 docs/05「水平越权」。
    """

    # TODO ⑤：补字段


class ReturnCreate(ApiModel):
    """还书请求体。

    需要的字段：
        record_id  int，必填，gt=0（借阅记录 id）
        reader_id  str，必填，min_length=1，max_length=16
    """

    # TODO ⑥：补字段


class BorrowOut(ApiModel):
    """借阅记录出参。

    需要的字段：
        id          int
        book_id     str
        user_id     str
        borrow_date date
        due_date    date
        return_date date | None
        status      str        ← 来自 BorrowRecord.status 这个 @property，不落库
    """

    # TODO ⑦：补字段


# =============================================================================
# 鉴权相关（阶段 5）
# =============================================================================


class UserCreate(ApiModel):
    """注册请求体。

    需要的字段：
        id        str，必填，pattern ^[AR]\\d{3,}$（示例 R001 / A001）
        name      str，必填，min_length=1，max_length=50
        phone     str | None，默认 None，max_length=20
        password  str，必填，min_length=8，max_length=64
                  ⚠️ 这里收的是**明文**，只用于立刻哈希，绝不入库、绝不进日志

    ⚠️⚠️ 故意【没有】role 字段：注册接口必须把角色写死成 reader，
         否则前端传个 "admin" 就把自己提权了（docs/05 常见坑 #7）。
    """

    # TODO ⑧：补字段


class UserOut(ApiModel):
    """用户出参。

    需要的字段：
        id / name / phone / role

    ⚠️ 故意没有 password / password_hash —— 字段都不存在，物理上不可能泄露。
    """

    # TODO ⑨：补字段


class TokenOut(ApiModel):
    """登录成功的出参。

    需要的字段：
        access_token  str
        token_type    str，默认 "bearer"
        user          UserOut     嵌套模型，顺手把当前用户信息带回去给前端
    """

    # TODO ⑩：补字段
