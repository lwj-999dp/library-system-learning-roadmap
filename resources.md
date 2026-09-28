# 学习资源总表

> 全部链接均已实测可访问。**优先级**：🔴 必学 · 🟡 推荐 · ⚪ 选学

---

## 怎么用这份表

1. **不要全看。** 每个阶段只挑 🔴 必学 的部分，学完直接做练习。
2. **看文档优先于看视频。** 视频容易产生「我懂了」的错觉，且回查困难。
3. **英文不好没关系。** 本表优先列中文资源；英文资源只在没有好中文替代时出现。
4. **工时是「看懂 + 敲一遍」的时间**，不含反复复习。实际会浮动 ±30%。

---

## 📊 资源总量速览

| 阶段 | 资源工时 | 练习工时 | 阶段小计 |
|:---:|:---:|:---:|:---:|
| 0 · 环境准备 | 12 | — | **12 h** |
| 1 · Python 基础 | 40 | 20 | **60 h** |
| 2 · Web 与 HTTP | 14 | 4 | **18 h** |
| 3 · 数据库与 SQL ★ | 60 | 20 | **80 h** |
| 4 · FastAPI + SQLAlchemy | 48 | 22 | **70 h** |
| 5 · 鉴权与安全 | 16 | 12 | **28 h** |
| 6A · HTML / CSS / JS | 45 | 10 | **55 h** |
| 6B · JavaScript 进阶 | 25 | 10 | **35 h** |
| 6C · React | 41 | 19 | **60 h** |
| 6D · TypeScript | 18 | 4 | **22 h** |
| 7 · 前后端联调 | 10 | 20 | **30 h** |
| | | | **核心 470 h** |
| 8 · 进阶与部署（选修） | 25 | 20 | **45 h** |

---

## 🧰 通用工具（阶段 0 前装好，全程都用）

| 工具 | 用途 | 下载 | 优先级 |
|---|---|---|---|
| VS Code | 写代码 | <https://code.visualstudio.com/> | 🔴 |
| Git | 版本控制 | <https://git-scm.com/downloads> | 🔴 |
| Node.js (LTS) | 跑前端 | <https://nodejs.org/zh-cn> | 🔴 |
| Python 3.12 | 跑后端 | <https://www.python.org/downloads/> | 🔴 |
| MySQL 8.4 | 数据库 | <https://dev.mysql.com/downloads/> | 🔴 |
| Hoppscotch | 在线测接口（免安装） | <https://hoppscotch.io/> | 🟡 |

> VS Code 必装扩展：`Python`、`Pylance`、`ESLint`、`Prettier`、`SQLTools`、`Chinese (Simplified)` 语言包。

---

## 阶段 0 · 环境准备（12 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| 廖雪峰 Git 教程 | 图文 | 中 | 3 h | 🔴 | <https://liaoxuefeng.com/books/git/index.html> |
| Pro Git 官方书（第 1–3 章） | 电子书 | 中 | 4 h | 🔴 | <https://git-scm.com/book/zh/v2> |
| GitHub Skills 互动课程 | 互动 | 英 | 3 h | 🟡 | <https://skills.github.com/> |
| 环境安装实操（Python/Node/MySQL） | 动手 | — | 2 h | 🔴 | 见 [docs/00](docs/00-环境准备.md) |

**学完必须会：** `git add / commit / push / pull / branch / merge`、看懂 `git status`、配好 SSH key、能启动 MySQL 并连上。

---

## 阶段 1 · Python 基础（60 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **廖雪峰 Python 教程**（第 1–12 章） | 图文 | 中 | 25 h | 🔴 | <https://liaoxuefeng.com/books/python/introduction/index.html> |
| Python 官方教程（中文） | 文档 | 中 | 10 h | 🟡 | <https://docs.python.org/zh-cn/3/tutorial/> |
| 菜鸟教程 Python3（当字典查） | 速查 | 中 | 5 h | 🟡 | <https://www.runoob.com/python3/python3-tutorial.html> |
| CS50P 哈佛 Python 课 | 视频 | 英 | 20 h | ⚪ | <https://cs50.harvard.edu/python/> |
| 自己写 5 个小脚本 | 动手 | — | 20 h | 🔴 | 见 [docs/01](docs/01-Python基础.md) |

**重点章节：** 数据类型 → 函数 → 高级特性（切片/迭代/列表生成式）→ 模块 → 面向对象 → 错误处理。

**可以跳过：** 图形界面（turtle）、电子邮件、区块链等与 Web 无关的章节。

---

## 阶段 2 · Web 与 HTTP 基础（18 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| MDN · HTTP 概述 | 文档 | 中 | 4 h | 🔴 | <https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Overview> |
| MDN · 学习网页开发（了解全貌） | 教程 | 中 | 4 h | 🟡 | <https://developer.mozilla.org/zh-CN/docs/Learn> |
| FastAPI 官方中文文档（先读「教程-用户指南」） | 文档 | 中 | 6 h | 🔴 | <https://fastapi.tiangolo.com/zh/> |
| 动手：写 `/health` + 内存版 CRUD | 动手 | — | 4 h | 🔴 | 见 [docs/02](docs/02-Web与HTTP基础.md) |

**学完必须会：** 说清 `GET/POST/PUT/DELETE` 区别、`200/201/400/401/403/404/500` 各自含义、什么是请求体/响应体、什么是 CORS。

---

## 阶段 3 · 数据库与 SQL ★核心（80 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **SQLBolt 互动教程** | 互动 | 英 | 10 h | 🔴 | <https://sqlbolt.com/> |
| **廖雪峰 SQL 教程** | 图文 | 中 | 12 h | 🔴 | <https://liaoxuefeng.com/books/sql/index.html> |
| SQLZoo 在线练习 | 互动 | 英 | 8 h | 🟡 | <https://sqlzoo.net/> |
| **小林coding · 图解 MySQL**（事务篇 + 锁篇） | 图文 | 中 | 15 h | 🔴 | <https://xiaolincoding.com/mysql/> |
| MySQL 官方手册 · 事务隔离级别 | 文档 | 英 | 8 h | 🟡 | <https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html> |
| Use The Index, Luke（索引原理） | 图文 | 英 | 7 h | ⚪ | <https://use-the-index-luke.com/> |
| 动手：建库 + 复现超借 + 修复 | 动手 | — | 20 h | 🔴 | 见 [docs/03](docs/03-数据库与SQL.md) |

**这一阶段的必读顺序（重要）：**

```
SQLBolt 基础语法
      ↓
廖雪峰 SQL（建表 / JOIN / GROUP BY）
      ↓
小林coding 事务篇  ← 理解 MVCC、隔离级别
      ↓
小林coding 锁篇    ← 理解行锁、间隙锁、死锁
      ↓
动手复现「5 并发借 1 本库存书，4 个都成功」的 bug
      ↓
用 SELECT ... FOR UPDATE + READ COMMITTED 修好
```

---

## 阶段 4 · FastAPI + SQLAlchemy + Pydantic（70 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **FastAPI 官方中文文档 · 用户指南**（全） | 文档 | 中 | 25 h | 🔴 | <https://fastapi.tiangolo.com/zh/tutorial/> |
| **SQLAlchemy 2.0 ORM 快速入门** | 文档 | 英 | 8 h | 🔴 | <https://docs.sqlalchemy.org/en/20/orm/quickstart.html> |
| SQLAlchemy 2.0 官方文档（全） | 文档 | 英 | 7 h | 🟡 | <https://docs.sqlalchemy.org/en/20/> |
| Pydantic 官方文档 | 文档 | 英 | 8 h | 🟡 | <https://docs.pydantic.dev/latest/> |
| 动手：完整图书 CRUD API | 动手 | — | 22 h | 🔴 | 见 [docs/04](docs/04-FastAPI与SQLAlchemy.md) |

**重点：** `Depends` 依赖注入、`response_model`、`select()` 2.0 写法、`selectinload` 解决 N+1。

---

## 阶段 5 · 鉴权与安全（28 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **FastAPI 官方 · 安全性章节** | 文档 | 中 | 6 h | 🔴 | <https://fastapi.tiangolo.com/zh/tutorial/security/> |
| JWT 官方介绍 | 文档 | 英 | 3 h | 🔴 | <https://jwt.io/introduction> |
| OWASP · 密码存储速查表 | 文档 | 英 | 3 h | 🔴 | <https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html> |
| bcrypt / PyJWT 实操 | 动手 | — | 4 h | 🔴 | 见 [docs/05](docs/05-鉴权与安全.md) |
| 动手：给 API 加登录鉴权 | 动手 | — | 12 h | 🔴 | 见 [docs/05](docs/05-鉴权与安全.md) |

---

## 阶段 6A · HTML / CSS / JavaScript（55 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **MDN · 学习网页开发**（HTML + CSS 部分） | 教程 | 中 | 20 h | 🔴 | <https://developer.mozilla.org/zh-CN/docs/Learn> |
| **MDN · JavaScript 第一步** | 教程 | 中 | 15 h | 🔴 | <https://developer.mozilla.org/zh-CN/docs/Learn/JavaScript> |
| freeCodeCamp 中文视频 | 视频 | 中 | 10 h | 🟡 | <https://www.bilibili.com/video/BV1sD421p7XM/> |
| 动手：纯 HTML/CSS 静态页面 | 动手 | — | 10 h | 🔴 | 见 [docs/06A](docs/06A-HTML-CSS-JavaScript.md) |

---

## 阶段 6B · JavaScript 进阶（35 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **现代 JavaScript 教程**（第一部分） | 图文 | 中 | 20 h | 🔴 | <https://zh.javascript.info/> |
| ES6 入门教程 · 阮一峰 | 电子书 | 中 | 5 h | 🟡 | <https://es6.ruanyifeng.com/> |
| 动手：待办清单 + fetch 调 API | 动手 | — | 10 h | 🔴 | 见 [docs/06B](docs/06B-JavaScript进阶.md) |

**必须吃透：** `Promise` / `async-await`、`map/filter/find/reduce`、解构、展开运算符、模块 `import/export`、`fetch`。

> ⚠️ 这一步不过关，React 会学得非常痛苦。这是全流程最容易被跳过、后果最严重的一环。

---

## 阶段 6C · React（60 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **React 官方中文文档 · Learn** | 文档 | 中 | 25 h | 🔴 | <https://zh-hans.react.dev/learn> |
| React 官方 · Thinking in React | 文档 | 中 | 3 h | 🔴 | <https://zh-hans.react.dev/learn/thinking-in-react> |
| Tailwind CSS 文档 | 文档 | 英 | 6 h | 🟡 | <https://tailwindcss.com/docs> |
| Vite 中文文档 | 文档 | 中 | 3 h | 🟡 | <https://cn.vitejs.dev/guide/> |
| shadcn/ui 文档 | 文档 | 英 | 4 h | ⚪ | <https://ui.shadcn.com/docs/installation/vite> |
| 动手：React 版图书管理页面 | 动手 | — | 19 h | 🔴 | 见 [docs/06C](docs/06C-React.md) |

---

## 阶段 6D · TypeScript（22 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| **TypeScript 官方手册（中文）** | 文档 | 中 | 10 h | 🔴 | <https://www.typescriptlang.org/zh/docs/handbook/2/basic-types.html> |
| TypeScript 入门教程（xcatliu） | 电子书 | 中 | 5 h | 🟡 | <https://ts.xcatliu.com/> |
| type-challenges（只做简单题） | 练习 | 英 | 3 h | ⚪ | <https://github.com/type-challenges/type-challenges> |
| 动手：给 React 项目补类型 | 动手 | — | 4 h | 🔴 | 见 [docs/06D](docs/06D-TypeScript.md) |

---

## 阶段 7 · 前后端联调（30 h）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| MDN · Fetch 用法 | 文档 | 中 | 4 h | 🔴 | <https://zh.javascript.info/fetch> |
| MDN · Fetch 跨源请求（CORS） | 文档 | 中 | 3 h | 🔴 | <https://zh.javascript.info/fetch-crossorigin> |
| Hoppscotch / Postman 调试接口 | 工具 | 中 | 3 h | 🟡 | <https://hoppscotch.io/> |
| 动手：前端接后端 + 排错 | 动手 | — | 20 h | 🔴 | 见 [docs/07](docs/07-前后端联调.md) |

---

## 阶段 8 · 进阶与部署（45 h，选修）

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| 12-Factor App（中文） | 文档 | 中 | 5 h | 🟡 | <https://12factor.net/zh_cn/> |
| RealWorld 全栈示例项目 | 代码 | 英 | 10 h | 🟡 | <https://github.com/gothinkster/realworld> |
| system-design-primer | 代码 | 英 | 10 h | ⚪ | <https://github.com/donnemartin/system-design-primer> |
| 动手：Docker 部署 + 并发压测 | 动手 | — | 20 h | 🔴 | 见 [docs/08](docs/08-进阶与部署.md) |

---

## 📚 GitHub 学习类仓库（按需取用，不要通读）

| 仓库 | 星数 | 用途 | 链接 |
|---|:---:|---|---|
| developer-roadmap | 368k | 各方向技能树总览 | <https://github.com/nilbuild/developer-roadmap> |
| freeCodeCamp | 456k | 免费全栈课程 | <https://github.com/freeCodeCamp/freeCodeCamp> |
| project-based-learning | 285k | 用做项目的方式学 | <https://github.com/practical-tutorials/project-based-learning> |
| system-design-primer | — | 系统设计入门 | <https://github.com/donnemartin/system-design-primer> |
| HelloGitHub | — | 中文开源项目月刊 | <https://github.com/521xueweihan/HelloGitHub> |
| studyline | 48 | 中文技术面试学习路线合集 | <https://github.com/zhilicode/studyline> |
| awesome-react | — | React 生态资源 | <https://github.com/enaqx/awesome-react> |
| awesome | — | 各种 awesome 列表总入口 | <https://github.com/sindresorhus/awesome> |
| typescript-tutorial | 10.7k | TypeScript 中文入门 | <https://github.com/xcatliu/typescript-tutorial> |
| type-challenges | 48.5k | TS 类型体操 | <https://github.com/type-challenges/type-challenges> |

---

## 🎥 视频资源说明

**本表刻意少列视频**，原因：

1. 视频**回查困难** —— 忘了某个语法要拖进度条，文档可以直接 Ctrl+F。
2. 视频**容易产生虚假掌握感** —— 看着老师敲觉得自己会了，一关视频就写不出来。
3. 视频**更新滞后** —— React 19、FastAPI 0.115 这类新版本，文档永远最新。

**建议配方：** 文档为主（70%）+ 视频为辅（30%，只在某个概念文档读不懂时去看）。

如果一定要看视频，优先选：

| 方向 | 推荐 | 说明 |
|---|---|---|
| Python | [CS50P](https://cs50.harvard.edu/python/) | 哈佛出品，作业质量极高，英文但有字幕 |
| 前端 | [freeCodeCamp 中文](https://www.bilibili.com/video/BV1sD421p7XM/) | 体系完整，免费 |
| 数据库 | [小林coding](https://xiaolincoding.com/mysql/) | 图文为主，比视频更适合理解事务与锁 |

---

## ❌ 不要学的东西（省时间）

新手最大的时间黑洞是「想把每个依赖都学明白」。以下内容**本项目用不到**，直接跳过：

| 内容 | 为什么跳过 |
|---|---|
| Docker / K8s | 阶段 8 再碰 |
| Redis / 消息队列 | 本项目的量级不需要 |
| 微服务 / 分布式 | 先把单体做明白 |
| Webpack 配置 | 用 Vite，零配置 |
| CSS 预处理器（Sass/Less） | Tailwind 已够用 |
| jQuery | 过时技术，别学 |
| 通读 `node_modules` | 永远不要打开 |
| 手写 shadcn/ui 组件 | 用 CLI 生成 |

---

[← 返回首页](README.md) · [里程碑与验收 →](milestones.md)
