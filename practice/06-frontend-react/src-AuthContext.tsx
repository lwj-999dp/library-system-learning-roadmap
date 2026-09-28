/**
 * ============================================================
 * 复制到 → src/context/AuthContext.tsx
 * ============================================================
 * 登录态放 Context，因为它要跨很多层组件用（Layout 的退出按钮、ProtectedRoute、
 * 各个页面）。放什么、不放什么（docs/06C 常见坑 10）：
 *   ✅ 放：登录态（token / user）—— 真正跨层级的
 *   ❌ 不放：每个输入框的值、弹窗开关 —— 那会让一改就全局重渲染
 *
 * 「刷新不掉登录」的关键在 useState 的**初始化函数**：
 *   useState(() => localStorage.getItem(TOKEN_KEY))
 * 传函数而不是传值 —— 只在首次挂载时读一次 localStorage。
 * 如果写成 useState(localStorage.getItem(...))，每次渲染都会去读一遍，逻辑会变乱。
 *
 * 还没实现的函数里留了一行占位语句，做完删掉。
 * ============================================================
 */

import { createContext, useContext, useState, type ReactNode } from "react";
import type { IUser } from "../data/types";

/** localStorage 的 key：必须和 src/api/client.ts 里的 TOKEN_KEY 完全一致 */
export const TOKEN_KEY = "token";
/** 顺便把用户信息也存一份，刷新后不用再请求一次「当前用户」接口 */
export const USER_KEY = "user";

export interface IAuthContextValue {
  token: string | null;
  user: IUser | null;
  /** 给 Layout / ProtectedRoute 用的便捷布尔值（能推导的值就不必单独存 state） */
  isLoggedIn: boolean;
  login: (token: string, user?: IUser | null) => void;
  logout: () => void;
}

/** 默认 null：配合下面的 useAuth() 就能保证「必须在 AuthProvider 内部使用」 */
const AuthContext = createContext<IAuthContextValue | null>(null);

/** 从 localStorage 恢复用户信息（localStorage 里是字符串，要 JSON.parse，且必须兜底） */
function readStoredUser(): IUser | null {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as IUser) : null;
  } catch {
    // 存进去的不是合法 JSON（手改过 / 旧版本留下的），当成没登录，别让整页白屏
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // ===== 从 localStorage 恢复登录态（这一步已经写好，读一遍就懂）=====
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<IUser | null>(() => readStoredUser());

  /**
   * 登录成功后调用：把 Token 写进 localStorage 和 state。
   *
   * TODO(AuthContext-1) 三步（参考 docs/06C 的 ① AuthContext）：
   *   ① localStorage.setItem(TOKEN_KEY, nextToken)
   *   ② 如果 nextUser 不为 null：localStorage.setItem(USER_KEY, JSON.stringify(nextUser))
   *      —— localStorage 只能存字符串，存对象必须 JSON.stringify（docs/06B 常见坑 8）
   *   ③ setToken(nextToken); setUser(nextUser)
   *      —— ❗不要写 token = nextToken：state 只能通过 setter 改，否则界面不会重渲染
   */
  const login = (nextToken: string, nextUser: IUser | null = null): void => {
    // 占位：做完上面三步后删掉这一行
    console.warn(`[NOT_DONE] AuthContext.login() 还没实现（收到 token：${nextToken ? "有" : "无"}）`, nextUser); // NOT_DONE
  };

  /** 退出登录：本地清干净 + state 置空。这个已经写好，照着 login 抄思路即可 */
  const logout = (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, isLoggedIn: Boolean(token), login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/** 自定义 Hook：组件里用 const { token, login } = useAuth(); */
export function useAuth(): IAuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth() 必须在 <AuthProvider> 内部使用");
  return ctx;
}
