/**
 * ============================================================
 * 复制到 → src/api/client.ts
 * ============================================================
 * 全项目**唯一的网络出口**。规矩只有一条：
 *   页面组件里禁止出现 fetch —— Token 注入、超时、错误提取、401 登出这四件事
 *   只写一遍，改也只改一处（docs/07-前后端联调.md 第 2 节）。
 *
 * 还没实现的函数里都留了一行占位语句（行尾带标记），做完就删掉它。
 * 全部删完 + 补齐 README 里列的组件后，`npm run typecheck` 应该是干净的。
 * ============================================================
 */

import type { IBorrow, IBook, IBookQuery, ILoginRequest, ILoginResponse } from "../data/types";

/**
 * 后端地址。
 * · 默认 "/api"：配合 vite.config.ts 的代理（开发环境首选，永远不会有 CORS 问题）
 * · 想直连后端就在项目根目录建 .env.local，写 VITE_API_BASE_URL=http://127.0.0.1:8000/api
 * ⚠️ 因为这里已经带了 "/api"，下面所有 path 都不要再写 "/api"。
 */
export const API_BASE: string = import.meta.env.VITE_API_BASE_URL ?? "/api";

/** localStorage 里存 Token 的 key —— 读（本文件）和写（AuthContext）必须一致 */
export const TOKEN_KEY = "token";

/** 超时时间：后端卡死时不要让用户转到天荒地老（导出只是方便调试，业务代码不用管） */
export const TIMEOUT_MS = 10_000;

/**
 * 统一错误类型：调用方 catch 到的永远是它，err.message 已经是人话。
 * ⚠️ 这里**故意不用** TypeScript 的「构造函数参数属性」写法
 *    （constructor(public status: number, ...)），因为新版 Vite 模板开了
 *    `erasableSyntaxOnly`，那种语法会直接报错。老老实实声明字段 + 赋值最稳。
 */
export class ApiError extends Error {
  /** 0 表示「请求根本没发出去」或超时；其余是 HTTP 状态码 */
  readonly status: number;
  /** 后端原始响应体，调试时才需要 */
  readonly data: unknown;

  constructor(status: number, message: string, data: unknown = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/** request() 的入参：在原生 RequestInit 上把 body 换成「任意对象」 */
export interface IRequestOptions extends Omit<RequestInit, "body"> {
  /** 会自动 JSON.stringify，页面里不用管 */
  body?: unknown;
  /** false = 不带 Token（只有登录接口这么用），默认 true */
  auth?: boolean;
}

/**
 * 把后端各种形态的错误统一抽成一句人话。
 *
 * TODO(extractError) 三种形态都要覆盖（见 docs/07 第 2 节的 extractError）：
 *   ① body.detail 是字符串 → 直接返回它（400 业务错误，比如「库存不足」）
 *   ② body.detail 是数组   → 这是 FastAPI 的 422 校验错误，每一项长这样
 *                            { loc: ["body", "stock"], msg: "Input should be a valid integer" }
 *                            拼成 "stock: Input should be a valid integer"，
 *                            多项用 "；" 连接。loc 取最后一项（e.loc.at(-1)）最好读。
 *   ③ 都不是 → 返回 `HTTP ${res.status}`
 *
 * 提示：res.json() 在响应体不是 JSON 时会 reject，所以要 .catch(() => null)；
 *      别忘了整个 res.json() 是异步的，要 await。
 */
export async function extractError(res: Response): Promise<string> {
  return `HTTP ${res.status}`; // NOT_DONE（占位：把上面三种形态实现掉，再删掉这一行）
}

/**
 * 唯一的请求函数。所有业务接口都走它。
 *
 * TODO(request) 按四步写（参考实现见 docs/07 第 2 节）：
 *
 *   (1) 超时控制
 *       · const controller = new AbortController();
 *       · const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
 *       · 把 controller.signal 传给 fetch；在 finally 里 clearTimeout(timer)
 *
 *   (2) 请求头
 *       · 有 body 时才加 "Content-Type": "application/json"（GET 不该带）
 *       · options.auth !== false 且有 Token 时加 Authorization: `Bearer ${token}`
 *         —— "Bearer " 后面有一个空格，漏了后端一定 401
 *       · 允许 options.headers 覆盖默认头
 *
 *   (3) 发请求 + 把「网络层错误」翻译成人话
 *       · fetch 不会因为 404 / 500 而 reject，只有请求根本没发出去才 reject
 *       · AbortError：超时 → new ApiError(0, "请求超时：后端没启动或卡死")
 *         （如果是外面传进来的 signal 主动取消，原样抛出，不要包装成错误提示）
 *       · 其它异常 → new ApiError(0, "无法连接服务器（Failed to fetch）")
 *
 *   (4) 状态码分支
 *       · res.status === 401 → localStorage.removeItem(TOKEN_KEY)
 *                              + 不在 /login 时 location.href = "/login"
 *                              + throw new ApiError(401, "登录已过期，请重新登录")
 *       · !res.ok → throw new ApiError(res.status, await extractError(res))
 *       · res.status === 204 → 返回 undefined（DELETE 接口常用，直接 res.json() 会报错）
 *       · 其余 → 返回 await res.json()
 *
 * @example
 *   const books = await request<IBook[]>("/books");
 *   const res = await request<ILoginResponse>("/auth/login", { method: "POST", body: payload, auth: false });
 */
export async function request<T>(path: string, options: IRequestOptions = {}): Promise<T> {
  // 步骤见上面 TODO(request) 的 (1)~(4)
  throw new ApiError(0, `request() 还没实现：${options.method ?? "GET"} ${API_BASE}${path}`, null); // NOT_DONE
}

/* ============================================================
 * 业务接口封装：页面只 import 这些函数，不自己拼 URL、不自己写 fetch。
 * 下面这几个是**完整版**，照抄即可 —— 它们顺便演示了 request() 该怎么调。
 * （正式项目里可以按 docs/07 第 3 节把它们挪到 src/data/books.ts，
 *   client.ts 只留 request()；本脚手架先放在一起，少一个文件少一个坑。）
 * ============================================================ */

/** 登录：auth: false —— 这时候还没有 Token，带上反而出错 */
export function login(payload: ILoginRequest): Promise<ILoginResponse> {
  return request<ILoginResponse>("/auth/login", { method: "POST", body: payload, auth: false });
}

/** 图书列表：URLSearchParams 会自动帮你转义中文和特殊字符；signal 用来取消上一次请求 */
export function listBooks({ keyword = "", page = 1, pageSize = 10, signal }: IBookQuery = {}): Promise<IBook[]> {
  const query = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
  if (keyword.trim()) query.set("keyword", keyword.trim());
  return request<IBook[]>(`/books?${query.toString()}`, { signal });
}

/** 借书。⚠️ 不要在前端算库存，借完重新调 listBooks() 拿后端的最新数字 */
export function borrowBook(bookId: string): Promise<IBorrow> {
  return request<IBorrow>("/borrows/borrow", { method: "POST", body: { bookId } });
}
