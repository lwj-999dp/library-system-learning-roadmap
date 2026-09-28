# -*- coding: utf-8 -*-
"""database.py · 引擎 / 会话 / 声明式基类 / 请求级 Session 依赖（★ 完整，不需要你改）

对应文档
--------
docs/03-数据库与SQL.md 「第 4 步：用 SQLAlchemy event 监听器把会话隔离级别改成 READ COMMITTED」
docs/04-FastAPI与SQLAlchemy.md 练习 1 的 app/database.py

这个文件要做什么
----------------
1. 建**连接池**（不要每次请求都新建连接）
2. **每条新连接**建立时，把会话隔离级别设成 `READ COMMITTED` ← 超借修复的 ② 号补丁
3. 提供 `SessionLocal` 与 `get_db()` 依赖：一个请求一个 Session，请求结束一定 close
4. 提供 2.0 风格的声明式基类 `Base`

★ 为什么必须把隔离级别改成 READ COMMITTED（面试要能讲 1 分钟）
-------------------------------------------------------------
MySQL 默认是 `REPEATABLE READ`。它的规则是：
**事务内第一次「非锁定读」（普通 SELECT）的那一刻建立 Read View，之后整个事务都用这个快照。**

于是超借 bug 是这样发生的：

    with db.begin():
        book = db.get(Book, "B001")            # ① 普通 SELECT → 快照在此定死，看到 available=1
        ...                                    # ② 后来拿到 FOR UPDATE 行锁，请求确实排队了
        borrowed = COUNT(... return_date IS NULL)   # ③ 但这里读的还是①的快照 → 还是 0！
        if book.stock - borrowed <= 0: 拒绝       # ④ 判断成「还能借」→ 超借

**快照读会绕过行锁。** 光加 `FOR UPDATE` 只让请求排队，排队后重算 COUNT 依然读旧快照。

`READ COMMITTED` 的规则是「每条语句重新建 Read View」，所以锁内重算能读到别人刚提交的记录：
锁负责**排队**，隔离级别负责**读得准**，两者缺一不可。

⚠️ 还有一个更隐蔽的坑：只要事务里存在**任意一条先于 FOR UPDATE 的普通 SELECT**
（依赖注入里查用户、`db.refresh()`、参数校验触发的查询），快照就会提前定死。
所以正确做法是 ①**锁定读放在事务第一句** + ②**连接级 READ COMMITTED** 一起上。

⚠️ `SET GLOBAL TRANSACTION ISOLATION LEVEL ...` 只对**之后新建的连接**生效，
   已经躺在连接池里的老连接不受影响 —— 这就是这里必须用【每条新连接】事件监听器的原因。

验收标准
--------
- [ ] `SQL_ECHO=true` 启动后，借书请求里能亲眼看到 `... FOR UPDATE` 这条 SQL
- [ ] MySQL 里 `SHOW PROCESSLIST;` 看到的连接，隔离级别是 READ COMMITTED
      （或在应用里执行 `SELECT @@transaction_isolation;` 确认是 READ-COMMITTED）
- [ ] 全部查询用 `select()` 2.0 风格，全项目搜不到 `db.query(`
- [ ] `get_db()` 用 `yield` + `finally: db.close()`，不会连接泄漏
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import settings

# -----------------------------------------------------------------------------
# 引擎 + 连接池
# -----------------------------------------------------------------------------
# pool_size / max_overflow：池里常驻 10 条连接，忙时最多再开 20 条
# pool_pre_ping：借出连接前先 ping 一下，防止 MySQL 8 小时空闲自动断连后拿到死连接
# pool_recycle：连接最长活 1 小时就回收重建，配合 MySQL 的 wait_timeout
# echo：打印真实 SQL，开发调 N+1 时必开，生产关掉
#
# 注意：create_engine 是**惰性**的，这一行不会真的去连数据库 —— 所以即使 .env 还没配好，
#       import database 也不会报错（main.py 因此总能启动，只会打警告）。
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.sql_echo,
    future=True,
)


@event.listens_for(engine, "connect")
def _set_read_committed(dbapi_connection, _connection_record) -> None:
    """每条新连接建立时都设成 READ COMMITTED —— 超借修复的第 ② 号补丁。

    `connect` 事件在「物理连接刚建好、还没交给应用」时触发，所以池里每一条连接
    都保证是 READ COMMITTED，不会漏。

    等价写法：`create_engine(url, isolation_level="READ COMMITTED")`。
    但面试优先讲 event 监听器版 —— 因为它能顺带说清「什么时候、对哪条连接、执行了什么 SQL」。
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()


# -----------------------------------------------------------------------------
# 会话工厂 + 声明式基类
# -----------------------------------------------------------------------------
# autoflush=False：不自动 flush，避免在你不希望的时候把 SQL 发出去（重算库存要靠手动 flush）
# expire_on_commit=False：commit 后对象仍可读，省掉一次 refresh 查询（FastAPI 返回响应时需要）
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 的声明式基类。models.py 里所有 ORM 模型都继承它。"""


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：一个请求一个 Session，请求结束一定关闭，连接归还池子。

    用法：`def endpoint(db: Session = Depends(get_db)): ...`

    ⚠️ 必须 `try / finally`。少了 finally，异常请求就把连接漏在池外，
       请求一多就是 `Too many connections`。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
