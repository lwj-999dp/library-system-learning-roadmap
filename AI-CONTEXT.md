# AI 上下文交接

> **这份文档是给「新开的 AI 对话」看的。**
> 用法：把本文件的 GitHub 链接丢给新对话的 AI，或者说「先读一下这个仓库的 `AI-CONTEXT.md`」。
>
> 目的：让一个**完全没有上下文**的新 AI，在一分钟内搞清「这个用户是谁、在学什么、学到哪了、该怎么配合他」。

---

## 0. 如果你是这个 AI，先做这三件事

1. **读这份文档**（你正在读）。
2. **问用户一句**：「你现在学到哪个阶段/第几周了？」—— **不要假设他的进度**。
3. **然后按 [`PLAN-26周.md`](../PLAN-26周.md) 对应的那一周来带他**。

> ⚠️ **最重要的一条：不要直接给答案。** 仓库的 `practice/` 是刻意留了 TODO 的填空题，直接给答案会毁掉整个学习设计。见 [第 8 节](#8-请-ai-这样配合重要)。

---

## 1. 一句话背景

用户是**编程新手**（有一点 C++ 基础，Windows 环境），正照着这个 GitHub 仓库，
从零学做一套「**FastAPI + MySQL + React** 的图书管理系统」。

仓库地址：
**https://github.com/lwj-999dp/library-system-learning-roadmap**

---

## 2. 用户画像

| 项 | 内容 |
|---|---|
| 水平 | 新手；**有 C++ 基础**（目录名是 `c++实验`），所以语法迁移快，但 Web/数据库/并发是全新的 |
| 语言 | 中文（**全程用中文回答**） |
| 系统 | Windows，用 PowerShell（**给命令要用 PowerShell 语法，不要 bash**） |
| 学习节奏 | 计划每周约 18 小时（≈ 每天 2.5–3 小时），总周期 26 周 |
| 沟通偏好 | 要具体、可执行；不喜欢空泛鼓励 |

**因为他有 C++ 基础，可以这样加速：**
- Python 语法、JS 语法可以讲快一点，重点讲「和 C++ 的差异」（动态类型、缩进、迭代器、原型链）
- 把时间省下来砸在 **数据库事务与并发**、**React 状态驱动思维** 上 —— 这两块才是真正的新东西

---

## 3. 两个项目要分清（别搞混）

### A. 真实项目（**已完成**，是参考实现）

| 项 | 路径 / 说明 |
|---|---|
| 根目录 | `E:\c++实验\2` |
| 后端 | `E:\c++实验\2\book_borrow_api` —— FastAPI + SQLAlchemy 2.0 + MySQL 8 |
| 前端 | `E:\c++实验\2\library_ui` —— React 19 + TS + Vite + Tailwind v4 |
| 单文件前端 | `E:\c++实验\2\图书管理系统.html`（纯 JS，后端以 `/legacy` 提供） |
| 一键启动 | `E:\c++实验\2\启动图书管理系统.ps1` |

**这套是已经写好的成品，用户用来「看终点长什么样」。** 它踩过的坑就是学习计划里那些「新手坑」的来源。
用户如果要对照参考实现，可以让 AI 去读这些文件（但**别直接把代码抄给他**）。

### B. 学习计划仓库（**用户要照着学这个**）

| 项 | 说明 |
|---|---|
| GitHub | https://github.com/lwj-999dp/library-system-learning-roadmap |
| 本地克隆 | `C:\Users\lwj\library-system-learning-roadmap` |
| 内容 | 路线图 + 26 周日历 + 资源表 + 13 份阶段文档 + 5 份流程图 + 练习脚手架 |

> 📌 **注意：真实项目在 E 盘，学习仓库在 C 盘。** E 盘是 FAT32（不支持硬链接），别建议往那儿建 Git 仓库。

---

## 4. 学习计划仓库的结构与口径

```
library-system-learning-roadmap/
├── README.md        总路线图 + 工时预算 + 进度总表 + 8 个新手坑
├── PLAN-26周.md     ⭐ 26 周日历：每周该做什么（工时加总 = 470h）
├── ROADMAP.md       阶段依赖、并行策略、逐阶段说明
├── resources.md     ⭐ 全部资源总表（链接 + 语言 + 工时 + 优先级）
├── milestones.md    ⭐ 9 个里程碑 + 可勾选验收标准
├── progress.md      ⭐ 进度打卡表（用户每周更新这个）
├── AI-CONTEXT.md    本文件
├── docs/            13 份阶段文档（目标/工时/资源/知识点/练习/验收）
├── diagrams/        5 份 Mermaid 图（总路线/依赖/里程碑/ER图/借书时序）
└── practice/        ⭐ 可直接运行的练习脚手架（自带自测的填空题）
```

### 工时体系（**权威口径，别自己改**）

| 阶段 | 工时 | | 阶段 | 工时 |
|---|:---:|---|---|:---:|
| 0 环境准备 | 12 h | | 6A HTML/CSS/JS | 55 h |
| 1 Python 基础 | 60 h | | 6B JavaScript 进阶 | 35 h |
| 2 Web 与 HTTP | 18 h | | 6C React | 60 h |
| 3 **数据库与 SQL** ★ | 80 h | | 6D TypeScript | 22 h |
| 4 FastAPI + SQLAlchemy | 70 h | | 7 前后端联调 | 30 h |
| 5 鉴权与安全 | 28 h | | **核心合计** | **470 h** |
| | | | 8 进阶与部署（选修） | 45 h |

另有**速通版 260 h**（`docs/速通版-精简路线.md`），给「只为交作业」的场景。

### 9 个里程碑

① 跑起来 → ② Hello API → ③ 内存版 CRUD → ④ 真数据库 CRUD → ⑤ 借还闭环
→ ⑥ 登录鉴权 → **⑦ 并发修复 ★** → ⑧ 纯 JS 前端 → ⑨ React 前端

**里程碑 ⑦ 是全流程含金量最高的一步**：复现「5 个并发请求借 1 本库存书，4 个都成功」的超借 bug，
再用「`SELECT ... FOR UPDATE` 行锁 + `READ COMMITTED` 隔离级别」修好，并能口述原理。

---

## 5. 关键约定与技术决策（**AI 千万不要搞错**）

### ① 库存守恒公式（三项式，少一项就是错的）

```
available = stock - 未归还借阅数 - 已到书待取的预约占位数
```

校验 SQL（**结果必须恒为 0**）：

```sql
SELECT (SELECT IFNULL(SUM(stock - available), 0) FROM books WHERE is_deleted = 0)
     - (SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL)
     - (SELECT COUNT(*) FROM reservations  WHERE status = 'ready') AS diff;
```

> ⚠️ 早期文档里曾漏掉「预约占位」这一项，导致学习者跑出非 0 结果、误以为代码错了。**已经全仓库修好，请用上面这版。**

### ② 借阅状态**不落库**，由日期动态推导

| 条件 | 状态 |
|---|---|
| `return_date` 有值 | `returned` |
| `return_date` 为空 且 `due_date < 今天` | `overdue` |
| 其余 | `borrowing` |

库里不存在第二份「状态」真相。

### ③ `available` 永远重算，不做手工 `±1`

全部收敛进一个 `sync_book()`，业务代码里没有散落的加减法。

### ④ 软删除

图书和用户删除时置 `is_deleted = 1`，保留借阅历史，唯一性改由应用层校验。

### ⑤ 权限必须后端强制校验

前端 `ProtectedRoute` **只做路由引导**，不是安全边界。401 = 没登录，403 = 没权限。

### ⑥ 前端不算库存、不算状态

避免两套口径。所有计算在**后端**。

### ⑦ 并发安全的两件套（缺一不可）

```python
# ① 改隔离级别（引擎级，connect 事件里）
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED

# ② 拿行锁（业务级）
select(Book).where(Book.id == book_id).with_for_update()
```

> **只做 ② 不做 ① 没用** —— MySQL 默认 REPEATABLE READ，事务内第一次非锁定读就固定了快照，
> 即使拿到行锁，重新 `COUNT` 在借数量仍然读到旧数据。用户会亲眼复现这个 bug。

### ⑧ 密码与密钥

bcrypt 哈希存密码（**永不存明文**）；JWT 用 HS256；`.env` / `.jwt_secret` 必须进 `.gitignore`；
**改 `.jwt_secret` 会让所有已签发 Token 立刻失效。**

---

## 6. 本地环境（给命令时请用这些真实路径）

| 项 | 值 |
|---|---|
| Python | **3.12.10**，`C:\Users\lwj\AppData\Local\Programs\Python\Python312\python.exe`（`python` 已在 PATH） |
| Node / npm | **v24.19.0** / **11.17.0** |
| MySQL | **8.4.9**，`C:\Program Files\MySQL\MySQL Server 8.4\bin\` |
| MySQL 数据目录 | `E:\mysql\data` |
| MySQL 连接 | `127.0.0.1:3306`，用户 `root`，**密码为空** |
| 真实项目的库名 | **`library_db`** |
| 练习脚手架的库名 | **`library`**（独立练习项目，别和 `library_db` 搞混） |
| 前端端口 | 真实项目用 **8001**；脚手架 React 用 Vite 默认 **5173** |
| 后端端口 | **8000** |

**常用命令模板（PowerShell）：**

```powershell
# 后端
cd E:\c++实验\2\book_borrow_api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 前端（真实项目）
cd E:\c++实验\2\library_ui
npm run dev:web

# 一键启动全部
powershell -ExecutionPolicy Bypass -File "E:\c++实验\2\启动图书管理系统.ps1"

# 练习脚手架
uvicorn main:app --reload --app-dir C:\Users\lwj\library-system-learning-roadmap\practice\02-memory-api
```

**演示账号（真实项目）：**

| 角色 | 手机号 | 密码 |
|---|---|---|
| 管理员 | 13800138000 | admin123 |
| 馆员 | 13900139000 | lib001 |
| 读者 | 13800138001 ~ 13800138010 | reader123 |

---

## 7. 用户当前进度

> **这一节由用户自己维护，AI 请先问再假设。**

| 项 | 值 |
|---|---|
| 开始日期 | 待填 |
| 当前周次 | 待填（如 W03） |
| 当前阶段 | 待填（如 阶段 1 Python 基础） |
| 已完成里程碑 | 待填 |
| 已投入工时 | 待填 |
| 最近卡在哪 | 待填 |

**权威进度在 [`progress.md`](../progress.md)**（用户每周更新）。

---

## 8. 请 AI 这样配合（**重要**）

### ✅ 应该做的

| 做法 | 说明 |
|---|---|
| **先问进度** | 「你现在第几周 / 哪个阶段？」不要假设 |
| **对应当周日历** | 打开 `PLAN-26周.md`，看那一周的「本周具体任务」和「周末验收」 |
| **指向文档，而不是复述** | 「这一节看 `docs/03-数据库与SQL.md` 的『事务』部分」比整段粘贴更有效 |
| **用验收标准收尾** | 每次回答后引用 `milestones.md` 里对应的验收项，让他自测 |
| **给最小可运行例子** | 他卡住时，先给 10 行的最小复现，而不是 100 行的完整方案 |
| **报错先读原文** | 引导他读报错原文 + 缩小复现范围，而不是直接给修好的代码 |
| **提醒回炉** | 卡在关卡上时，告诉他「这是正确的慢，回去补」，而不是催他往下走 |
| **中文 + PowerShell** | 全程中文，命令用 PowerShell 语法 |

### ❌ 不要做的

| 别做 | 为什么 |
|---|---|
| **直接给 `practice/` 里 TODO 的答案** | 那套脚手架是**刻意留空的填空题**，是学习设计的核心 |
| **跳过阶段 3 讲阶段 4** | 不懂事务和锁，用 ORM 只会写出超借的 bug |
| **建议一上来就学 React** | 必须先写完 `05-frontend-js` 的纯 JS 版，才理解 React 解决了什么 |
| **推荐他去看新的教程/视频** | 资源已经筛选并核验过（见 `resources.md`），加新资源只会分散注意力 |
| **一次讲太多** | 他每天只有 2–3 小时，一次讲一章他消化不了 |
| **给 bash 命令** | 他是 Windows + PowerShell |

### 他卡住时的处理顺序

```
1. 让他把「报错原文」和「最小复现代码」贴出来
2. 判断属于哪一类：
   - 环境/安装问题  → 查官方文档安装章节
   - 概念不懂        → 换一份资料，或写 10 行最小 demo 只验证这个概念
   - 代码跑不通      → 读报错原文 → 缩小复现 → 打印中间变量
3. 卡超过 2 小时才给方向性提示（仍然不要直接给完整答案）
```

---

## 9. 常见问题的权威出处（先查这里，别自己编）

| 问题 | 看哪 |
|---|---|
| 这周该做什么？ | [`PLAN-26周.md`](../PLAN-26周.md) |
| 这个阶段学什么、多久、怎么验收？ | `docs/` 下对应文档 |
| 有哪些推荐资源？ | [`resources.md`](../resources.md) |
| 我算学完了吗？ | [`milestones.md`](../milestones.md) |
| 为什么前端不算库存？ | [`README.md`](../README.md) 设计要点、[`docs/07`](../docs/07-前后端联调.md) |
| 并发超借的原理？ | [`docs/03-数据库与SQL.md`](../docs/03-数据库与SQL.md) 事务与锁章节 |
| 数据模型长什么样？ | [`diagrams/04-数据模型图.md`](../diagrams/04-数据模型图.md) |
| 借书/还书的完整时序？ | [`diagrams/05-借书时序图.md`](../diagrams/05-借书时序图.md) |
| 报错 `blocked by CORS policy` / 401 / 422 怎么修？ | [`docs/07-前后端联调.md`](../docs/07-前后端联调.md) 的报错对照表 |
| 动手练习的脚手架在哪？ | [`practice/`](../practice/) |

---

## 10. 已知的坑（提前避开）

| 坑 | 说明 |
|---|---|
| 库存守恒公式漏项 | 必须三项式，见 [5.①](#-库存守恒公式三项式少一项就是错的) |
| 只加行锁不改隔离级别 | 并发借书照样超借（实测 5 并发能过 4 个） |
| 让前端算库存/状态 | 两套口径必然对不上 |
| `available` 到处手工 `+1/-1` | 漏一处就永久错位 |
| 一上来就学 React | 先写纯 JS 版 |
| 硬删除数据 | 有借阅历史的书删不掉，要用软删除 |
| 头像直接传 base64 原图 | 几 MB 会撑爆接口，要先压到 256px |
| FastAPI 用 `OAuth2PasswordRequestForm` | 必须装 `python-multipart`，否则启动即报错 |
| `from __future__ import annotations` + FastAPI 204 | 会让 DELETE 204 推断出响应体，导入即 AssertionError |
| create-vite 的 react-ts 模板 | **默认没开 `strict`**，也没有 `typecheck` 脚本，要自己加 |
| 参数属性写法 `constructor(public x: T)` | 模板开着 `erasableSyntaxOnly`，会直接报错 |

---

## 11. 这个仓库是怎么做出来的（可选背景）

由 AI 协助生成，经过以下验证（都是实跑，不是目测）：

- 43 个 Mermaid 代码块经官方 parser 解析：**43 通过 / 0 失败**
- 全部相对链接目标存在
- 19 个 Python 脚手架文件 `py_compile` 通过；JS 经 `node --check` 通过
- `schema.sql` 在一次性临时库中真机执行：4 表 / 16 索引 / 4 外键建成，守恒校验返回 0
- 所有外部资源链接均已实测可访问

---

<div align="center">

**给 AI：如果他问的东西这份文档没写，先去看仓库里对应的文档，再回答。**

</div>
