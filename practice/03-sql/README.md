# 阶段 3 练习 · 数据库与 SQL

对应文档：[`docs/03-数据库与SQL.md`](../../docs/03-数据库与SQL.md)

## 练习顺序（别乱跳）

| # | 做什么 | 文件 | 预计 | 完成标志 |
|:--:|---|---|:--:|---|
| 1 | 建库建表，读懂每个约束 | `schema.sql` | 2 h | `SHOW TABLES;` 看到 4 张表；亲手触发一次 `ERROR 1451` |
| 2 | 做 20 道 SQL 练习题（第 1~17 题） | `queries.sql` | 8 h | 每题都能说出「为什么这么写、走哪条索引」 |
| 3 | 事务 / 隔离级别 / 死锁实验（第 18~19 题） | `queries.sql` | 5 h | 能复现一次 `ERROR 1213`，并读懂死锁日志 |
| 4 | 复现超借 → 修好它（第 20 题） | `concurrency_test.py` | 5 h | 修复前 ≥2 个 `201`，修复后只有 1 个 `201` |

## 1. 建库建表

```bash
mysql -u root -p < schema.sql          # 可重复执行，会先 DROP TABLE 再重建
mysql -u root -p library -e "SHOW TABLES;"
```

`schema.sql` 是**基础设施，不是练习**，直接整份执行。它包含：

- 4 张表 `users` / `books` / `borrow_records` / `reservations`，全部 InnoDB + utf8mb4
- 主键、外键、软删除 `is_deleted`、`created_at`、中文表/列注释
- 软删除 + 唯一索引冲突的**推荐解法**：生成列 `isbn_active`
- 一批演示数据，够 20 道练习题用

> ⚠️ `schema.sql` 里的用户 `password_hash` 是空的，登录会失败。阶段 5 请跑
> `practice/04-library-api/seed.py` 生成带真实 bcrypt 哈希的用户。

## 2. 做 SQL 练习题

```bash
mysql -u root -p library < queries.sql          # 一次跑完全部（含你的答案）
mysql -u root -p library                        # 交互式，逐题做更推荐
```

`queries.sql` 里每题都有题目描述 + `-- TODO:` 答案区，由易到难分 6 组：
基础 SELECT → WHERE/ORDER BY → GROUP BY → JOIN → 子查询 → 事务与锁。
最后 3 题固定是：**行锁 `SELECT ... FOR UPDATE`**、**隔离级别实验**、**库存守恒校验**。

## 3. 跑并发测试（超借复现）

**前提：`concurrency_test.py` 需要阶段 4 的借书接口做完才能跑**
（`POST /api/borrows/borrow`，见 `practice/04-library-api/routers/borrows.py`）。
阶段 3 只做 SQL 时，先把第 18~20 题在 MySQL 命令行里做完。

```bash
pip install -r ../requirements.txt
# ① 打开 concurrency_test.py 顶部的【配置区】，改 MYSQL_CONFIG["password"]
# ② 另开一个窗口把后端跑起来：
cd ../04-library-api && uvicorn main:app --reload
# ③ 回到本目录执行：
python concurrency_test.py                     # 默认 5 并发
python concurrency_test.py --concurrency 10
python concurrency_test.py --token eyJhbGci... # 阶段 5 开了鉴权后要带 Token
```

脚本会先用 `pymysql` **直连数据库**把 `B001` 重置成 `stock=1 / available=1` 并清掉历史记录
（不依赖任何调试接口），再并发借书，最后打印状态码、成功次数、判定和库存守恒 `diff`。

### 修复前预期输出（bug 复现成功）

```
读者 R001 -> 201  {"id":1,...}
读者 R002 -> 201  {"id":2,...}
读者 R003 -> 201  {"id":3,...}
读者 R004 -> 201  {"id":4,...}
读者 R005 -> 400  库存不足
成功借出次数（201） = 4
🐛 判定：超借！1 本书被借走了 4 次。
（并发数不同可能是 2~4 个 201，只要 > 1 就是 bug）
```

### 修复后预期输出

```
读者 R001 -> 201
读者 R002 -> 400
读者 R003 -> 400
读者 R004 -> 400
读者 R005 -> 400
成功借出次数（201） = 1
✅ 判定：正确！1 本书只被借出 1 次，其余都被拦住了。
守恒校验 diff = 0
```

修复要**同时**做两件事，缺一不可：

1. `routers/borrows.py` 的借书事务里，**第一句**就是
   `select(...).with_for_update()`；
2. `database.py` 的 `READ COMMITTED` 事件监听器生效（脚手架已给完整版）。

> 一句话：**行锁解决「同时进来」，隔离级别解决「读到的数据新不新」。**
> `REPEATABLE READ` 的快照读会绕过行锁，光加锁等于给门装了锁、却从窗户进出。

## 4. 收尾校验

```sql
-- 并发测试后立刻跑，结果必须是 0
SELECT (SELECT IFNULL(SUM(stock - available), 0) FROM books WHERE is_deleted = 0)
     - (SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL)
     - (SELECT COUNT(*) FROM reservations  WHERE status = 'ready') AS diff;
```
