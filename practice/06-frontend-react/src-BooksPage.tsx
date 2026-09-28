/**
 * ============================================================
 * 复制到 → src/pages/BooksPage.tsx
 * ============================================================
 * React 版图书页：搜索 + 表格 + 借书。和纯 JS 版功能完全对等，
 * 但代码里**没有任何 document.querySelector** —— 你只管改 state，界面由 React 推导。
 *
 * 还没实现的函数里留了一行占位语句，做完删掉。
 * ============================================================
 */

import { useEffect, useState } from "react";
import { borrowBook, listBooks } from "../api/client";
import { useDebounce } from "../hooks/useDebounce";
import type { IBook } from "../data/types";

export default function BooksPage() {
  const [books, setBooks] = useState<IBook[]>([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  /** 借书成功后 +1，让下面的 useEffect 重新跑一次 —— 比手动调 loadBooks() 更 React */
  const [refreshKey, setRefreshKey] = useState(0);
  /** 防抖：输入停止 300ms 才真正去请求（useDebounce 要你自己写，见 README 第 4 节） */
  const debouncedKeyword = useDebounce(keyword.trim(), 300);

  useEffect(() => {
    /*
     * ===== TODO(BooksPage-1) 拉数据（参考 docs/06C 的 ⑥ BooksPage）=====
     *   ① 不能在 useEffect 里直接写 async 函数（返回 Promise，React 会报错）；
     *      要么在内部定义 async 函数再调用，要么用 .then() 链
     *   ② 请求前 setLoading(true)、setError("")；拿到数据 setBooks(data)
     *      —— ❗不是 books.push(...)，state 必须换新引用（docs/06C 常见坑 1）
     *   ③ 后端若返回分页对象 { items, total }，要取 data.items，
     *      直接 map 会报 "Cannot read properties of undefined (reading 'map')"
     *   ④ 一定要返回清理函数，否则快速输入时旧请求的结果会覆盖新结果：
     *        const controller = new AbortController();
     *        listBooks({ keyword: debouncedKeyword, signal: controller.signal })
     *        return () => controller.abort();
     *      被取消时（err.name === "AbortError"）直接 return，不要当错误处理
     *   ⑤ 依赖数组已经是 [debouncedKeyword, refreshKey]：关键词变了、或借书后都要重新拉
     */

    // 占位：做完上面五步后删掉这一行
    void [setLoading, setError, setBooks]; // NOT_DONE
  }, [debouncedKeyword, refreshKey]);

  /*
   * ===== TODO(BooksPage-2) 借书 =====
   *   ① await borrowBook(bookId)    ← client.ts 里已经写好了这个函数
   *   ② 成功后：setRefreshKey((key) => key + 1) 触发重新拉列表
   *      —— 用后端返回的最新 available，⚠️ 绝不写 setBooks(books.map(... available - 1))
   *   ③ 失败：setError(err instanceof Error ? err.message : "借书失败")
   *      —— err.message 是 client.ts 提取好的中文，别自己再包一层
   *   ④ 防连点：按钮上加 disabled={loading} 或用一个 borrowing 状态标记
   */
  async function handleBorrow(bookId: string): Promise<void> {
    // 占位：做完上面四步后删掉下面两行
    console.warn(`[NOT_DONE] handleBorrow() 还没实现，bookId = ${bookId}`); // NOT_DONE
    setRefreshKey((key) => key); // NOT_DONE
  }

  // ===== 脚手架占位区（TODO 全部做完后，把这一行删掉）=====
  // 这里列出的符号，正是「做完之后应该被你的代码用起来」的东西；
  // 现在只是为了让 `npm run typecheck` 在 TODO 未完成时也不报「已声明但从未使用」。
  void [handleBorrow, listBooks, borrowBook]; // NOT_DONE

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-xl font-semibold">图书列表</h2>

        {/* 受控输入：value + onChange 必须成对出现，只写 value 就打不进字（docs/06C 常见坑 7） */}
        <input
          type="search"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          placeholder="搜索书名 / 作者 / ISBN"
          className="rounded border border-slate-300 px-3 py-1.5"
        />

        {/* 把它显示出来，你才能直观看到「防抖」到底防住了什么 */}
        <span className="text-sm text-slate-500">当前搜索：{debouncedKeyword || "全部"}</span>
      </div>

      {loading && <p className="text-slate-500">加载中…</p>}
      {error && <p className="text-red-600">出错了：{error}</p>}

      <div className="overflow-x-auto rounded border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-2 text-left">ISBN</th>
              <th className="p-2 text-left">书名</th>
              <th className="p-2 text-left">作者</th>
              <th className="p-2 text-left">库存</th>
              <th className="p-2 text-left">状态</th>
              <th className="p-2 text-left">操作</th>
            </tr>
          </thead>
          <tbody>
            {/*
              ===== TODO(BooksPage-3) 渲染表格 =====
              把下面这段占位换成真正的渲染，要求：
                · 空列表（books.length === 0）时渲染一行：<tr><td colSpan={6}>没有找到图书</td></tr>
                · 用 books.map((book) => …) 渲染每一行
                  —— key 用 book.bookId，**不要用数组下标**（删中间项会串行，docs/06C 常见坑 6）
                · 书名 / 作者 / ISBN 直接用 JSX 插值 {book.title}
                  —— React 会自动转义，天然防 XSS，不需要手动 textContent
                · 库存格显示 {book.available} / {book.stock}
                · 状态格：{book.available > 0 ? "可借" : "已借完"}
                · 操作格：<button disabled={book.available === 0} onClick={() => handleBorrow(book.bookId)}>借书</button>
                  —— onClick 传的是**函数本身**；写成 onClick={handleBorrow(book.bookId)} 会一渲染就执行
            */}
            {books.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-4 text-center text-slate-500">
                  TODO：还没有数据 —— 先做完 TODO(BooksPage-1) 的「拉数据」
                </td>
              </tr>
            ) : (
              <tr>
                <td colSpan={6} className="p-4 text-center text-slate-500">
                  TODO：已拿到 {books.length} 本书，但还没渲染成表格行 —— 见 TODO(BooksPage-3)
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <p className="text-sm text-slate-500">
        提示：库存和状态只信后端返回值，前端不做任何计算（docs/07 第 1 节）。
      </p>
    </section>
  );
}
