# -*- coding: utf-8 -*-
"""crud.py · 库存与事实表的纯数据操作（TODO ★★ 全项目最核心的一个函数在这里）

对应文档
--------
docs/04-FastAPI与SQLAlchemy.md 练习 2 的 app/crud.py
docs/03-数据库与SQL.md 练习 3「超借 bug 复现与修复」（原理都在这份文档里）

这个文件放什么
--------------
只放**跨表 / 库存计算**这类纯数据函数，全部是「给 Session，还你结果」：
    count_borrowed()    这本书现在有多少条未归还记录
    count_reserved()    这本书有多少个 ready 预约在占库存
    sync_book()   ★★★  重算 available —— 全项目【唯一】能改 available 的地方
    run_maintenance()   惰性维护：过期预约失效 + 逾期统计（阶段 4 练习 3）

图书 CRUD 的查询语句直接写在 routers/books.py 里（路由那一层就是「解析参数 → 查询 → 返回」），
借书 / 还书的事务写在 routers/borrows.py 里（★ 行锁 `with_for_update()` 在那里）。
这样每个函数只有一处职责，不会同一段逻辑抄两遍。

两条铁律
--------
1. **crud 层不抛 HTTPException。** 这里只懂数据库，不懂 HTTP。
   需要报错就返回 `(结果, 错误信息)`，由路由翻译成 400 / 404 / 409。
2. **绝不写 `available += 1` / `available -= 1`。**
   加减法散落在借书 / 还书 / 预约 / 取消预约 / 改库存五个地方，
   任何一处漏掉或重复执行，库存就永久错位且查不出原因。
   唯一正确的做法是**从事实表重算**（sync_book），无论调多少次结果都一样。

验收标准
--------
- [ ] 全项目搜不到 `available +=` 或 `available -=`，只有 sync_book 里的一句赋值
- [ ] 借出一本 → available 减 1；归还一本 → 加 1
- [ ] `stock - available` 恒等于「未归还借阅数 + ready 预约数」，守恒校验 SQL 返回 0
- [ ] 反复请求读接口 10 次，available 不会一直涨（run_maintenance 幂等）
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from models import Book, BorrowRecord, Reservation

# 默认借期（天）
DEFAULT_LOAN_DAYS: int = 30


def count_borrowed(db: Session, book_id: str) -> int:
    """这本书当前有多少条**未归还**记录（return_date IS NULL）。

    ★ 已给出的示例函数：count_reserved() 请照这个模子写。
    注意几个细节：
      * `select(func.count()).select_from(模型)` 是 2.0 的计数写法（不是 db.query(...).count()）
      * 条件用 `.is_(None)` 而不是 `== None`（后者在 SQLAlchemy 里会被 lint 警告，也可能出错）
      * `scalar_one()` 取单个标量值
    """
    return db.execute(
        select(func.count())
        .select_from(BorrowRecord)
        .where(
            BorrowRecord.book_id == book_id,
            BorrowRecord.return_date.is_(None),
        )
    ).scalar_one()


def count_reserved(db: Session, book_id: str) -> int:
    """这本书有多少个 `status = 'ready'` 的预约在**占库存**（已到书但还没被取走）。

    TODO ①：照着 count_borrowed() 写，把表换成 Reservation、条件换成
             `Reservation.status == "ready"`。

    为什么只有 ready 占库存：
      * pending   = 还在排队，书都没到，不占
      * ready     = 书已经给它留出来了，**必须占**（否则被预约的书会被别人借走）
      * fulfilled / expired / cancelled = 已经结束，不占
    忘了减 ready 预约数，就是 docs/03 常见坑 #13。
    """
    raise NotImplementedError("TODO: crud.count_reserved() —— 统计 ready 预约占位数（照 count_borrowed 写）")


def sync_book(db: Session, book_id: str) -> int:
    """★★★ 全项目唯一的库存计算入口：从事实表重算 `available`，返回新值。

    ★ 公式（背下来）：

        available = stock - 未归还借阅数 - 已到书待取的预约占位数

    TODO ②：把上面的公式实现出来。步骤：
        1. `book = db.get(Book, book_id)`；查不到就 `return 0`（别抛异常）
        2. `borrowed = count_borrowed(db, book_id)`
        3. `reserved = count_reserved(db, book_id)`
        4. `book.available = max(book.stock - borrowed - reserved, 0)`  ← 兜底不允许负数
        5. `return book.available`

    为什么是「重算」而不是「+1 / -1」：
        重算的输入是**事实表**（借阅记录 / 预约记录），无论调用多少次、在哪个流程调用、
        是不是重复执行了，结果都一致（幂等）。加减法做不到这一点。

    ⚠️ 调用它的前提：本次事务里新加的借阅记录必须已经 `db.flush()` 过，
       否则 COUNT 数不到这一条，重算结果会偏大（docs/04 常见坑 #11）。
    ⚠️ 调用方负责 commit —— 这里只改内存里的 ORM 对象 + 发出 UPDATE，不提交事务。
    """
    raise NotImplementedError(
        "TODO: crud.sync_book() —— available = stock - 未归还借阅数 - ready 预约数（见函数上方公式）"
    )


def run_maintenance(db: Session) -> None:
    """惰性维护（阶段 4 练习 3，可选加分项）：把「定时任务」塞进读接口里顺带做完。

    为什么不引入 Celery / APScheduler：这个项目没有常驻调度器，多一套东西就多一套运维。
    而「预约过期」这类数据只在**有人来看**的时候才需要正确，挂在读接口最前面就够了。

    TODO ③（进阶）：实现三条，缺一不可：
        ① **能提前返回**：先查有没有「status in ('pending','ready') 且 expire_date < 今天」的预约，
           一条都没有就立刻 return —— 绝大多数请求的开销只是一条索引查询
        ② **批量**：用一条 `update(Reservation).where(...).values(status="expired")` 搞定，
           绝不要 for 循环逐行 UPDATE（1000 条过期预约 = 1000 条 SQL）
        ③ **重算库存**：占位释放了，必须对受影响的每个 book_id 调一次 sync_book()，
           否则 available 会一直少算
        ④ 顺手统计逾期未还（`due_date < 今天 AND return_date IS NULL`）打条日志即可
           —— 借阅状态不落库，所以没有「改成逾期」这个动作
        最后 `db.commit()` 把维护结果落库；整个函数必须**幂等**（跑 10 次 available 也不变）。

    挂载位置：只挂在**读接口**（GET）最前面，写接口不要再调一次（docs/04 常见坑 #15）。
    """
    raise NotImplementedError("TODO: crud.run_maintenance() —— 过期预约失效 + 重算库存（进阶，见函数内注释）")


def today() -> date:
    """统一取「今天」，方便测试时替换（不要在各处直接写 date.today()）。"""
    return date.today()
