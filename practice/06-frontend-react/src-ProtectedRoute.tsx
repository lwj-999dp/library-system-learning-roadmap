/**
 * ============================================================
 * 复制到 → src/routes/ProtectedRoute.tsx
 * ============================================================
 * 路由守卫：没登录就不许看 /books、/borrows 这些页面。
 *
 * ⚠️ 先记住一句话（docs/06C 三 · 路由与登录态）：
 *    前端路由守卫只是**体验优化**，让人别看到白屏；
 *    真正的权限判断必须在后端（改一下 localStorage 就能骗过前端）。
 *
 * 用法（App.tsx 里）：
 *   <Route element={<ProtectedRoute />}>
 *     <Route element={<Layout />}>
 *       <Route path="/books" element={<BooksPage />} />
 *     </Route>
 *   </Route>
 * 守卫本身不渲染页面，只负责「放行 / 踢回登录页」，放行时用 <Outlet /> 占位。
 * ============================================================
 */

// 提示：实现 TODO 时需要用到 Navigate，记得把它加进下面这行 import（现在加了会被 typecheck 报「未使用」）
import { Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const { token } = useAuth();
  const location = useLocation();

  /*
   * ===== TODO(ProtectedRoute) 把下面这行占位换成真正的守卫 =====
   *
   *   没 token → 声明式重定向踢回登录页，并把「从哪来的」记在 state 里，
   *              这样登录成功后能跳回用户原本想去的页面：
   *
   *     if (!token) {
   *       return <Navigate to="/login" replace state={{ from: location.pathname }} />;
   *     }
   *     return <Outlet />;
   *
   *   三个细节别漏：
   *     · replace：别在历史记录里留一条 /books，否则用户点「后退」会来回弹
   *     · state={{ from: location.pathname }}：登录页用 location.state?.from 跳回去
   *     · 有 token 才渲染 <Outlet /> —— Outlet 是嵌套路由的「出口」
   *
   *   做完后删掉下面这行占位。
   */
  console.warn(
    `[NOT_DONE] ProtectedRoute 还没实现登录校验，当前一律放行（token：${token ? "有" : "无"}，位置：${location.pathname}）`,
  ); // NOT_DONE

  return <Outlet />;
}
