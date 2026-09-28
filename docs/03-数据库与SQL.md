# 阶段 3 · 数据库与 SQL ★核心

> **一句话定位：** 这一阶段决定你是「会调 API 的人」还是「懂系统的人」—— 全流程 470 小时里，只有这里的知识是**别人抄不走**的。

---

## ✅ 学完能做什么

| 能力 | 具体表现 | 用在哪 |
|---|---|---|
| 独立设计表结构 | 看着需求写出 4 张表 + 主外键 + 索引，不用抄别人 | 项目第一天 |
| 手写复杂 SQL | `JOIN` / `GROUP BY` / 子查询 / 聚合，不用 ORM 也能查数 | 排查线上数据问题 |
| 讲清事务 ACID | 用「转账」例子说清四个特性各在保护什么 | 面试必问 |
| 讲清 4 个隔离级别 | 各防哪种异常、MySQL 默认哪个、为什么 | 面试加分 |
| 讲清 MVCC | 快照何时建立、为什么它让行锁「看起来失效」 | **面试能讲 10 分钟** |
| 用行锁解决并发 | `FOR UPDATE` + `READ COMMITTED` 修好超借 | 里程碑 ⑦ |
| 排查死锁 | 看懂 `SHOW ENGINE INNODB STATUS` 的死锁日志 | 线上救火 |
| 做软删除 | 说清 `DELETE` 为什么炸、唯一索引怎么处理 | 里程碑 ④ |

---

## ⏱️ 工时拆解（合计 80 h = 资源 60 h + 练习 20 h）

| # | 模块 | 主资源 | 资源 h | 练习 h | 小计 |
|:--:|---|---|:--:|:--:|:--:|
| A | SQL 基础语法 | SQLBolt + 廖雪峰 SQL | 22 | 5 | 27 |
| B | 事务与 ACID | 小林coding · 事务篇 | 8 | 3 | 11 |
| C | 隔离级别与 MVCC ★ | MySQL 官方手册 + 小林coding | 8 | 4 | 12 |
| D | 锁与死锁 ★ | 小林coding · 锁篇 | 7 | 3 | 10 |
| E | 索引原理（⚪选学，可砍） | Use The Index, Luke | 7 | 0 | 7 |
| F | 在线刷题 | SQLZoo | 8 | 0 | 8 |
| G | **超借复现与修复** ★★ | 动手 | 0 | 5 | 5 |
| | **合计** | | **60** | **20** | **80** |

> ⚠️ 砍掉 E 只省 7 小时，但你会失去「为什么这条 SQL 慢 100 倍」的解释能力。**建议别砍，放最后学。**

---

## 📚 资源清单

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| SQLBolt 互动教程 | 互动 | 英 | 10 h | 🔴必学 | <https://sqlbolt.com/> |
| 廖雪峰 SQL 教程 | 图文 | 中 | 12 h | 🔴必学 | <https://liaoxuefeng.com/books/sql/index.html> |
| SQLZoo 在线练习 | 互动 | 英 | 8 h | 🟡推荐 | <https://sqlzoo.net/> |
| 小林coding · 图解 MySQL（事务篇 + 锁篇） | 图文 | 中 | 15 h | 🔴必学 | <https://xiaolincoding.com/mysql/> |
| MySQL 官方手册 · 事务隔离级别 | 文档 | 英 | 8 h | 🟡推荐 | <https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html> |
| Use The Index, Luke（索引原理） | 图文 | 英 | 7 h | ⚪选学 | <https://use-the-index-luke.com/> |
| 动手：建库 + 复现超借 + 修复 | 动手 | — | 20 h | 🔴必学 | 本文「动手练习」 |

**推荐顺序（别乱跳）：** SQLBolt → 廖雪峰（建表 / JOIN / GROUP BY）→ SQLZoo 刷题 → 小林coding 事务篇（ACID / MVCC）→ MySQL 手册（隔离级别细节）→ 小林coding 锁篇（行锁 / 间隙锁 / 死锁）→ **动手复现超借 → 修好它** → 索引原理（选学）→ 进入阶段 4。

---

## 🧠 必须掌握的知识点

### A. 基础语法（SQLBolt + 廖雪峰）

- [ ] `CREATE TABLE` 字段类型：`VARCHAR` / `INT` / `BIGINT` / `DECIMAL` / `DATE` / `DATETIME` / `TINYINT` / `ENUM`
- [ ] 约束：`NOT NULL` / `DEFAULT` / `AUTO_INCREMENT` / `COMMENT` / `ENGINE=InnoDB` / `CHECK`
- [ ] **主键**：唯一 + 非空 + 聚簇索引；能说清为什么 `books.id` 用 `VARCHAR(16)` 业务编号而不是自增
- [ ] **外键** `FOREIGN KEY`：保护引用完整性（删书报 `1451`）；能说清为什么有人主张不用外键
- [ ] **索引** `KEY` / `UNIQUE KEY`：唯一索引 ≠ 主键，一个表只能有一个主键
- [ ] 查询：`SELECT` / `WHERE` / `ORDER BY` / `LIMIT` / `OFFSET` / `DISTINCT` / `BETWEEN` / `LIKE` / `IN`
- [ ] 写操作 `INSERT` / `UPDATE` / `DELETE`，以及 `UPDATE` 忘写 `WHERE` 的后果
- [ ] 聚合 `COUNT` / `SUM` / `AVG` / `MAX` / `MIN`；`COUNT(*)` 与 `COUNT(列)` 的区别
- [ ] `GROUP BY` + `HAVING`：**`WHERE` 过滤行、`HAVING` 过滤组**，区别必须能说清
- [ ] 多表 `INNER JOIN` / `LEFT JOIN`，以及 `ON` 与 `WHERE` 在左连接里的位置差异；子查询与 `EXISTS`
- [ ] 日期函数 `CURDATE()` / `NOW()` / `DATE_ADD()` / `DATEDIFF()`

### B. 事务与 ACID

- [ ] `BEGIN`（`START TRANSACTION`）/ `COMMIT` / `ROLLBACK`；`autocommit` 为什么让你平时不用手动提交
- [ ] **A 原子性** —— 要么全成要么全滚，靠 **undo log**
- [ ] **C 一致性** —— 约束不被破坏，靠 A + I + D 共同保证，**不是单独一个机制**
- [ ] **I 隔离性** —— 并发事务互不干扰，靠 **锁 + MVCC**
- [ ] **D 持久性** —— 提交了就不丢，靠 **redo log**
- [ ] 用「转账」把四条各讲一遍（练习 2 要做）

### C. 隔离级别（★ 面试重灾区）

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 一句话说明 |
|---|:--:|:--:|:--:|---|
| `READ UNCOMMITTED` | ❌ 会发生 | ❌ 会发生 | ❌ 会发生 | 能读到别人**没提交**的数据，基本不能用 |
| `READ COMMITTED` | ✅ 防住 | ❌ 会发生 | ❌ 会发生 | 每条语句读**最新已提交**数据（Oracle / PG 默认） |
| `REPEATABLE READ` | ✅ 防住 | ✅ 防住 | ✅ 基本防住 | 事务内重复读结果一致；**MySQL 默认** |
| `SERIALIZABLE` | ✅ 防住 | ✅ 防住 | ✅ 防住 | 完全串行，性能最差，几乎不用 |

| 异常 | 现象 |
|---|---|
| **脏读** | A 读到 B **还没提交**的修改，B 随后回滚，A 拿的是脏数据 |
| **不可重复读** | A 内两次读同一行结果不同（B 在中间 `UPDATE` 并提交） |
| **幻读** | A 内两次范围查询行数不同（B 在中间 `INSERT` / `DELETE` 并提交） |

- [ ] 用 `SELECT @@transaction_isolation;` 亲自验一次默认值是 `REPEATABLE READ`
- [ ] 会话级切换 `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;`；全局 `SET GLOBAL ...` **只对新连接生效**
- [ ] 能说清 `REPEATABLE READ` 的幻读为什么算「基本防住」：靠**间隙锁 Next-Key Lock**，不是靠快照

### D. MVCC（多版本并发控制）★

```mermaid
flowchart LR
    T["BEGIN"] --> R1["第 1 次普通 SELECT<br/>👉 此刻建立 Read View，快照定死"]
    R1 --> R2["第 2 次普通 SELECT<br/>仍看这个快照"]
    R2 --> L["SELECT ... FOR UPDATE<br/>👉 当前读，看最新数据"]
    L --> R3["第 3 次普通 SELECT<br/>❗还是老快照"]
    R3 --> C["COMMIT"]

    style R1 fill:#fff3cd,color:#000
    style L fill:#a8dadc,color:#000
    style R3 fill:#f8d7da,color:#000
```

- [ ] **快照建立在「事务内第一次非锁定读（普通 SELECT）」的时刻**，不是 `BEGIN` 的时刻
- [ ] **快照读**：普通 `SELECT`，走 MVCC，不加任何锁
- [ ] **当前读**：`FOR UPDATE` / `FOR SHARE` / `UPDATE` / `DELETE`，读最新已提交版本并加锁
- [ ] undo log 版本链 + `Read View` 可见性判断（比 `trx_id` 大小）
- [ ] **关键结论：快照读会绕过行锁。** 拿到了行锁，后面的普通 `COUNT(*)` 依然读旧快照 —— 超借 bug 的根
- [ ] `READ COMMITTED` 下**每条语句**重新建 Read View，所以锁内重算能读到最新数据

### E. 锁

- [ ] 共享锁 S 锁（`FOR SHARE`）与排他锁 X 锁（`FOR UPDATE`）
- [ ] 行锁 vs 表锁：InnoDB 默认行锁，但**锁的是索引**，没走索引会退化成锁全表
- [ ] `SELECT ... FOR UPDATE`：谁阻塞谁、锁在 `COMMIT` / `ROLLBACK` 时释放
- [ ] 间隙锁 Gap Lock 与 Next-Key Lock：解决幻读，**也是死锁的主要来源**
- [ ] 死锁四个必要条件；InnoDB 用等待图检测回路，主动回滚**代价小**的那个事务
- [ ] 排查：`SHOW ENGINE INNODB STATUS\G` → `LATEST DETECTED DEADLOCK`；`SHOW PROCESSLIST;` 看在等什么
- [ ] `innodb_lock_wait_timeout` 默认 50 秒；`ERROR 1213` = 死锁，`ERROR 1205` = 锁等待超时
- [ ] **全局统一加锁顺序**（都按 `id` 升序）能规避大部分死锁

### F. 索引原理（⚪选学，但强烈建议）

- [ ] B+ 树为什么适合索引（矮胖、叶子节点成链表、范围查询友好）；聚簇索引 vs 二级索引、**回表**
- [ ] 最左前缀原则；索引失效场景：列上做函数运算、隐式类型转换、`LIKE '%x'`、`OR`
- [ ] `EXPLAIN` 看懂 `type`（`const` > `ref` > `range` > `index` > `ALL`）、`key`、`rows`、`Extra`；索引不是越多越好

### G. 软删除（本项目硬性约定）

- [ ] 为什么用 `is_deleted = 1` 不用 `DELETE`：① **外键约束**（有借阅历史的书删不掉）② **历史记录保留**（否则借阅记录成孤儿）③ **可恢复** ④ **唯一字段可复用**
- [ ] 代价：所有查询都要带 `WHERE is_deleted = 0`，漏一处就是 bug —— 别靠人记，封装成默认过滤
- [ ] **软删除 + 唯一索引冲突**：删掉的书仍占着 ISBN。解法：删除时把 `isbn` 置 `NULL`（唯一索引里 `NULL` 可重复）／改写成 `CONCAT(isbn,'#del#',id)`／**用生成列（推荐）**：

```sql
isbn_active VARCHAR(20) GENERATED ALWAYS AS (IF(is_deleted = 0, isbn, NULL)) STORED,
UNIQUE KEY uk_books_isbn_active (isbn_active)
```

**核心公式（背下来）：** `available = stock − COUNT(未归还借阅记录) − COUNT(status='ready' 的预约占位)`

---

## 🗺️ 数据模型

```mermaid
erDiagram
    USERS ||--o{ BORROW_RECORDS : "借阅"
    BOOKS ||--o{ BORROW_RECORDS : "被借阅"
    USERS ||--o{ RESERVATIONS : "预约"
    BOOKS ||--o{ RESERVATIONS : "被预约"

    USERS {
        varchar id PK "编号 R001"
        varchar name "姓名"
        varchar role "admin 或 reader"
        varchar password_hash "bcrypt 哈希"
        tinyint is_deleted "软删除"
    }
    BOOKS {
        varchar id PK "编号 B001"
        varchar isbn "ISBN"
        varchar title "书名"
        int stock "总库存"
        int available "可借数"
        tinyint is_deleted "软删除"
    }
    BORROW_RECORDS {
        bigint id PK "自增"
        varchar user_id FK "读者"
        varchar book_id FK "图书"
        date due_date "应还日"
        date return_date "归还日 NULL 表示在借"
    }
    RESERVATIONS {
        bigint id PK "自增"
        varchar user_id FK "读者"
        varchar book_id FK "图书"
        varchar status "pending ready fulfilled expired cancelled"
        date expire_date "失效日"
    }
```

> 💡 **借阅状态不落库**，由 `return_date` / `due_date` 和今天推导。存两份真相必然对不上。

---

## 🛠️ 动手练习

### 练习 1：写出完整的 `schema.sql`（5 h）

存成 `schema.sql` 跑一遍。**不要复制粘贴就完事**，逐行看懂每个约束为什么这么写。

```sql
-- schema.sql · 图书管理系统建库脚本（MySQL 8.4）
DROP DATABASE IF EXISTS library;
CREATE DATABASE library DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE library;

CREATE TABLE users (
  id            VARCHAR(16)  NOT NULL            COMMENT '编号 A001 / R001',
  name          VARCHAR(50)  NOT NULL            COMMENT '姓名',
  phone         VARCHAR(20)      NULL            COMMENT '手机号',
  role          ENUM('admin','reader') NOT NULL DEFAULT 'reader',
  password_hash VARCHAR(100) NOT NULL DEFAULT '' COMMENT 'bcrypt 哈希，绝不存明文',
  is_deleted    TINYINT(1)   NOT NULL DEFAULT 0,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_users_phone (phone),
  KEY idx_users_role (role, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE books (
  id         VARCHAR(16)   NOT NULL              COMMENT '图书编号 B001',
  isbn       VARCHAR(20)       NULL              COMMENT 'ISBN',
  title      VARCHAR(200)  NOT NULL              COMMENT '书名',
  author     VARCHAR(100)  NOT NULL DEFAULT ''   COMMENT '作者',
  publisher  VARCHAR(100)  NOT NULL DEFAULT ''   COMMENT '出版社',
  category   VARCHAR(50)   NOT NULL DEFAULT ''   COMMENT '分类',
  price      DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '定价',
  stock      INT           NOT NULL DEFAULT 0    COMMENT '总库存',
  available  INT           NOT NULL DEFAULT 0    COMMENT '可借数，由 sync_book 重算',
  cover_url  VARCHAR(255)  NOT NULL DEFAULT ''   COMMENT '封面',
  is_deleted TINYINT(1)    NOT NULL DEFAULT 0,
  created_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_books_isbn (isbn),
  KEY idx_books_title (title),
  KEY idx_books_category (category, is_deleted),
  KEY idx_books_available (is_deleted, available),
  CONSTRAINT ck_books_stock CHECK (stock >= 0 AND available >= 0 AND available <= stock)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书表';

CREATE TABLE borrow_records (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id     VARCHAR(16) NOT NULL COMMENT '读者',
  book_id     VARCHAR(16) NOT NULL COMMENT '图书',
  borrow_date DATE        NOT NULL COMMENT '借出日',
  due_date    DATE        NOT NULL COMMENT '应还日',
  return_date DATE            NULL COMMENT '归还日；NULL=在借',
  renew_count TINYINT     NOT NULL DEFAULT 0 COMMENT '续借次数',
  created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_br_user (user_id, return_date),
  KEY idx_br_book (book_id, return_date),
  KEY idx_br_due  (return_date, due_date),
  CONSTRAINT fk_br_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_br_book FOREIGN KEY (book_id) REFERENCES books(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='借阅记录表';

CREATE TABLE reservations (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id      VARCHAR(16) NOT NULL,
  book_id      VARCHAR(16) NOT NULL,
  status       ENUM('pending','ready','fulfilled','expired','cancelled')
               NOT NULL DEFAULT 'pending' COMMENT 'pending=排队 ready=已到书待取',
  reserve_date DATE     NOT NULL COMMENT '预约日',
  expire_date  DATE     NOT NULL COMMENT '到期日；ready 后即取书截止日',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_res_book   (book_id, status),
  KEY idx_res_user   (user_id, status),
  KEY idx_res_expire (status, expire_date),
  CONSTRAINT fk_res_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_res_book FOREIGN KEY (book_id) REFERENCES books(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约表';

INSERT INTO users (id, name, role) VALUES
  ('A001', '管理员', 'admin'), ('R001', '张三', 'reader'), ('R002', '李四', 'reader');

INSERT INTO books (id, isbn, title, author, category, stock, available) VALUES
  ('B001', '9787115428028', 'Python 编程：从入门到实践', 'Eric Matthes', '编程', 1, 1),
  ('B002', '9787111544937', '深入理解计算机系统', 'Randal Bryant', '计算机', 3, 3);

-- 外键生效验证：有借阅记录时删书应该报错
INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date)
VALUES ('R001', 'B001', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY));
DELETE FROM books WHERE id = 'B001';   -- ❌ ERROR 1451，这就是必须软删除的理由
```

- [ ] `SHOW TABLES;` 能看到 4 张表；随手 `EXPLAIN` 一条查询确认 `key` 列命中索引
- [ ] 亲手触发一次 `ERROR 1451` 外键错误

### 练习 2：事务、隔离级别、死锁实验（7 h）

```sql
SELECT @@transaction_isolation;                             -- 默认 REPEATABLE READ
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;   -- 依次换成另外三个

-- 窗口 A
START TRANSACTION;
UPDATE books SET available = available - 1 WHERE id = 'B001';
SELECT available FROM books WHERE id = 'B001';   -- 0
-- 窗口 B（此时 A 未提交）
SELECT available FROM books WHERE id = 'B001';   -- 仍是 1，这就是隔离性
-- 回到窗口 A
ROLLBACK;                                        -- 这就是原子性：白改了
```

- [ ] 把 `ROLLBACK` 换成 `COMMIT`，窗口 B 再观察一次
- [ ] 用「张三给李四转 100 块」写两条 `UPDATE`，故意让第二条报错，验证第一条被回滚
- [ ] 按上面的表逐行复现四种级别下「B 能看到什么」，写下笔记：`REPEATABLE READ` 下 **B 读的是快照，不是锁**
- [ ] 用两个窗口按 `A 锁 B001 → B 锁 B002 → A 求 B002 → B 求 B001` 复现 `ERROR 1213` 死锁
- [ ] 立刻跑 `SHOW ENGINE INNODB STATUS\G`，从 `LATEST DETECTED DEADLOCK` 里指出：谁被回滚、各持有什么锁、在等什么锁
- [ ] 说出为什么「按 `id` 升序统一加锁顺序」能避免这个死锁；用 200 字写下 ACID 各自的实现机制

### 练习 3：超借 bug 复现与修复 ★★（5 h，全文档高潮）

**场景：** `B001` 的 `stock = 1`、`available = 1`，**5 个读者同时借**。
正确结果 **1 个 `201` + 4 个 `400`**；Bug 现象 **4 个 `201`** —— 1 本书被借走 4 次。

```mermaid
sequenceDiagram
    autonumber
    participant T1 as 事务1
    participant DB as MySQL
    participant T2 as 事务2

    T1->>DB: BEGIN
    T1->>DB: 普通 SELECT 图书（非锁定读）
    Note over T1,DB: 👉 Read View 此刻建立，看到 available=1
    T2->>DB: BEGIN
    T2->>DB: 普通 SELECT 图书（非锁定读）
    Note over T2,DB: 也看到 available=1
    T1->>DB: SELECT ... FOR UPDATE
    DB-->>T1: 拿到行锁
    T2->>DB: SELECT ... FOR UPDATE
    Note over T2,DB: ⏳ 阻塞，等 T1 提交
    T1->>DB: SELECT COUNT(*) 未归还记录 → 0
    T1->>DB: INSERT 借阅记录 + UPDATE available=0
    T1->>DB: COMMIT，释放行锁
    DB-->>T2: 拿到行锁
    T2->>DB: SELECT COUNT(*) 未归还记录
    Note over T2,DB: ❗ 仍读旧快照，COUNT 还是 0，判断库存充足
    T2->>DB: INSERT + COMMIT
    Note over T1,T2: 🐛 超借！两个事务都借成功了
```

**一句话原因：** MySQL 默认 `REPEATABLE READ`，事务内**第一次非锁定读**就把快照定死。行锁只能让请求**排队**，排队后重新 `COUNT` 在借数量读到的还是旧快照 —— 锁白加了。

**第 1 步：先看 bug 的核心三句**（完整可运行版见阶段 4 的借书接口）

```python
with Session(engine) as db, db.begin():
    # ① 非锁定读 —— Read View 在这一刻定死！
    book = db.execute(select(Book).where(Book.id == book_id)).scalar_one_or_none()

    # ② 重算在借数量 —— 走的是①的快照，看不到别人刚提交的记录
    borrowed = db.execute(
        select(func.count()).select_from(BorrowRecord).where(
            BorrowRecord.book_id == book_id, BorrowRecord.return_date.is_(None)
        )
    ).scalar_one()

    if borrowed >= book.stock:      # ③ BUG：borrowed 来自旧快照，永远判断为「够借」
        return "400 库存不足"
    db.add(BorrowRecord(user_id=user_id, book_id=book_id,
                        borrow_date=date.today(),
                        due_date=date.today() + timedelta(days=30)))
    return "201 借阅成功"
```

> ⚠️ 就算把 ① 改成 `with_for_update()`，只要**事务里存在任意一条先于它的普通 SELECT**（依赖注入里查用户、
> ORM 的 `refresh()`、参数校验触发的查询），快照依然提前定死。这就是修复必须**同时**依赖 `READ COMMITTED` 的原因。

**第 2 步：并发测试脚本（`concurrent.futures` + `requests`）**

```python
# concurrent_borrow_test.py —— 5 并发借同一本书
import concurrent.futures

import pymysql
import requests

BASE = "http://127.0.0.1:8000"
TOKEN = "把管理员登录后的 Token 粘这里"
BOOK_ID = "B001"
DB = dict(host="127.0.0.1", port=3306, user="root",
          password="你的MySQL密码", database="library", charset="utf8mb4")


def reset_book() -> None:
    """把测试用书重置成 stock=1 / available=1，并清掉它的历史借阅记录。

    直接连 MySQL 改，**不依赖后端提供任何调试接口**。
    """
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM borrow_records WHERE book_id = %s", (BOOK_ID,))
            cur.execute("UPDATE books SET stock = 1, available = 1 WHERE id = %s", (BOOK_ID,))
        conn.commit()
    finally:
        conn.close()


def borrow(i: int) -> tuple[int, str]:
    """第 i 个读者借书，返回 (状态码, 响应体摘要)。"""
    r = requests.post(
        f"{BASE}/api/borrows/borrow",
        json={"bookId": BOOK_ID, "readerId": f"R{i:03d}"},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=15,
    )
    return r.status_code, r.text[:80]


def main() -> None:
    reset_book()   # 每次跑之前重置，保证起点一致

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(borrow, range(1, 6)))

    for i, (code, body) in enumerate(results, start=1):
        print(f"读者 R{i:03d} -> {code}  {body}")

    ok = sum(1 for code, _ in results if code == 201)
    print(f"\n成功借出次数 = {ok}")
    print("🐛 超借了！1 本书被借走多次" if ok > 1 else "✅ 正确：只有 1 个人借到")


if __name__ == "__main__":
    main()
```

> 💡 不想写 `reset_book()` 也行：直接在 MySQL 命令行里跑下面两句，效果完全一样。
>
> ```sql
> DELETE FROM borrow_records WHERE book_id = 'B001';
> UPDATE books SET stock = 1, available = 1 WHERE id = 'B001';
> ```

**修复前**（并发数不同可能是 2~4 个 `201`，**只要 > 1 就是 bug**）：

```
读者 R001 -> 201  {"id":1,...}
读者 R002 -> 201  {"id":2,...}
读者 R003 -> 201  {"id":3,...}
读者 R004 -> 201  {"id":4,...}
读者 R005 -> 400  库存不足
成功借出次数 = 4
🐛 超借了！1 本书被借走多次
```

**第 3 步：修复 ① —— 加行锁**

```python
book = db.execute(
    select(Book).where(Book.id == book_id, Book.is_deleted == 0)
    .with_for_update()          # 生成 SQL: ... FOR UPDATE
).scalar_one_or_none()
```

**第 4 步：修复 ② —— 用 SQLAlchemy event 监听器把会话隔离级别改成 `READ COMMITTED`**

```python
# database.py
from sqlalchemy import create_engine, event

DATABASE_URL = "mysql+pymysql://root:password@127.0.0.1:3306/library?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,     # 防止 MySQL 8 小时空闲自动断连
    pool_recycle=3600,
)


@event.listens_for(engine, "connect")
def _set_read_committed(dbapi_connection, _connection_record):
    """每条新连接建立时都设成 READ COMMITTED。

    为什么必须这么做：REPEATABLE READ 下 Read View 在事务内第一次
    非锁定读时建立，之后即使拿到行锁，重算 COUNT 仍读旧快照。
    READ COMMITTED 让每条语句重新取快照，锁内就能读到最新已提交数据。
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()
```

> 💡 等价写法：`create_engine(DATABASE_URL, isolation_level="READ COMMITTED")`。
> 但**面试优先讲 event 监听器版**，因为它能顺带说清「什么时候、对哪条连接执行了什么」。

**第 5 步：修复后的完整借书逻辑**

```python
# fixed_borrow.py —— ① 行锁串行化 ② READ COMMITTED 保证锁内读到最新数据
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database import engine          # 已挂 READ COMMITTED 监听器
from models import Book, BorrowRecord, Reservation


def sync_book(db: Session, book_id: str) -> None:
    """统一重算 available —— 全项目唯一的库存计算入口。

    available = stock - 未归还借阅数 - ready 状态预约占位数
    绝对不要在别处写 available += 1 / -= 1。
    """
    book = db.get(Book, book_id)
    if book is None:
        return
    borrowed = db.execute(
        select(func.count()).select_from(BorrowRecord).where(
            BorrowRecord.book_id == book_id, BorrowRecord.return_date.is_(None)
        )
    ).scalar_one()
    reserved = db.execute(
        select(func.count()).select_from(Reservation).where(
            Reservation.book_id == book_id, Reservation.status == "ready"
        )
    ).scalar_one()
    book.available = max(book.stock - borrowed - reserved, 0)


def borrow_fixed(user_id: str, book_id: str, days: int = 30) -> dict:
    with Session(engine) as db:
        with db.begin():                       # 一个事务
            # ① 第一句就是锁定读：并发请求在这里排队
            book = db.execute(
                select(Book).where(Book.id == book_id, Book.is_deleted == 0)
                .with_for_update()
            ).scalar_one_or_none()
            if book is None:
                return {"code": 404, "msg": "图书不存在"}

            # ② 锁内重算：READ COMMITTED 保证读到别人刚提交的记录
            borrowed = db.execute(
                select(func.count()).select_from(BorrowRecord).where(
                    BorrowRecord.book_id == book_id,
                    BorrowRecord.return_date.is_(None),
                )
            ).scalar_one()

            # ③ 同一读者不能对同一本书有两条未归还记录
            dup = db.execute(
                select(func.count()).select_from(BorrowRecord).where(
                    BorrowRecord.user_id == user_id,
                    BorrowRecord.book_id == book_id,
                    BorrowRecord.return_date.is_(None),
                )
            ).scalar_one()
            if dup:
                return {"code": 400, "msg": "你已借阅此书且未归还"}

            # ④ 真正判断库存
            if book.stock - borrowed <= 0:
                return {"code": 400, "msg": "库存不足"}

            today = date.today()
            db.add(BorrowRecord(
                user_id=user_id, book_id=book_id,
                borrow_date=today, due_date=today + timedelta(days=days),
                return_date=None, renew_count=0,
            ))
            db.flush()                # 先把 INSERT 刷出去，sync_book 才数得到
            sync_book(db, book_id)
        # 出了 with 块即 COMMIT，行锁释放，下一个请求才被放行
    return {"code": 201, "msg": "借阅成功"}
```

**修复后重跑测试脚本：**

```
读者 R001 -> 201  {"id":1,...}
读者 R002 -> 400  库存不足
读者 R003 -> 400  库存不足
读者 R004 -> 400  库存不足
读者 R005 -> 400  库存不足
成功借出次数 = 1
✅ 正确：只有 1 个人借到
```

**第 6 步：为什么只做 ① 不做 ② 没用？（必须能口述）**

| 只做 ① 行锁 | 只做 ② `READ COMMITTED` | ① + ② 一起做 |
|---|---|---|
| 请求确实排队了，但排队后 `COUNT` 还是读事务开始时的旧快照 → **照样超借** | 每条语句读到最新数据，但**没有任何东西阻止两个事务同时读到「还能借」** → **照样超借**（经典丢失更新） | 锁负责**排队**，隔离级别负责**读得准**，缺一不可 |

一句话回答面试官：

> **行锁解决「同时进来」，隔离级别解决「读到的数据新不新」。`REPEATABLE READ` 的快照读会绕过行锁，所以光加锁等于给门装了锁、却从窗户进出。**

**第 7 步：收尾验证**

```sql
-- 并发测试后立刻跑，结果必须是 0
SELECT (SELECT SUM(stock - available) FROM books WHERE is_deleted = 0)
     - (SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL) AS diff;
```

- [ ] 修复前复现出 ≥2 个 `201`；修复后只有 1 个 `201`
- [ ] 上面这条校验 SQL 返回 `0`
- [ ] 能把第 6 步那张表讲给同学听，对方听懂了

> 🧠 **进阶思考：** 还有个更简单的方案 —— 不 `COUNT`，直接原子扣减：
> `UPDATE books SET available = available - 1 WHERE id = ? AND available > 0;` 判断影响行数是否为 1。
> 单条语句本身就是原子的。想一想：它为什么成立？什么场景下又不够用（提示：还要写借阅记录、还要防重复借）？

---

## ✅ 验收标准

- [ ] 能默写出 4 张表的 `CREATE TABLE`，含主键、外键、至少 3 个索引
- [ ] 能说清主键和外键分别解决什么问题
- [ ] 能说清为什么删书用 `is_deleted = 1` 而不是 `DELETE`，以及软删除对唯一索引的影响和解法
- [ ] 4 种隔离级别各防哪种异常、MySQL 默认哪个，能脱口而出；脏读 / 不可重复读 / 幻读各能举例
- [ ] 能说清 MVCC 快照在**事务内第一次非锁定读**时建立
- [ ] **能复现**超借（修复前 5 并发 ≥2 个 `201`），**能修复**（修复后只有 1 个 `201`，其余 4 个 `400`）
- [ ] 能说清为什么只加 `FOR UPDATE` 不改隔离级别没用
- [ ] `stock - available` 恒等于在借数，校验 SQL 返回 `0`
- [ ] 能独立复现一次死锁，并从 `SHOW ENGINE INNODB STATUS` 里指出成因
- [ ] 能对任意慢 SQL 用 `EXPLAIN` 判断有没有走索引
- [ ] 能口述 ACID 四条的实现机制（undo log / 约束 / 锁+MVCC / redo log）

---

## ⚠️ 常见坑

| # | 坑 | 后果 | 正确做法 |
|:--:|---|---|---|
| 1 | 只加行锁，不改隔离级别 | **并发借书照样超借**（实测 5 并发过 4 个） | ①`FOR UPDATE` + ②`READ COMMITTED` 一起上 |
| 2 | 先普通 `SELECT` 再 `FOR UPDATE` | 快照已定死，锁白加 | **锁定读放事务第一句** |
| 3 | 到处手写 `available += 1 / -= 1` | 散落的加减法一定算错 | 收敛到唯一的 `sync_book()` **重算** |
| 4 | 把借阅状态存进数据库 | 两份真相必然对不上（早该 overdue 却还是 borrowing） | 状态由日期**推导** |
| 5 | 硬删除 `DELETE` | 有借阅历史的书报 `1451` | 软删除 `is_deleted = 1` |
| 6 | 软删除后没处理唯一索引 | 删掉的 ISBN 永远占位，新书加不进来 | 生成列 / 删除时置 `NULL` |
| 7 | 查询忘了带 `WHERE is_deleted = 0` | 已删除数据出现在列表里 | 封装成默认过滤，别靠人记 |
| 8 | 两个事务按不同顺序锁多行 | 死锁 `1213` | 全局统一加锁顺序（按 `id` 升序） |
| 9 | 长事务：`BEGIN` 之后去调外部接口 | 行锁长时间不释放，把表拖死 | 事务里**只做数据库操作**，事务要短 |
| 10 | `LIKE '%关键词%'` 还指望走索引 | 全表扫描，数据一多就卡 | 前缀匹配 `LIKE '关键词%'` 或全文索引 |
| 11 | 在 `WHERE` 里对列做运算 `YEAR(created_at)=2025` | 索引失效 | 改写成范围 `created_at >= '2025-01-01' AND < '2026-01-01'` |
| 12 | 以为 `SET GLOBAL` 改隔离级别立刻生效 | 老连接不受影响，白改 | 只对新连接生效，或改配置后重启 |
| 13 | 用 `COUNT(*)` 判断能否借却不管预约占位 | 被预约的书被人借走 | 公式带上 `ready` 状态的预约数 |
| 14 | 并发测试跑在单线程测试客户端上 | 永远复现不出 bug，误以为没问题 | 必须真 MySQL + 真多线程 |
| 15 | 明文数据库密码写进代码提交 Git | 泄露 | 走 `.env` + `.gitignore` |

---

## 📌 这一阶段的三句话

1. **锁管排队，隔离级别管读得准。** 两者缺一，并发就是错的。
2. **状态要由数据推导，不要存两份真相。**
3. **凡是「并发下会不会算错」的问题，先问一句：我读的是快照还是最新数据？**

---

[← 返回首页](../README.md) · [资源总表](../resources.md) · [里程碑](../milestones.md)
