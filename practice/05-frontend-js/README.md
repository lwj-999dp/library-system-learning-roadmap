# 阶段 6 · 纯 JS 版图书前端（练习脚手架）

> 零依赖、无框架、不用 `npm install`、不用构建。**双击 `index.html` 就能打开。**
> 对应文档：[6A HTML/CSS/JS](../../docs/06A-HTML-CSS-JavaScript.md) · [6B JavaScript 进阶](../../docs/06B-JavaScript进阶.md) · [7 前后端联调](../../docs/07-前后端联调.md)

---

## 1. 怎么跑起来

**方式一（最简单）：** 双击 `index.html`。因为用的是普通 `<script src="app.js">`（不是 `type="module"`），`file://` 协议下也能正常工作。

**方式二（更接近真实环境）：** 在本目录起一个静态服务器，然后访问 <http://localhost:8080>。

```bash
cd practice/05-frontend-js
python -m http.server 8080
# 或者： npx serve .
```

打开后按 `F12` → **Console**，你会看到一句欢迎语。输入下面这个命令，就能看到自己做到哪一步了：

```js
runSelfCheck()   // 或者点右下角的「自检」按钮
```

---

## 2. mock 模式 ↔ 后端模式

`app.js` 顶部有一个开关：

```js
const USE_MOCK = true;   // ← 改这里
```

| 值 | 行为 | 什么时候用 |
|:---:|---|---|
| `true`（默认） | `api()` 转发给内置的 `mockApi()`，用本文件里的 6 条假数据 | **后端还没写好的时候**，先专心练前端 |
| `false` | 请求真实后端 `http://127.0.0.1:8000` | 后端能跑之后，做 [阶段 7 联调](../../docs/07-前后端联调.md) |

改成 `false` 之后请确认三件事：① 后端已启动（浏览器打开 `http://127.0.0.1:8000/docs` 能出文档页）；② FastAPI 已配 CORS 或你已用别的办法解决跨源；③ `api()` 那个 TODO 已经做完了。mock 模式还有一个 **「跳过登录」** 按钮，可以在没做登录 TODO 时先练列表部分。

---

## 3. TODO 清单（5 个，从上往下做）

判断标准很简单：**每个待填函数里都有一行占位语句（行尾是 `// NOT_DONE`），删掉它就表示这个空填完了。** 做完一个就在控制台跑一次 `runSelfCheck()`，5 个 ✅ 才算全部完成 —— 它是直接检查函数体，比肉眼可靠。

| # | 函数 | 作用 | 关键提示 | 对应文档 |
|:---:|---|---|---|---|
| ① | `api(path, options)` | 统一请求封装（全项目唯一网络出口） | 注入 `Authorization: Bearer <token>`；`fetch` 不会因 404 而 reject，要自己看 `res.ok`；401 清 Token 跳登录；`body` 要 `JSON.stringify` | 6B「动手练习」、7 第 2 节 |
| ② | `renderBooks(books)` | 数据 → 界面，渲染表格 | **先清空 `tbody`**（忘了会越堆越多）；文本用 `textContent` 防 XSS；按钮必须带 `data-action="borrow"` 和 `data-id` | 6A 第四节 |
| ③ | `filterBooks(keyword)` | 实时搜索过滤 | 返回**新数组**不改原数组；`trim()` + `toLowerCase()` 后 `includes()`；搜书名/作者/ISBN | 6B 第二节 |
| ④ | `handleLogin(event)` | 登录并保存 Token | 登录接口要 `auth: false`（此时还没 Token）；Token 存 `localStorage` 的 `token` key | 6B 的 `auth.js` |
| ⑤ | `handleBorrow(bookId)` | 借书 + 重新拉列表 | 借完必须 `await loadBooks()`；**绝不写 `available - 1`**——库存只有后端说了算 | 7 第 1、7 节 |

已写好的部分**不用改**，它们是参照物：`mockApi()`（假后端）、`loadBooks()`（怎么调 `api()`）、`toast()`、`showPage()`、`bindEvents()`（事件委托）。

---

## 4. 验收标准

- [ ] 打开页面无红色控制台报错
- [ ] `runSelfCheck()` 输出 **5 个 ✅**，并提示「TODO 全部完成」
- [ ] mock 模式点「跳过登录」能进列表页，看到 6 本书；「已借完」的书按钮是灰的
- [ ] 搜索框输入 `javascript` 只剩 1 行；清空后恢复 6 行
- [ ] 点「借书」后 toast 提示成功，且**该书的 `available` 数字来自重新拉取的接口数据**
- [ ] 借 `B002`（库存 0）能看到后端返回的中文错误，而不是白屏
- [ ] 退出登录后回到登录页；刷新页面登录态不丢
- [ ] 把 `USE_MOCK` 改成 `false`、做完 `api()` 后，登录 → 列表 → 借书全流程走通
- [ ] Network 面板里能看到请求带了 `Authorization: Bearer ...`；删掉 localStorage 里的 token 后请求能自动跳回登录页
- [ ] 全项目搜 `document.querySelector`，只出现在 `app.js`，`index.html` 里没有 JS

---

## 5. 卡住了？

| 现象 | 大概率原因 |
|---|---|
| 点了「借书」没反应 | `renderBooks` 里按钮的 `data-action` / `data-id` 没按约定写，事件委托找不到它 |
| 表格行数越搜越多 | `renderBooks` 里忘了清空 `tbody` |
| 搜 `javascript` 搜不到 `JavaScript` | 忘了 `toLowerCase()` |
| 一直提示「登录已过期」 | `localStorage` 的 key 与 `TOKEN_KEY` 不一致，或 `Authorization` 少了 `Bearer ` 前缀 |
| 后端模式报「网络异常」 | 后端没启动、端口写错 —— 先直接用浏览器打开 `http://127.0.0.1:8000/docs` 验证 |

> 这个练习的答案不在本目录，而在文档里：**先自己写 30 分钟**，再去 `docs/06B` 和 `docs/07` 对照参考实现。
