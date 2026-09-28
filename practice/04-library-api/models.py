# -*- coding: utf-8 -*-
"""models.py · ORM 模型（TODO ★ 你的第一件事）

对应文档
--------
docs/04-FastAPI与SQLAlchemy.md 「C. SQLAlchemy 2.0 ORM」+ 练习 1 的 app/models.py
建表权威脚本：practice/03-sql/schema.sql（字段名、类型以它为准，不要自己改名！）

这个文件要做什么
----------------
把 4 张表的每一列翻译成 SQLAlchemy 2.0 的 **`Mapped[类型]` + `mapped_column(...)`** 写法，
并配上 `relationship()` 双向关联。

⚠️ 为什么先做这个文件：models.py 不填，crud / routers 里的每一句查询都无从下手。
   字段名必须和 schema.sql 完全一致（数据库那边已经建好了，ORM 只是映射）。

写法模板（照这个风格写，不要用旧的 Column(...)）
------------------------------------------------
    # 普通列
    title: Mapped[str] = mapped_column(String(200), index=True, comment="书名")
    # 可空列：类型写成 `X | None`，并给 default=None
    isbn: Mapped[str | None] = mapped_column(String(20), default=None)
    # 有默认值的列
    stock: Mapped[int] = mapped_column(Integer, default=0)
    # 金额一律用 Numeric，别用 Float
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    # 时间戳：让 MySQL 自己填（server_default），而不是 Python 端
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    # 双向关联（两边都要写 back_populates，否则改了 A 那边看不到）
    borrow_records: Mapped[list["BorrowRecord"]] = relationship(back_populates="book")

验收标准
--------
- [ ] `python -c "import models"` 无报错
- [ ] 4 个模型的主键、可空性、默认值和 schema.sql 完全一致
      （`db.get(Book, "B001")` 能查到，`book.title` 能读到值）
- [ ] `relationship` 两边都写了 `back_populates`
- [ ] 全项目搜不到 `db.query(`，全部用 `select()`
- [ ] ★ 借阅状态**不落库**：`BorrowRecord.status` 是由日期推导的 `@property`
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    """用户表 users（管理员 + 读者）。

    需要的列（对照 schema.sql 的 users 表）：
        id            VARCHAR(16)  主键，'A001' / 'R001'
        name          VARCHAR(50)  非空
        phone         VARCHAR(20)  可空 + 唯一
        role          ENUM('admin','reader')，默认 'reader'
        password_hash VARCHAR(100) 非空，默认 ''，存 bcrypt 哈希
        is_deleted    TINYINT(1)   非空，默认 0
        created_at    DATETIME     非空，默认 CURRENT_TIMESTAMP

    关系：
        borrow_records  一个用户有多条借阅记录
        reservations    一个用户有多条预约
    """

    __tablename__ = "users"

    # 示例列（已给出）：主键
    id: Mapped[str] = mapped_column(String(16), primary_key=True, comment="编号 A001 / R001")

    # TODO ①：在这里补 User 剩下的列
    #   提示：phone 要 unique=True 且可空（MySQL 里 NULL 不参与唯一性判断）；
    #        role 用 String(10) + default="reader" 即可（不要用 SQLAlchemy 的 Enum 去映射
    #        MySQL ENUM，改起来麻烦）；password_hash 给 default=""。

    # TODO ②：补 relationship（用字符串写类名，避免前向引用问题）
    #   borrow_records: Mapped[list["BorrowRecord"]] = relationship(back_populates="user")
    #   reservations:   Mapped[list["Reservation"]] = relationship(back_populates="user")


class Book(Base):
    """图书表 books。

    需要的列（对照 schema.sql 的 books 表）：
        id         VARCHAR(16)   主键，'B001'
        isbn       VARCHAR(20)   可空 + 唯一
        title      VARCHAR(200)  非空 + 索引
        author     VARCHAR(100)  非空默认 ''
        publisher  VARCHAR(100)  非空默认 ''
        category   VARCHAR(50)   非空默认 '' + 索引
        price      DECIMAL(10,2) 非空默认 0
        stock      INT           非空默认 0（总库存，管理员设定）
        available  INT           非空默认 0（可借数，★ 只能由 crud.sync_book() 重算）
        cover_url  VARCHAR(255)  非空默认 ''
        is_deleted TINYINT(1)    非空默认 0
        created_at DATETIME      server_default=CURRENT_TIMESTAMP
        updated_at DATETIME      server_default=CURRENT_TIMESTAMP + onupdate

    ⚠️ schema.sql 里还有一个生成列 isbn_active，它是给数据库做唯一约束用的，
       ORM 不需要映射它（映射了也没法写，生成列不允许 INSERT）。

    关系：
        borrow_records / reservations
    """

    __tablename__ = "books"

    # 示例列（已给出）：主键
    id: Mapped[str] = mapped_column(String(16), primary_key=True, comment="图书编号 B001")

    # TODO ③：补 Book 剩下的列
    #   易错点：
    #     * isbn 必须是 `Mapped[str | None]`，否则插入 NULL 会报错
    #     * price 用 Numeric(10, 2)，Python 侧类型是 Decimal
    #     * is_deleted 用 `Mapped[bool]` + default=False（TINYINT(1) 由 SQLAlchemy 处理）
    #     * updated_at 要 `onupdate=func.current_timestamp()`，这样 UPDATE 时自动刷新

    # TODO ④：补 relationship
    #   borrow_records：一本书有多条借阅记录
    #   reservations：  一本书有多条预约


class BorrowRecord(Base):
    """借阅记录表 borrow_records（★ 库存的事实来源）。

    需要的列（对照 schema.sql 的 borrow_records 表）：
        id          BIGINT 自增主键
        user_id     VARCHAR(16) 外键 → users.id
        book_id     VARCHAR(16) 外键 → books.id
        borrow_date DATE 非空
        due_date    DATE 非空
        return_date DATE 可空 —— ★ NULL 表示「仍在借」，借阅状态由它推导
        renew_count TINYINT 非空默认 0
        created_at  DATETIME 默认 CURRENT_TIMESTAMP

    关系：
        user / book（两边都写 back_populates）

    ★★★ 记住：不要把「借阅中 / 已逾期 / 已归还」存成一个字段。
        状态必须由 return_date / due_date 和今天**推导**，存两份真相必然对不上。
    """

    __tablename__ = "borrow_records"

    # 示例列（已给出）：自增主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # TODO ⑤：补 BorrowRecord 剩下的列
    #   外键写法：book_id: Mapped[str] = mapped_column(ForeignKey("books.id"))

    # TODO ⑥：补 user / book 两个 relationship（都要 back_populates）

    # TODO ⑦：实现 status —— 借阅状态的唯一推导入口
    #   规则（顺序不能反）：
    #     return_date 不为 None        → "returned"（已归还）
    #     due_date < date.today()      → "overdue" （已逾期）
    #     否则                          → "borrowing"（借阅中）
    #   注意：它是一个 @property，不是数据库列；schemas.BorrowOut 会读它。
    @property
    def status(self) -> str:
        raise NotImplementedError("TODO: BorrowRecord.status —— 由日期推导借阅状态（见上面 ⑦）")


class Reservation(Base):
    """预约表 reservations。

    需要的列（对照 schema.sql 的 reservations 表）：
        id           BIGINT 自增主键
        user_id      VARCHAR(16) 外键 → users.id
        book_id      VARCHAR(16) 外键 → books.id
        status       ENUM('pending','ready','fulfilled','expired','cancelled') 默认 'pending'
        reserve_date DATE 非空
        expire_date  DATE 非空
        created_at   DATETIME 默认 CURRENT_TIMESTAMP

    ★ 只有 status = 'ready'（已到书待取）才占库存：
        available = stock - 未归还借阅数 - ready 预约占位数

    关系：
        user / book
    """

    __tablename__ = "reservations"

    # 示例列（已给出）：自增主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # TODO ⑧：补 Reservation 剩下的列 + user / book 两个 relationship
    #   提示：status 用 String(16) + default="pending"，在代码里用字符串比较（"ready" 等）
