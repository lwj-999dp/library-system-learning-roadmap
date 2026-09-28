# 阶段 6C · React

## 📌 一句话定位

> **从「手动改 DOM」升级到「改数据，界面自己变」—— 前端思维的成年礼。**

| 项目 | 内容 |
|---|---|
| **总工时** | **60 h**（资源 41 h + 练习 19 h）→ 交付物：把里程碑 ⑧ 的纯 JS 页面用 React 重写一遍 |
| **前置 / 后置** | 前置 [6A](06A-HTML-CSS-JavaScript.md) + [6B](06B-JavaScript进阶.md)（**尤其是 Promise / 数组方法 / 模块化**）；后置 [6D · TypeScript](06D-TypeScript.md) |

---

## 🤔 React 到底解决了什么问题

**先看清楚你上一阶段写的代码有多痛：**

```javascript
// ❌ 纯 JS 版（里程碑 ⑧）：数据一变，你得手动同步所有受影响的界面
let books = [], loading = false;
function renderTable() { /* 清空 tbody，重建每一行，约 20 行 */ }
async function loadBooks() {
  loading = true; renderLoading();       // 忘了这行 → 转圈不出现
  books = await api("/api/books");
  loading = false; renderTable(); renderLoading();   // 漏掉哪个，哪个就是 bug
}
```

| # | 痛点 | 具体表现 |
|:---:|---|---|
| 1 | **每改一次数据都要手动操作 DOM** | 数据变了要记得调用所有相关的 `renderXxx()`，漏一个就是 bug |
| 2 | **状态散落各处** | `books` / `keyword` / `loading` 都是全局变量，谁都能改，出错不知道找谁 |
| 3 | **代码无法复用** | 想再用一次图书表格，只能把 HTML 字符串复制粘贴一份 |

**React 的答案只有一句话：你只管改 state（`setBooks(data)`），界面由 React 推导。** 代码里再没有 `renderXxx()`，DOM 长什么样不归你管。

```mermaid
flowchart LR
    A["改 state<br/>setBooks(data)"] --> B["React 重新调用<br/>组件函数"]
    B --> C["生成新 JSX<br/>（虚拟树）"] --> D["和上一棵对比<br/>找差异"]
    D --> E["只更新变化的<br/>真实 DOM 节点"]
    style A fill:#1d3557,color:#fff
    style E fill:#2d6a4f,color:#fff
```

> 💡 如果你跳过了 6A/6B 直接看这里，上面这段你不会有感觉。先写完里程碑 ⑧，你才知道 React 值这 60 小时。

---

## 🎯 学完能做什么

| 能力 | 具体表现 |
|---|---|
| 拆组件 | 拿到一个页面，能拆成 `Layout` + 若干业务组件 |
| 管状态 | 知道哪些状态放组件里、哪些该提到 `Context` |
| 发请求 | 用 `useEffect` 拉数据，处理加载中 / 失败 / 空状态 |
| 做路由 | 用 `react-router-dom` 配多页面，未登录访问 `/books` 自动跳 `/login`；会用 Vite 起项目、Tailwind 写样式、CLI 加 shadcn 组件 |

---

## ⏱️ 工时拆解

| # | 模块 | 内容 | 工时 | 类型 |
|:---:|---|---|:---:|:---:|
| 1 | React 官方 Learn | 核心概念 + Hooks 全部章节 | 25 h | 资源 |
| 2 | Thinking in React | 用「拆组件」的思路做一遍 | 3 h | 资源 |
| 3 | Tailwind CSS | 工具类 + v4 的 `@theme` | 6 h | 资源 |
| 4 | Vite | 项目结构、`npm run dev` 到底干了什么 | 3 h | 资源 |
| 5 | shadcn/ui | 用 CLI 添加组件（**不要手写**） | 4 h | 资源 |
| | | **资源小计** | **41 h** | |
| 6 | 练习 | React 版图书管理页面（重写里程碑 ⑧） | 19 h | 动手 |
| | | **练习 / 合计** | **19 h / 60 h** | |

---

## 📚 资源清单

| 资源 | 类型 | 语言 | 工时 | 优先级 | 链接 |
|---|---|:---:|:---:|:---:|---|
| React 官方中文文档 · Learn | 文档 | 中 | 25 h | 🔴必学 | <https://zh-hans.react.dev/learn> |
| React 官方 · Thinking in React | 文档 | 中 | 3 h | 🔴必学 | <https://zh-hans.react.dev/learn/thinking-in-react> |
| Tailwind CSS 文档 | 文档 | 英 | 6 h | 🟡推荐 | <https://tailwindcss.com/docs> |
| Vite 中文文档 | 文档 | 中 | 3 h | 🟡推荐 | <https://cn.vitejs.dev/guide/> |
| shadcn/ui 文档 | 文档 | 英 | 4 h | ⚪选学 | <https://ui.shadcn.com/docs/installation/vite> |
| 动手：React 版图书管理页面 | 动手 | — | 19 h | 🔴必学 | — |

> 官方 Learn 阅读顺序：描述 UI → 添加交互 → 状态管理 → 脱围机制（`useRef`/`useEffect`）→ Thinking in React。⚠️ **跳过「脱围机制」你会卡在数据请求上**：依赖数组和清理函数必须看懂。

---

## 🧠 必须掌握的知识点

### 一、核心概念

- [ ] JSX：JS 的语法扩展，插值用 `{}`，属性用驼峰 `className` / `htmlFor` / `onClick`，必须有一个根节点或 `<>...</>`
- [ ] 组件就是「返回 JSX 的函数」，**首字母必须大写**；`props` 父传子、**只读不能改**，`children` 是特殊 prop
- [ ] 条件渲染 `{isLoading && <Spinner />}`、三元、提前 `return null`；列表渲染 `books.map((b) => <tr key={b.id}>…)`，**`key` 用唯一业务 ID，不能用下标**
- [ ] 事件处理：传函数而不是调用（`onClick={fn}` 而不是 `fn()`）；受控表单 `value` + `onChange` 必须成对出现

### 二、Hooks

- [ ] `useState` 返回 `[值, setter]`，setter 触发重渲染
- [ ] **state 更新是异步批量处理的**：`setCount(count + 1)` 连写两次只加 1，要用 `setCount((c) => c + 1)`
- [ ] **永远不要直接改 state**：`books.push(x)` 不行，要 `setBooks([...books, x])`
- [ ] `useEffect` 的用途：同步到外部系统；依赖数组三种形态 `fn`（每次）/ `[]`（只挂载一次）/ `[id]`（挂载 + id 变化）
- [ ] **清理函数** `return () => {}`：卸载前 / 下次执行前触发，用来 `AbortController.abort()`、`clearTimeout`
- [ ] `StrictMode` 在开发模式下**故意执行两次** effect；`useContext` 跨层级传数据；`useRef` 存不触发渲染的值
- [ ] **自定义 Hook** 必须以 `use` 开头，且只能在组件 / Hook 顶层调用，不能写在条件或循环里

### 三、路由与登录态

- [ ] `<BrowserRouter>` 包裹，`<Routes>` / `<Route path element>` 配置，`path="*"` 兜底；`<Outlet />` 是嵌套路由占位出口
- [ ] `useNavigate()` 编程式跳转；`useLocation()` 拿当前路径；`<Navigate to="/login" replace />` 声明式重定向；**`ProtectedRoute` 守卫**：没 Token 就跳登录页
- [ ] **登录态放 `Context`**：`AuthProvider` + `useAuth()` 自定义 Hook，Token 存 `localStorage`
- [ ] ⚠️ **前端路由守卫只是体验优化，真正的权限判断必须在后端**

### 四、工程化（不会这些项目跑不起来）

- [ ] Vite 是什么：基于原生 ESM 的开发服务器 + 用 Rollup 打包的构建工具；目录约定 `src/pages` / `components` / `context` / `hooks` / `api`
- [ ] Tailwind v4：`@import "tailwindcss"` + `@theme` 定义设计令牌；shadcn/ui **用 `npx shadcn@latest add button` 生成，不要手写**

| 命令 | 干了什么 |
|---|---|
| `npm create vite@latest my-app -- --template react-ts` | 生成项目骨架 |
| `npm run dev` | 启动 Vite 服务器（默认 5173）：按需编译、热更新 HMR、**不写磁盘** |
| `npm run build` / `preview` | 生产构建到 `dist/`；本地预览 `dist/` |
| `npm run typecheck` | `tsc --noEmit`，只查类型不产出文件（6D 要用） |

---

## 🛠️ 动手练习

### 练习：用 React 重写里程碑 ⑧ 的纯 JS 页面（19 h）

**目标：** 功能与纯 JS 版完全对等，拆成 `LoginPage` / `BooksPage` / `Layout` / `ProtectedRoute` 四个文件。

```bash
npm create vite@latest library-ui -- --template react-ts
cd library-ui && npm install && npm install react-router-dom tailwindcss @tailwindcss/vite
npx shadcn@latest init && npx shadcn@latest add button input table
```

**目录结构：** `api/client.ts`（6B 的 `api()` 加泛型）、`components/Layout.tsx`（导航 + `<Outlet />`）、`context/AuthContext.tsx`（登录态）、`hooks/useDebounce.ts`（自定义 Hook）、`pages/{LoginPage,BooksPage}.tsx`、`routes/ProtectedRoute.tsx`（守卫）。

**Tailwind v4 的 `@theme`**（v4 没有 `tailwind.config.js`，配置直接写在 CSS 里）：

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  /* 自定义颜色，自动生成 bg-brand-500 / text-brand-700 等工具类 */
  --color-brand-50:  #f0fdf4;
  --color-brand-500: #22c55e;
  --color-brand-700: #15803d;
}
```

**① `AuthContext`（登录态 + 自定义 Hook）：**

```tsx
// src/context/AuthContext.tsx
import { createContext, useContext, useState, type ReactNode } from "react";

interface AuthState { token: string | null; login: (t: string) => void; logout: () => void }
const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  // 传函数：只在首次挂载时读一次 localStorage，刷新不掉登录
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const login = (t: string) => { localStorage.setItem("token", t); setToken(t); };
  const logout = () => { localStorage.removeItem("token"); setToken(null); };
  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>;
}
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth 必须在 <AuthProvider> 内部使用");
  return ctx;
}
```

**② `ProtectedRoute` 路由守卫：**

```tsx
// src/routes/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
export default function ProtectedRoute() {
  const { token } = useAuth();
  const location = useLocation();
  // 没 Token 就跳登录页，并用 state 记下来自哪里，登录成功后跳回去
  if (!token) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Outlet />;   // 通过校验，渲染子路由
}
```

**③ `Layout`：** 一个 `<header>` 放导航和退出按钮，`<main>` 里只写 `<Outlet />`，用 `useAuth().logout()` + `useNavigate()` 处理退出。

**④ `LoginPage`：** 两个受控 input + 一个提交函数：

```tsx
const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  try {
    const data = await api<{ access_token: string }>("/api/auth/login", {
      method: "POST", body: { username, password }, auth: false,
    });
    login(data.access_token);
    navigate(location.state?.from ?? "/books", { replace: true });  // 跳回原页面
  } catch (err) { setError(err instanceof Error ? err.message : "登录失败"); }
};
```

**⑤ 自定义 Hook `useDebounce`（输入停止 300ms 才触发）：** 用 `useEffect` + `setTimeout` 实现，**清理函数里 `clearTimeout`** 取消上一个定时器，返回防抖后的值。

**⑥ `BooksPage`（`useEffect` + `map` + `key` + 清理函数）：**

```tsx
// src/pages/BooksPage.tsx
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useDebounce } from "../hooks/useDebounce";

interface Book { id: string; title: string; author: string; stock: number; available: number }

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);   const [error, setError] = useState("");
  const debouncedKeyword = useDebounce(keyword);   // 自定义 Hook：防抖

  useEffect(() => {
    const controller = new AbortController();
    let alive = true;
    setLoading(true);
    api<Book[]>(`/api/books?keyword=${encodeURIComponent(debouncedKeyword)}`, {
      signal: controller.signal,
    })
      .then((data) => alive && setBooks(data))
      .catch((err) => {
        if (err.name === "AbortError") return;   // 被取消，不算错误
        if (alive) setError(err.message);
      })
      .finally(() => alive && setLoading(false));
    // 清理函数：卸载或关键词变化时取消上一次请求
    return () => { alive = false; controller.abort(); };
  }, [debouncedKeyword]);

  if (loading) return <p>加载中…</p>;   if (error) return <p>出错了：{error}</p>;

  return (
    <div>
      <input placeholder="搜索书名" value={keyword} onChange={(e) => setKeyword(e.target.value)} />
      <table>
        <tbody>
          {books.map((book) => (
            // key 用业务 ID，不要用数组下标
            <tr key={book.id}>
              <td>{book.title}</td>
              <td>{book.available} / {book.stock}</td>
              <td>
                <button disabled={book.available === 0}
                  onClick={() => api("/api/borrows/borrow", {
                    method: "POST", body: { bookId: book.id },
                  })}>
                  借书
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**⑦ `App.tsx`：** 把受保护路由包起来 —— `<Routes>` 里写 `<Route path="/login" element={<LoginPage />} />`，再写一个 `<Route element={<ProtectedRoute />}>`，它内部嵌 `<Route element={<Layout />}>`，最里面才是 `<Route path="/books" element={<BooksPage />} />`，最后用 `<Route path="*" element={<Navigate to="/books" replace />} />` 兜底。

---

## ✅ 验收标准

- [ ] 能用 `setBooks([...books, x])` 而不是 `books.push(x)`，并说清为什么；能说清 `useEffect` 依赖数组三种写法、清理函数的用途、`key` 为什么不能用下标
- [ ] 能说清 `Context` 适合放什么（登录态），不适合放什么（每个输入框的值）
- [ ] 组件拆分合理，**没有超过 300 行的文件**；数据变了页面自动更新，**代码里搜不到 `document.querySelector`**
- [ ] 未登录访问 `/books` 自动跳 `/login`，登录后跳回 `/books`；刷新登录态不丢
- [ ] 搜索框有防抖；退出登录后 Token 被清掉；出错显示人话而不是白屏；与里程碑 ⑧ 的纯 JS 版**功能完全对等**
- [ ] 用 `npx shadcn@latest add` 加过至少 2 个组件，**没有手写**

---

## ⚠️ 常见坑

| # | 坑 | 症状 | 怎么躲 |
|:---:|---|---|---|
| 1 | 直接改 state | `books.push(x)` 后界面不动 | `setBooks([...books, x])` |
| 2 | 连续 `setCount(count + 1)` | 只加了 1 | 用 `setCount((c) => c + 1)` |
| 3 | `useEffect` 依赖数组漏项 | 数据变了不重新请求 | 装 ESLint 的 `react-hooks` 插件 |
| 4 | 没有清理函数 | 切页面时警告 `setState on unmounted` | `AbortController` + `alive` 标志 |
| 5 | 组件名小写 / `onClick={fn()}` | 不渲染 / 一渲染就执行 | 首字母大写；传函数本身 |
| 6 | `key` 用数组下标 | 删除中间项后输入框内容串行 | 用业务 ID |
| 7 | 表单只写 `value` 不写 `onChange` | 输入框打不进字 | 受控组件必须成对出现 |
| 8 | `useEffect` 里直接写 `async` | 报错返回 Promise | 里面再套一个 `async` 函数调用 |
| 9 | 把能算出来的值也存 state | 两份真相，容易不同步 | 能推导的现算，不存 |
| 10 | 所有状态都塞进 `Context` | 一改全局重渲染，卡 | 只放真正跨层级的（登录态） |
| 11 | 手写 UI 组件 / 权限判断只做在前端 | 写了 800 行还不好看；改 `localStorage` 就能进管理页 | 用 shadcn CLI 生成；**真正的校验必须在后端** |

（另：`StrictMode` 下 effect 会**故意跑两次**，请求发两遍不是 bug —— 用清理函数处理即可。）
---

## 🧭 下一步

页面能跑通了？接力 [阶段 6D · TypeScript](06D-TypeScript.md) 给所有接口和数据模型补上类型，然后回看 [里程碑 ⑧](../milestones.md) 的三个反思题 —— 你现在应该能答了。

> 📌 **一句话收尾：** React 没让你少写代码，它让你**少写「同步界面」的代码**。这一个转变，值 60 小时。

---

[← 返回首页](../README.md) · [资源总表](../resources.md) · [里程碑](../milestones.md)
