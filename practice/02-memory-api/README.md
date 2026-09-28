# 阶段 2 · 内存版图书 CRUD（练习脚手架）

> **数据存在内存里，进程一关就没。** 这是故意的：阶段 2 只练「HTTP 接口长什么样」，
> 阶段 4 才会把它换成真正的 MySQL。

对应文档：[`docs/02-Web与HTTP基础.md`](../../docs/02-Web与HTTP基础.md) ｜ 里程碑：[③ 内存版 CRUD](../../milestones.md)

---

## 怎么跑起来

```powershell
# 1. 装依赖（第一次才需要，在仓库根目录执行）
pip install -r practice/requirements.txt

# 2. 启动服务（改代码会自动重启）
uvicorn main:app --reload --app-dir practice/02-memory-api

# 3. 打开自动生成的接口文档，点 Try it out 直接调
#    http://127.0.0.1:8000/docs

# 4. 不启服务，只想知道自己 TODO 做完没有
python practice/02-memory-api/main.py
```

---

## 接口清单

| 方法 | 路径 | 干什么 | 成功状态码 | 失败状态码 |
|---|---|---|:---:|---|
| `GET` | `/health` | 健康检查（已写好，不用改） | 200 | — |
| `GET` | `/books` | 图书列表；`?keyword=三体` 按书名模糊搜索 | 200 | — |
| `POST` | `/books` | 新增图书，body 传 `title / author / stock` | **201** | 422（字段非法） |
| `PUT` | `/books/{book_id}` | 局部更新，只改传上来的字段 | 200 | 404（id 不存在）/ 422 |
| `DELETE` | `/books/{book_id}` | 删除图书 | **204**（无响应体） | 404（id 不存在） |

预置数据：`B001 三体 / B002 活着 / B003 人类简史`，新增图书 id 从 `B004` 开始自增。

---

## 测试例子（curl，PowerShell / Git Bash 都能用）

```bash
# 列表：应该返回 3 本
curl http://127.0.0.1:8000/books

# 搜索：应该只返回《三体》
curl "http://127.0.0.1:8000/books?keyword=三体"

# 新增合法：应该看到 HTTP/1.1 201 Created，响应体 id 是 B004
curl -i -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"呐喊","author":"鲁迅","stock":2}'

# 参数非法：应该看到 422（书名不能为空、库存类型不对）
curl -i -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"","author":"鲁迅","stock":"abc"}'

# 局部更新：只传 stock，返回的 author 必须还在
curl -i -X PUT http://127.0.0.1:8000/books/B001 \
  -H "Content-Type: application/json" -d '{"stock":9}'

# 更新不存在的 id：应该 404
curl -i -X PUT http://127.0.0.1:8000/books/B999 \
  -H "Content-Type: application/json" -d '{"stock":1}'

# 删除：第一次 204（无响应体），第二次 404
curl -i -X DELETE http://127.0.0.1:8000/books/B002
curl -i -X DELETE http://127.0.0.1:8000/books/B002
```

> 不想敲命令行就用 [Hoppscotch](https://hoppscotch.io/)：方法选 POST，URL 填
> `http://127.0.0.1:8000/books`，Body 选 `application/json`，把 JSON 填进去点 Send。
> **重点看返回的状态码**，不只是看响应体 —— 状态码是前后端约定的语言。

---

## 验收标准

- [ ] `python main.py` 的自测项全部 `[x]`（逻辑层面：列表 / 过滤 / 自增 id / 局部更新 / 404）
- [ ] `/docs` 能打开，5 个接口都在，能点 `Try it out` 调通
- [ ] `POST /books` 返回 **201**，`DELETE` 返回 **204**，`PUT` 不存在的 id 返回 **404**
- [ ] `stock` 传字符串或 `title` 传空串时返回 **422**，**不是 500**
- [ ] `PUT /books/B001` 只传 `stock` 时，`author` / `title` 没有被清空
- [ ] 能口头回答：`422` 是谁的问题？为什么 `/docs` 不用自己写前端？`PUT` 和 `PATCH` 差在哪？

---

## 卡住了看哪里

| 现象 | 原因 / 去哪看 |
|---|---|
| `[ ] 接口 N …… 未完成（第 X 行 TODO）` | 打开 `main.py` 跳到第 X 行，读 TODO 上方的「提示」和「预期结果」 |
| 接口返回 500 且日志里是 `NotImplementedError` | 正常 —— 那个接口你还没写 |
| `[Errno 10048] address already in use` | 8000 端口被占：`uvicorn main:app --port 8001 --app-dir practice/02-memory-api` |
| 返回 404 但路径看着没错 | 检查是不是少写了 `/books` 前缀，或 id 写成 `1` 而不是 `B001` |
| 前端调这个接口报 CORS | 见 `docs/02-Web与HTTP基础.md` 第 4 节，后端加 `CORSMiddleware` |

[← 返回练习总览](../README.md) ｜ [阶段 2 文档](../../docs/02-Web与HTTP基础.md)
