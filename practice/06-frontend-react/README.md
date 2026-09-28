# 阶段 6 · React 版图书前端（脚手架 + 初始化步骤）

> 这个目录**不是**一个完整的 npm 工程（那样会往仓库里塞几百 MB 的 `node_modules`）。
> 它给你的是：① 一条条可复制的初始化命令；② 5 个已经写好的骨架文件；③ 明确的 TODO 与验收标准。
> 对应文档：[6C React](../../docs/06C-React.md) · [6D TypeScript](../../docs/06D-TypeScript.md) · [7 前后端联调](../../docs/07-前后端联调.md)

---

## 1. 第一步：创建项目

在**仓库外面**找个目录（别在 `practice/` 里建，不然 `node_modules` 会污染仓库）：

```bash
npm create vite@latest my-library -- --template react-ts
cd my-library
npm install
```

> ⚠️ 一定要 `--template react-ts`。纯 `react` 模板没有 TypeScript，后面的类型练习全废。

## 2. 第二步：装依赖

```bash
npm install react-router-dom                       # 路由 + 守卫
npm install tailwindcss @tailwindcss/vite          # Tailwind v4（配置写在 CSS 里，没有 tailwind.config.js）
npx shadcn@latest init                             # 可选：shadcn/ui 初始化
npx shadcn@latest add button input table           # 可选：UI 组件一律用 CLI 生成，不要手写（docs/06C 常见坑 11）
```

**① 让 `npm run typecheck` 能用**——Vite 模板默认**没有**这个脚本，自己往 `package.json` 的 `scripts` 里加一行：

```json
"typecheck": "tsc --noEmit -p tsconfig.app.json"
```

（模板若没有 `tsconfig.app.json` 就写 `"typecheck": "tsc --noEmit"`。）

**② 把 `strict` 打开**——实测当前 `create-vite` 的 `react-ts` 模板**默认没开 `strict`**。不开就等于白装 TypeScript：`any` 到处漏、`null` 不检查，阶段 6D 的类型练习全废。打开 `tsconfig.app.json`，在 `compilerOptions` 里加一行：

```json
"strict": true
```

> 💡 顺便看一下这个文件里已有的 `noUnusedLocals` / `noUnusedParameters` / `erasableSyntaxOnly` ——
> 它们就是本目录骨架里那些「占位语句」存在的原因：TODO 没填完时，未使用的变量会让 typecheck 报错。
> 还有 `erasableSyntaxOnly`：所以 `ApiError` 里**不要**写成 `constructor(public status: number, …)` 那种
> 「构造函数参数属性」语法，那样会直接报错。

**② 配 Vite 代理**——开发环境首选，写完**永远不会有 CORS 问题**（docs/07 第 4 节方案 B）：

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: { "/api": { target: "http://127.0.0.1:8000", changeOrigin: true } },
  },
});
```

**③ Tailwind v4 的设计令牌**（`src/index.css`）：

```css
@import "tailwindcss";

@theme {
  --color-brand-50: #f0fdf4;
  --color-brand-500: #22c55e;
  --color-brand-700: #15803d;
}
```

## 3. 第三步：把这 5 个文件抄进去

**建议手敲，不要复制粘贴**（docs/07 练习 1 的原话）。文件名前缀 `src-` 只表示「要放到 `src/` 里」，别把前缀也带进项目。

| 本目录的文件 | 复制到 | 给的是什么 |
|---|---|---|
| `src-types.ts` | `src/data/types.ts` | **完整版**：数据契约，不用填空 |
| `src-api-client.ts` | `src/api/client.ts` | 骨架：`request()` 与 `extractError()` 留 TODO；`login/listBooks/borrowBook` 已写好 |
| `src-AuthContext.tsx` | `src/context/AuthContext.tsx` | 骨架：`login()` 留 TODO；`logout()` 与「从 localStorage 恢复」已写好 |
| `src-ProtectedRoute.tsx` | `src/routes/ProtectedRoute.tsx` | 骨架：未登录重定向留 TODO |
| `src-BooksPage.tsx` | `src/pages/BooksPage.tsx` | 骨架：拉数据 / 渲染表格 / 借书 留 TODO |

复制完的目录结构应该是：

```
src/
├── api/client.ts              ← 唯一的网络出口
├── data/types.ts              ← 类型契约
├── context/AuthContext.tsx    ← 登录态
├── routes/ProtectedRoute.tsx  ← 路由守卫
├── hooks/useDebounce.ts       ← 你自己写（见下）
├── pages/LoginPage.tsx        ← 你自己写
├── pages/BooksPage.tsx        ← 骨架
├── components/Layout.tsx      ← 你自己写
├── App.tsx                    ← 你自己写（拼路由）
└── main.tsx                   ← 模板自带，把 <AuthProvider> 包上去
```

## 4. 要你自己写的 4 个文件

| 文件 | 干什么 | 验收标准 |
|---|---|---|
| `src/hooks/useDebounce.ts` | 自定义 Hook：输入停止 300ms 才返回新值 | 用 `useEffect` + `setTimeout`，**清理函数里 `clearTimeout`**；快速输入时 BooksPage 只发 1 次请求（看 Network 面板） |
| `src/pages/LoginPage.tsx` | 登录页：两个受控 input + 提交 | 调 `login()`（client.ts）拿 `accessToken` → `useAuth().login(token, user)` → `navigate(location.state?.from ?? "/books", { replace: true })`；失败时把 `err.message` 显示在页面上（不是 `alert`） |
| `src/components/Layout.tsx` | 导航 + 退出按钮 + `<Outlet />` | 退出调 `useAuth().logout()` 并 `navigate("/login")`；正文只有 `<Outlet />` |
| `src/App.tsx` | 拼路由 | `<Route path="/login">` 公开；`<Route element={<ProtectedRoute />}>` → `<Route element={<Layout />}>` → `<Route path="/books">`；最后 `<Route path="*" element={<Navigate to="/books" replace />} />` 兜底 |

## 5. TODO 清单与占位约定

每个还没实现的函数里都留了一行占位语句，**行尾带 `// NOT_DONE` 标记**。把实现写好后，让**整个 `src/` 目录**里再也搜不到 `NOT_DONE`，就算做完了。

| # | 位置 | 要做什么 | 关键提示 | 对应文档 |
|:---:|---|---|---|---|
| ① | `client.ts` → `extractError()` | FastAPI 三种错误体压成一句人话 | `detail` 是字符串直接用；是数组（422）拼成 `字段: 说明`；都不是给 `HTTP xxx` | docs/07 第 2 节 |
| ② | `client.ts` → `request<T>()` | 超时 / Token 注入 / 网络错误翻译 / 401 登出 | `Bearer ` 有空格；`fetch` 不会因 404 而 reject；204 直接 `res.json()` 会报错 | docs/07 第 2 节 |
| ③ | `AuthContext.tsx` → `login()` | 写 localStorage + 改 state | `JSON.stringify` 存对象；必须用 `setToken`，不能 `token = xxx` | docs/06C ① |
| ④ | `ProtectedRoute.tsx` | 没 token 就 `<Navigate to="/login" replace state={{ from }} />` | 记得把 `Navigate` 加进 import | docs/06C ② |
| ⑤ | `BooksPage.tsx` → `useEffect` | 拉数据 | 内部再套 async 函数；**返回清理函数** `controller.abort()`；依赖 `[debouncedKeyword, refreshKey]` | docs/06C ⑥ |
| ⑥ | `BooksPage.tsx` → `handleBorrow()` | 借书 | `await borrowBook(bookId)` → `setRefreshKey(k => k + 1)`；**绝不写 `available - 1`** | docs/07 练习 3 |
| ⑦ | `BooksPage.tsx` → `<tbody>` | 渲染表格 | `books.map(...)` + `key={book.bookId}`（不用下标）；空列表一行 `colSpan={6}`；`onClick={() => handleBorrow(book.id)}` 传函数不是调用 | docs/06C 一 |

## 6. 总验收标准

- [ ] `npm run dev` 起得来，`npm run typecheck` **零报错**（占位全删干净之后）
- [ ] **登录态保持**：登录后刷新页面（F5）仍然是登录状态，不用重新登录
- [ ] **未登录跳转**：清掉 localStorage 后直接访问 `/books` → 自动跳 `/login`；登录成功后**跳回 `/books`**
- [ ] **数据自动更新**：借书成功后列表的 `available` 变成后端返回的最新值；搜索框输入时列表跟着变（有 300ms 防抖）
- [ ] 全项目搜 `fetch(`，**只有 `src/api/client.ts` 一处**；搜 `document.querySelector`，**0 处**
- [ ] 全项目搜 `available - 1`，**0 处**（前端不计算库存）
- [ ] 手动删掉 localStorage 的 token 再点任意操作 → 自动登出回到登录页，不是白屏
- [ ] 与 [纯 JS 版](../05-frontend-js/) **功能完全对等**：登录 → 列表 → 搜索 → 借书 → 退出
- [ ] 每个文件都在 300 行以内，`App.tsx` 里能一眼看出路由结构

## 7. 常见坑（React 版专属）

| 现象 | 原因 |
|---|---|
| typecheck 报「已声明但从未使用」 | 占位语句（`// NOT_DONE` 那行）还没删，或某个 import 还没用起来 |
| 刷新就掉登录 | Token 存进了 `useState` 而没进 `localStorage`；或读写用的 key 不一致 |
| 页面一渲染就狂发请求 | `useEffect` 依赖数组漏了 / 多了；或没写清理函数，`StrictMode` 下 effect 故意跑两次 |
| 输入框打不进字 | 只写了 `value` 没写 `onChange`（受控组件必须成对出现） |
| 列表报 `Cannot read properties of undefined (reading 'map')` | 后端返回的是 `{ items, total }`，要取 `data.items` |
| 借书后库存不变 | 借完没重新拉列表（只改了本地 state 是错的做法） |
| 控制台 `Unexpected token '<'` | 代理没生效，请求打到了 Vite 自己的 `index.html`（docs/07 报错对照表） |

> 📌 这个目录里的骨架**故意不给答案**。卡住超过 30 分钟，再回去看 [docs/06C](../../docs/06C-React.md) 里的参考实现 —— 那里每段代码都有。
