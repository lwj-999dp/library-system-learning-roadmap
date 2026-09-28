# 阶段 4 + 5 练习 · 图书管理系统后端骨架（FastAPI + SQLAlchemy + MySQL）

对应文档：[`docs/04-FastAPI与SQLAlchemy.md`](../../docs/04-FastAPI与SQLAlchemy.md)、[`docs/05-鉴权与安全.md`](../../docs/05-鉴权与安全.md)

这是一个**自带答案检查点的填空题骨架**：能启动、能看 `/docs`，但每个关键学习点都留了
`raise NotImplementedError("TODO: ...")`，调用时会返回 **501**（`main.py` 里注册了异常处理器），
而不是一坨 500 堆栈。填掉一个 TODO，对应接口立刻可用。

## 文件分工（每个文件只干一件事）

| 文件 | 状态 | 职责 |
|---|---|---|
| `config.py` | ✅ 完整 | 读 `.env` + 环境变量覆盖，导出 `settings` |
| `database.py` | ✅ 完整 | 引擎/连接池、Session、`Base`、`get_db()`、**READ COMMITTED 事件监听器** |
| `main.py` | ✅ 完整 | 应用装配、lifespan、CORS 白名单、中间件、501 处理器 |
| `seed.py` | ✅ 完整 | 灌演示数据（依赖 `security.hash_password`） |
| `models.py` | 📝 TODO | 4 张表的 ORM 字段 + relationship + `BorrowRecord.status` 推导 |
| `schemas.py` | 📝 TODO | Pydantic 出入参（请求/响应**必须**分开） |
| `crud.py` | 📝 TODO ★ | `count_reserved()`、**`sync_book()`（全项目最核心）**、`run_maintenance()` |
| `security.py` | 📝 TODO | bcrypt、JWT、`get_current_user` / `require_admin` / `require_reader` |
| `routers/auth.py` | 📝 TODO | 注册 / 登录 / me |
| `routers/books.py` | 📝 TODO | 图书 CRUD（分页+搜索+白名单排序+软删除） |
| `routers/borrows.py` | 📝 TODO ★ | **借书（`with_for_update()` 行锁）** / 还书 |

> 设计说明：图书 CRUD 的查询直接写在 `routers/books.py`，跨表/库存计算放在 `crud.py`，
> 借还事务放在 `routers/borrows.py`。同一段逻辑只有一处，不抄两遍。

## 启动步骤

```bash
# 1) 建虚拟环境 + 装依赖（依赖清单在上一层目录）
python -m venv .venv
.venv\Scripts\activate                  # Windows；macOS/Linux 用 source .venv/bin/activate
pip install -r ../requirements.txt

# 2) 先建库建表（权威脚本是阶段 3 的 schema.sql）
mysql -u root -p < ../03-sql/schema.sql

# 3) 配置环境变量
copy .env.example .env                  # macOS/Linux: cp .env.example .env
#    然后编辑 .env：把 DATABASE_URL 里的 your_password_here 换成真实密码
#    生成 JWT 密钥：python -c "import secrets; print(secrets.token_urlsafe(48))"

# 4) 启动（.env 没配好也起得来，只会打警告）
uvicorn main:app --reload
#    打开 http://127.0.0.1:8000/docs
```

## 建议的填空顺序（别跳）

| 顺序 | 填什么 | 对应文档 | 完成标志 |
|:--:|---|---|---|
| 1 | `models.py` | 04 · C 节 | `python -c "import models"` 通过，`db.get(Book,"B001")` 查得到 |
| 2 | `schemas.py` | 04 · B 节 | `/docs` 里能看到请求体表单 |
| 3 | `security.hash_password` / `verify_password` | 05 · A 节 | `python seed.py` 能跑，库里是 `$2b$12$...` |
| 4 | `routers/books.py` 的 GET 两个 | 04 · 练习 1 | `GET /api/books` 返回分页数据 |
| 5 | `routers/books.py` 的 POST/PATCH/DELETE | 04 · 练习 1 | `?page_size=99999` → 422；删除 → 204 且 `is_deleted=1` |
| 6 | `crud.count_reserved` → **`crud.sync_book`** | 04 · 练习 2 | 借还后 `available` 正确 |
| 7 | `routers/borrows.py` 的 borrow / return ★ | **03 · 练习 3** | 并发测试：修复前 ≥2 个 201，修复后只有 1 个 201 |
| 8 | `security` 的 JWT 与权限依赖 | 05 · B/C/D 节 | 无 Token → 401，读者删书 → 403 |
| 9 | `routers/auth.py` | 05 · 练习 2 | 登录拿到 Token，`/api/auth/me` 能返回自己 |
| 10 | `crud.run_maintenance`（进阶） | 04 · 练习 3 | 过期预约变 `expired`，`available` 加回 1，且幂等 |

## 阶段 4 验收清单（部分）

- [ ] `uvicorn main:app --reload` 启动无报错，`/docs` 有 系统/图书/借阅/鉴权 4 个分组
- [ ] `POST /api/books` 传 `stock:"abc"` → **422**，不是 500
- [ ] `GET /api/books?page_size=99999` → **422**
- [ ] `GET /api/books/{不存在的id}` → **404**
- [ ] `DELETE /api/books/B001` → **204**，MySQL 里 `is_deleted = 1`，数据还在
- [ ] 全项目搜不到 `db.query(`，只有 `select()`
- [ ] 全项目搜不到 `available +=` / `available -=`，只有 `sync_book()` 里的一句赋值
- [ ] `SQL_ECHO=true` 时能数出列表接口发了几条 SQL，并用 `selectinload` 压掉 N+1

## 阶段 5 验收清单（部分）

- [ ] 库里 `password_hash` 全是 `$2b$12$...`，同一个密码两次哈希不相等
- [ ] 同一个密码两次哈希结果不同，但都能校验通过
- [ ] 改 Token 一位字符 / 不带 Token / 过期 Token → **401**
- [ ] 读者 Token 调 `DELETE /api/books/B001` → **403**（不是 401）
- [ ] 读者还别人的书 → **403**（水平越权）
- [ ] 注册时多传 `"role":"admin"` → 库里仍是 `reader`
- [ ] 不存在的用户和错误密码，返回的 `detail` 一模一样
- [ ] `.env` 已在 `.gitignore` 里，`git status` 看不到它

## 和阶段 3 的并发测试联调

```bash
# 后端开着，另开一个窗口：
cd ../03-sql
python concurrency_test.py --concurrency 5
# 阶段 5 开了鉴权之后（脚本要用管理员 Token，因为它是「管理员代借」语义）：
python concurrency_test.py --concurrency 5 --token <A001 登录拿到的 access_token>
```

## 常见问题

| 现象 | 原因 |
|---|---|
| 接口返回 **501** | 这个接口的 TODO 还没填（响应体里会写明是哪个函数） |
| 接口返回 **500** 且日志是 `AttributeError: 'Book' object has no attribute ...` | `models.py` 的字段还没补齐 |
| 启动日志 `建表失败（不影响启动）` | MySQL 没起 / `.env` 里 `DATABASE_URL` 还是占位密码 / 没跑 `schema.sql` |
| 登录返回 **422** | 登录接口吃的是 **form-data**，不是 JSON：`-d "username=..&password=.."` |
| `python seed.py` 报 `NotImplementedError: security.hash_password` | 先完成阶段 5 的 `security.py` 密码哈希 |
| 启动报 `Form data requires "python-multipart"` | 依赖没装全：`pip install -r ../requirements.txt`（登录表单需要它） |
| 并发测试超借 | 借书事务里没有 `with_for_update()`，或锁定读不是事务第一句，或隔离级别监听器没生效 |
