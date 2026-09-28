/**
 * ============================================================
 * 复制到 → src/data/types.ts
 * ============================================================
 * 前后端的「数据契约」。这个文件是**完整版**，不用你填空 ——
 * 类型定义是契约，猜错了后面全是 undefined，所以直接给你。
 *
 * 三条铁律（见 docs/07-前后端联调.md 第 3 节）：
 *   1. 字段名必须和后端返回的 JSON 一模一样，前端不做「book_id → bookId」的翻译；
 *   2. 后端算好的东西（库存 available、借阅状态 status）前端只用不算；
 *   3. 后端改字段名时，先改这个文件，TypeScript 会把所有受影响的地方报出来。
 *
 * ⚠️ 如果后端返回的是 snake_case（book_id）、或者登录返回的是 access_token，
 *    请**改这个文件**去对齐后端，而不是在页面里写转换代码。
 * ============================================================
 */

/** 分页响应的通用包装：后端返回 { items, total, page, pageSize } 时用它 */
export interface IPage<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

/**
 * 后端统一响应包装。
 * 如果后端直接返回裸数据（比如 GET /books 直接给数组），这个类型用不上，
 * 把 `request<T>` 的返回值改成 T 即可 —— 二选一，别混着用。
 */
export interface IApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

/** 图书 */
export interface IBook {
  bookId: string;
  title: string;
  author: string;
  isbn: string;
  publisher?: string | null;
  stock: number;
  /** 可借数量：**只由后端计算**，前端只负责显示 */
  available: number;
  isDeleted: boolean;
}

/** 读者 */
export interface IReader {
  readerId: string;
  name: string;
  cardNo: string;
  phone?: string | null;
  email?: string | null;
  /** 最多可借本数，由后端按读者类型给定 */
  maxBorrow: number;
  status: ReaderStatus;
  createdAt: string;
}

export type ReaderStatus = "active" | "frozen";

/** 借阅记录：status 由后端根据 returnDate / dueDate 推导，前端不要自己算 */
export interface IBorrow {
  borrowId: number;
  bookId: string;
  readerId: string;
  /** ISO 8601 字符串，例如 "2025-03-01T10:00:00" */
  borrowDate: string;
  dueDate: string;
  /** 未归还时是 null */
  returnDate: string | null;
  status: BorrowStatus;
}

export type BorrowStatus = "borrowing" | "overdue" | "returned";

export type UserRole = "admin" | "librarian" | "reader";

/** 登录用户 */
export interface IUser {
  userId: number;
  username: string;
  name: string;
  role: UserRole;
}

/** POST /api/auth/login 的请求体 */
export interface ILoginRequest {
  username: string;
  password: string;
}

/**
 * POST /api/auth/login 的响应体。
 * 字段名以你后端的实际输出为准：docs/06C 里写的是 access_token，
 * docs/07 里写的是 accessToken —— 只能有一个是对的，去 FastAPI 的
 * /docs 里点一次就能看到真实字段，然后改这里。
 */
export interface ILoginResponse {
  accessToken: string;
  tokenType: string;
  user: IUser;
}

/** POST /api/borrows/borrow 的请求体 */
export interface IBorrowRequest {
  bookId: string;
}

/** 图书列表查询参数 */
export interface IBookQuery {
  keyword?: string;
  page?: number;
  pageSize?: number;
  /** 用来取消请求：组件卸载 / 关键词变化时 abort 掉上一次（docs/06C ⑥ 的清理函数） */
  signal?: AbortSignal;
}
