/**
 * ============================================================
 * 阶段 6 · 纯 JS 版图书管理前端 —— 练习脚手架（自带自测）
 * ------------------------------------------------------------
 * 对应文档：
 *   docs/06A-HTML-CSS-JavaScript.md  （DOM、事件委托、submit + preventDefault）
 *   docs/06B-JavaScript进阶.md        （api() 封装、fetch、async/await、localStorage）
 *   docs/07-前后端联调.md             （统一网络出口、401、库存只归后端算）
 *
 * 怎么用：
 *   1. 双击 index.html 就能打开（零依赖、无框架、不需要 npm install）
 *   2. 按 F12 → Console，输入 runSelfCheck() 看还有哪几个 TODO 没做
 *   3. 从上往下把 5 个 TODO 做完，每做完一个就再跑一次 runSelfCheck()
 *
 * 判断「做完了没有」的规则：
 *   每个还没实现的函数里都留了一行占位语句（行尾带一个标记注释）。
 *   把实现写好后，删掉那一行 —— 再跑自检就会变绿。
 *
 * 说明：本文件被 index.html 以「普通脚本」引入（不是 type="module"），
 *      所以 file:// 双击打开也能跑，不会遇到模块化的 CORS 报错。
 * ============================================================
 */

"use strict";

/* ============================================================
 * 0. 配置区
 * ============================================================ */

/** true = 走本地假数据（默认，后端还没写好也能先练前端）；false = 请求真实后端 */
const USE_MOCK = true;

/** 真实后端地址，就是 uvicorn 默认跑的那个 */
const API_BASE = "http://127.0.0.1:8000";

/** localStorage 里存 Token 用的 key —— api() 读、handleLogin() 写，必须是同一个 */
const TOKEN_KEY = "token";

/** 请求超时（毫秒） */
const REQUEST_TIMEOUT_MS = 10000;

/* ============================================================
 * 1. Mock 数据层（已经写好，不需要你改）
 *    USE_MOCK = true 时 api() 会把请求转到这里。
 *    它的行为尽量模仿 FastAPI：登录发 Token、借书真的会减库存、库存为 0 会报中文错误。
 * ============================================================ */

const MOCK_ACCOUNT = { username: "admin", password: "123456", name: "管理员" };

/** 假数据字段名与后端 JSON 完全一致（camelCase），见 docs/07 第 3 节 */
let mockBooks = [
  { bookId: "B001", title: "JavaScript 高级程序设计", author: "Matt Frisbie", isbn: "9787115428028", stock: 5, available: 3, isDeleted: false },
  { bookId: "B002", title: "深入理解计算机系统", author: "Randal E. Bryant", isbn: "9787115545381", stock: 2, available: 0, isDeleted: false },
  { bookId: "B003", title: "流畅的 Python", author: "Luciano Ramalho", isbn: "9787115462671", stock: 4, available: 4, isDeleted: false },
  { bookId: "B004", title: "MySQL 技术内幕", author: "姜承尧", isbn: "9787111421993", stock: 3, available: 1, isDeleted: false },
  { bookId: "B005", title: "FastAPI Web 开发实战", author: "Bill Lubanovic", isbn: "9787111712345", stock: 6, available: 6, isDeleted: false },
  { bookId: "B006", title: "你不知道的 JavaScript", author: "Kyle Simpson", isbn: "9787115426499", stock: 2, available: 2, isDeleted: false },
];

/** mock 模式下发出去的假 Token */
let mockToken = null;
let mockBorrowSeq = 0;

/** 统一错误类型：页面里只要拿到 err.message 就能直接显示给人看 */
class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/** 假装网络有延迟，这样 loading 状态才有意义 */
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * 假后端：入参出参尽量和真实 FastAPI 一致。
 * @param {string} path 例如 "/api/books?keyword=js"
 * @param {{ method?: string, body?: any }} [options]
 */
async function mockApi(path, { method = "GET", body } = {}) {
  await delay(200);
  const [rawPath, rawQuery = ""] = path.split("?");
  const query = new URLSearchParams(rawQuery);

  // ---- 登录：不需要 Token ----
  if (rawPath === "/api/auth/login" && method === "POST") {
    const { username, password } = body ?? {};
    if (username !== MOCK_ACCOUNT.username || password !== MOCK_ACCOUNT.password) {
      throw new ApiError("用户名或密码错误（mock 账号：admin / 123456）", 401, null);
    }
    mockToken = `mock-token-${Date.now()}`;
    return { accessToken: mockToken, tokenType: "bearer", user: { username: MOCK_ACCOUNT.username, name: MOCK_ACCOUNT.name } };
  }

  // ---- 下面的接口都要求已登录（模拟后端的 401） ----
  if (!mockToken) {
    throw new ApiError("登录已过期，请重新登录", 401, null);
  }

  // ---- 图书列表 ----
  if (rawPath === "/api/books" && method === "GET") {
    const keyword = (query.get("keyword") ?? "").trim().toLowerCase();
    const list = mockBooks.filter((b) => !b.isDeleted);
    const hit = keyword
      ? list.filter((b) => [b.title, b.author, b.isbn].some((field) => field.toLowerCase().includes(keyword)))
      : list;
    // 返回副本：外面拿到的对象改不动 mock 内部数据
    return hit.map((b) => ({ ...b }));
  }

  // ---- 借书：库存只有「后端」能改 ----
  if (rawPath === "/api/borrows/borrow" && method === "POST") {
    const book = mockBooks.find((b) => b.bookId === body?.bookId);
    if (!book) throw new ApiError("图书不存在", 404, null);
    if (book.available <= 0) throw new ApiError(`《${book.title}》已全部借出，暂时借不了`, 400, null);
    book.available -= 1; // 真实项目里这一步在 MySQL 事务里做（docs/07 第 7 节时序图）
    mockBorrowSeq += 1;
    return { borrowId: mockBorrowSeq, bookId: book.bookId, status: "borrowing" };
  }

  throw new ApiError(`mock 没实现这个接口：${method} ${rawPath}`, 404, null);
}

/* ============================================================
 * 2. 全局状态与 DOM 引用
 *    「唯一数据源」思想：数据变了就调一次 render，界面永远由数据推导。
 * ============================================================ */

const state = {
  books: [], // 最近一次从「后端」拿到的完整列表
  keyword: "", // 搜索框当前关键词
  user: null, // 当前登录用户
  loading: false,
};

const el = {
  loginPage: document.getElementById("login-page"),
  booksPage: document.getElementById("books-page"),
  loginForm: document.getElementById("login-form"),
  loginSubmit: document.getElementById("login-submit"),
  loginError: document.getElementById("login-error"),
  mockHint: document.getElementById("mock-hint"),
  skipLoginBtn: document.getElementById("skip-login-btn"),
  searchInput: document.getElementById("search-input"),
  refreshBtn: document.getElementById("refresh-btn"),
  bookTbody: document.getElementById("book-tbody"),
  loading: document.getElementById("loading"),
  listError: document.getElementById("list-error"),
  logoutBtn: document.getElementById("logout-btn"),
  currentUser: document.getElementById("current-user"),
  modeBadge: document.getElementById("mode-badge"),
  selfCheckBtn: document.getElementById("self-check-btn"),
};

/* ============================================================
 * 3. 小工具（已经写好）
 * ============================================================ */

/** 右上角弹一条提示：toast("借阅成功") / toast("库存不足", "error") */
function toast(message, type = "info") {
  const box = document.getElementById("toast-container");
  if (!box) return;
  const item = document.createElement("div");
  item.className = `toast toast-${type}`;
  item.textContent = message; // 用户可见文本一律 textContent，防 XSS（docs/06A 必会点）
  box.appendChild(item);
  setTimeout(() => item.remove(), 3000);
}

/** 切换「登录页 / 图书页」两个 section */
function showPage(name) {
  const goBooks = name === "books";
  el.loginPage.hidden = goBooks;
  el.booksPage.hidden = !goBooks;
  el.logoutBtn.hidden = !goBooks;
}

/** 转圈提示的开关 */
function setLoading(value) {
  state.loading = value;
  el.loading.hidden = !value;
}

/* ============================================================
 * 4. ★ TODO ① 统一请求封装 ★
 *    目标：全项目「唯一的网络出口」。页面里永远不直接写 fetch。
 *
 *    实现步骤（完整参考实现在 docs/06B-JavaScript进阶.md 的「动手练习」一节，
 *    以及 docs/07-前后端联调.md 第 2 节。先自己写 30 分钟再看）：
 *
 *    (1) 准备请求头与请求体
 *        · const token = localStorage.getItem(TOKEN_KEY)  ← 用本文件顶部的常量
 *        · 只有带 body 时才加 "Content-Type": "application/json"（GET 不该带）
 *        · options.auth !== false 且 token 存在时加 Authorization: `Bearer ${token}`
 *          —— "Bearer " 后面有一个空格，漏了后端一定返回 401（docs/07 报错对照表）
 *        · body 必须 JSON.stringify()，直接传对象后端会收到 [object Object]
 *
 *    (2) 用 fetch 发请求，并把「网络层错误」翻译成人话
 *        · 地址是 `${API_BASE}${path}`；method / headers / body 都传进去
 *        · fetch 只有在「请求根本没发出去」时才 reject，此时抛
 *          new ApiError("网络异常：后端没启动或地址写错", 0, null)
 *        · 用 AbortController + setTimeout 做超时（REQUEST_TIMEOUT_MS），
 *          在 finally 里 clearTimeout，别让定时器泄漏
 *        · 如果是外部传进来的 signal 被取消（err.name === "AbortError"），
 *          把错误原样抛出，不要包装成「网络异常」
 *
 *    (3) 把响应统一处理成「数据」或「人话错误」
 *        · res.status === 401 → localStorage.removeItem(TOKEN_KEY) + 跳回登录页 + 抛 ApiError
 *        · !res.ok → 抛 ApiError(统一错误信息, res.status, data)
 *        · res.status === 204 或响应体为空 → 返回 null；成功 → 返回解析后的 JSON
 *        · 「统一错误信息」单独写个小函数 extractMessage(data, status)：
 *            detail 是字符串 → 直接用（业务错误）
 *            detail 是数组   → 拼成 "字段: 说明；字段: 说明"（422 校验错误）
 *            两者都不是     → `请求失败（HTTP ${status}）`
 *        · 记住：fetch 不会因为 404 / 500 而 reject，必须自己判断 res.ok
 *
 *    ⚠️ 进阶思考（做完再看）：登录密码错误时后端也返回 401。
 *       如果 401 分支一律把消息覆盖成「登录已过期」，用户就看不到「用户名或密码错误」。
 *       想更友好就用 options.auth === false 或 path 判断，区分「登录失败」和「Token 过期」。
 * ============================================================ */

/**
 * 发起一次请求。mock 模式下自动转发给 mockApi()（已写好，不用管）。
 *
 * @param {string} path 以 / 开头的接口路径，例如 "/api/books"
 * @param {{ method?: string, body?: any, headers?: object, auth?: boolean, signal?: AbortSignal }} [options]
 *        auth=false 表示不带 Token（只有登录接口这么用）
 * @returns {Promise<any>} 已解析好的响应数据
 * @throws {ApiError} 无论网络错误还是业务错误，都抛出 message 是人话的 ApiError
 */
async function api(path, options = {}) {
  // ---- mock 分支：已写好，不要改 ----
  if (USE_MOCK) return mockApi(path, options);

  // 在这里写真实后端分支，步骤见本节顶部注释的 (1)~(3)
  throw new ApiError("api() 的真实后端分支还没实现，见第 4 节顶部注释的 (1)~(3)", 0, null); // NOT_DONE
}

/* ============================================================
 * 5. ★ TODO ② 渲染图书表格 ★
 *    这是本练习最重要的一次「数据 → 界面」练习。
 *
 *    按三步写（提示：docs/06A-HTML-CSS-JavaScript.md 第四节「DOM 与事件」）：
 *
 *    (1) 先清空上一次的内容（tbody.textContent = "" 或 innerHTML = ""）。
 *        忘了这行，每次渲染都会把旧行堆在后面 —— 最常见的 bug。
 *
 *    (2) 没有数据时（books.length === 0）显示一行占位：
 *        <tr><td colspan="6" class="empty">没有找到图书</td></tr>
 *        colspan 要等于表头的 6 列，否则那行只占一格，很难看。
 *
 *    (3) 有数据时循环渲染，每行 6 格：ISBN / 书名 / 作者 / 库存 / 状态 / 操作
 *        · 用 document.createElement + textContent 填文本，
 *          不要用 innerHTML 拼用户数据（XSS 风险）
 *        · 库存格显示 `${book.available} / ${book.stock}`
 *        · 状态格：available > 0 → <span class="tag tag-ok">可借</span>
 *                   available === 0 → <span class="tag tag-out">已借完</span>
 *        · 操作格放一个按钮，属性必须和下面的事件委托对上（这是约定，别改名字）：
 *            button.className = "btn-borrow"
 *            button.dataset.action = "borrow"   → HTML 上的 data-action="borrow"
 *            button.dataset.id = book.bookId    → HTML 上的 data-id="B001"
 *            button.textContent = "借书"
 *            available === 0 时 button.disabled = true
 *        · 最后 tbody.appendChild(tr)
 *
 *    为什么按钮不用一个个绑事件？因为 bindEvents() 里用了「事件委托」：
 *    监听器只绑在 tbody 上，靠 event.target.closest('[data-action="borrow"]') 找人。
 * ============================================================ */

/**
 * 把图书数组画进 <tbody>。
 *
 * @param {Array<{bookId:string,title:string,author:string,isbn:string,stock:number,available:number}>} books
 */
function renderBooks(books) {
  const tbody = el.bookTbody;
  if (!tbody) return;

  // 按本节顶部 (1)~(3) 写
  tbody.innerHTML = '<tr><td colspan="6" class="empty">TODO：renderBooks() 还没实现（见 app.js 第 5 节）</td></tr>'; // NOT_DONE
}

/* ============================================================
 * 6. ★ TODO ③ 实时搜索过滤 ★
 *    提示：docs/06B-JavaScript进阶.md 第二节「数组方法」
 *
 *    要求（纯函数，不改 state.books）：
 *    (1) 关键词先规范化：keyword.trim().toLowerCase()
 *    (2) 空关键词直接返回全部
 *    (3) 用 state.books.filter(...) 返回新数组；判断命中用 .includes()
 *    (4) 书名 / 作者 / ISBN 任意一个命中就算命中
 *        （用 some 或 || 都行；字段也要 toLowerCase()，
 *          否则搜 "javascript" 匹配不到 "JavaScript"）
 *    (5) 不要用 sort()，也不要 push 回 state.books —— 它返回的是新数组，不是原地改
 * ============================================================ */

/**
 * 按关键词过滤 state.books，返回新数组。
 *
 * @param {string} keyword
 * @returns {Array} 过滤后的图书数组
 */
function filterBooks(keyword) {
  // 按本节顶部 (1)~(5) 写
  return state.books; // NOT_DONE（占位：等价于「不过滤」，做完删掉这一行）
}

/* ============================================================
 * 7. ★ TODO ④ 登录 ★
 *    骨架已经给好：读表单、禁用按钮防连点、错误显示在 #login-error。
 *    提示：docs/06B-JavaScript进阶.md 的 auth.js 一节
 *
 *    (1) 先做前端基本校验
 *        · username 或 password 为空 → 写提示到 el.loginError、toast 一下，然后 return
 *          （别为一个空表单浪费一次请求；return 后 finally 会恢复按钮）
 *
 *    (2) 调登录接口
 *        · await api("/api/auth/login", { method: "POST", body: { username, password }, auth: false })
 *        · auth: false 一定要写：登录时还没有 Token，带上反而出错
 *        · 拿到的是 { accessToken, tokenType, user }（字段名 camelCase，与后端一致）
 *
 *    (3) 保存登录态
 *        · localStorage.setItem(TOKEN_KEY, data.accessToken)
 *          只认这一个 key；读它的地方是 api() 里的 localStorage.getItem(TOKEN_KEY)
 *        · localStorage 只能存字符串，存对象必须 JSON.stringify（docs/06B 常见坑 8）
 *
 *    (4) 成功后的收尾
 *        · state.user = data.user；el.currentUser.textContent = 用户名
 *        · toast(`欢迎回来，${...}`, "success")
 *        · await enterBooksPage()  ← 这个函数已经写好，直接调（切页面 + 拉列表）
 *
 *    (5) 失败处理
 *        · catch 里把 err.message 写进 el.loginError，并 toast(err.message, "error")
 *        · api() 抛出的 message 已经是人话，直接显示，别自己拼一句「登录失败」把信息盖掉
 * ============================================================ */

/**
 * 登录表单的 submit 处理函数（已在 bindEvents() 里绑定）。
 * @param {SubmitEvent} event
 */
async function handleLogin(event) {
  event.preventDefault(); // 不加这行浏览器会刷新页面，数据全没（docs/06A 常见坑 4）

  const form = event.target;
  const username = form.username.value.trim();
  const password = form.password.value;

  el.loginError.textContent = "";
  el.loginSubmit.disabled = true;
  el.loginSubmit.textContent = "登录中…";

  try {
    // 按本节顶部 (1)~(5) 写
    throw new ApiError("handleLogin() 还没实现，见第 7 节顶部注释的 (1)~(5)", 0, null); // NOT_DONE
  } catch (err) {
    el.loginError.textContent = err?.message ?? "登录失败";
    toast(err?.message ?? "登录失败", "error");
  } finally {
    el.loginSubmit.disabled = false;
    el.loginSubmit.textContent = "登录";
  }
}

/* ============================================================
 * 8. ★ TODO ⑤ 借书 ★
 *    提示：docs/07-前后端联调.md 第 7 节「完整借书流程时序图」
 *
 *    (1) 调借书接口
 *        · await api("/api/borrows/borrow", { method: "POST", body: { bookId } })
 *        · body 的字段名就是 bookId，和类型定义一致（docs/07 第 3 节）
 *
 *    (2) 成功后刷新数据
 *        · toast("借阅成功", "success")
 *        · await loadBooks() 重新向后端要一份最新列表
 *        ⚠️ 绝对不要写 book.available -= 1 或 available - 1：
 *           库存只有后端说了算，前端自己减就是两套口径（docs/07 第 1 节）
 *
 *    (3) 失败处理
 *        · catch 里 toast(err.message, "error")，比如「《xxx》已全部借出」
 *        · finally 里：如果按钮还在页面上（button.isConnected），把它恢复可点；
 *          成功时 loadBooks() 会重绘整个 tbody，旧按钮已经不在文档里，不用管
 * ============================================================ */

/**
 * 借一本书。由 tbody 上的「事件委托」调用（见 bindEvents）。
 * @param {string} bookId 例如 "B001"
 */
async function handleBorrow(bookId) {
  if (!bookId) return;

  // 防连点：借书按钮点一下要禁用到请求结束（docs/07 常见坑最后一条）
  const button = el.bookTbody.querySelector(`button[data-action="borrow"][data-id="${bookId}"]`);
  if (button) button.disabled = true;

  try {
    // 按本节顶部 (1)~(3) 写
    throw new ApiError("handleBorrow() 还没实现，见第 8 节顶部注释的 (1)~(3)", 0, null); // NOT_DONE
  } catch (err) {
    toast(err?.message ?? "借书失败", "error");
    if (button && button.isConnected) button.disabled = false;
  }
}

/* ============================================================
 * 9. 已经写好的流程代码（读一遍，重点看 loadBooks 怎么调 api()）
 * ============================================================ */

/**
 * 拉列表的固定套路：开 loading → 调 api() → 把数据交给 render → 关 loading。
 * 这个函数不用你改，把它当「调用范例」抄。
 */
async function loadBooks() {
  setLoading(true);
  el.listError.textContent = "";
  try {
    const books = await api("/api/books");
    state.books = Array.isArray(books) ? books : [];
    renderBooks(filterBooks(state.keyword)); // 数据一变就重画，别漏
  } catch (err) {
    el.listError.textContent = err?.message ?? "加载失败";
    toast(err?.message ?? "加载失败", "error");
  } finally {
    setLoading(false);
  }
}

/** 搜索框：输入即过滤（客户端实时过滤，不请求后端） */
function handleSearch(event) {
  state.keyword = event.target.value;
  renderBooks(filterBooks(state.keyword));
}

/** 退出登录：清 Token、清状态、回登录页 */
function handleLogout() {
  localStorage.removeItem(TOKEN_KEY);
  if (USE_MOCK) mockToken = null;
  state.books = [];
  state.keyword = "";
  state.user = null;
  el.searchInput.value = "";
  el.bookTbody.textContent = "";
  showPage("login");
  toast("已退出登录");
}

/** 切到图书页并拉数据 */
async function enterBooksPage() {
  showPage("books");
  el.currentUser.textContent = state.user?.name ?? state.user?.username ?? "已登录";
  await loadBooks();
}

/** mock 模式的「跳过登录」：后端还没写好时，先专心练列表部分 */
function handleSkipLogin() {
  if (!USE_MOCK) return;
  mockToken = "mock-guest-token";
  localStorage.setItem(TOKEN_KEY, mockToken);
  state.user = { username: "guest", name: "游客（mock）" };
  enterBooksPage();
}

/** 绑定所有事件（借书用事件委托，动态生成的按钮也能响应） */
function bindEvents() {
  el.loginForm.addEventListener("submit", handleLogin);
  el.searchInput.addEventListener("input", handleSearch);
  el.refreshBtn.addEventListener("click", () => loadBooks());
  el.logoutBtn.addEventListener("click", handleLogout);
  el.skipLoginBtn.addEventListener("click", handleSkipLogin);
  el.selfCheckBtn.addEventListener("click", runSelfCheck);

  // 事件委托：监听器只绑在 tbody 上，不管有多少行、多少按钮都只绑这一次
  // （docs/06A 必会点：靠 event.target 判断点到了谁）
  el.bookTbody.addEventListener("click", (event) => {
    const button = event.target.closest('button[data-action="borrow"]');
    if (!button) return;
    handleBorrow(button.dataset.id);
  });
}

/* ============================================================
 * 10. 自检：做完一个 TODO 就跑一次 runSelfCheck()
 * ============================================================ */

/** 判断「空填了没有」：函数体里只要还留着那行占位语句 = 没做完 */
const isNotDone = (fn) => fn.toString().includes("NOT_DONE");

const TODO_LIST = [
  {
    fn: api,
    name: "api(path, options)",
    what: "统一请求封装（唯一的网络出口）",
    tip: "mock 模式下不影响使用，但切到真实后端前必须做完",
    doc: "docs/06B 动手练习 / docs/07 第 2 节",
  },
  {
    fn: renderBooks,
    name: "renderBooks(books)",
    what: "数据 → 界面：渲染图书表格",
    tip: "先清空 tbody；文本用 textContent；按钮带 data-action / data-id",
    doc: "docs/06A 第四节",
  },
  {
    fn: filterBooks,
    name: "filterBooks(keyword)",
    what: "搜索过滤（返回新数组，不改原数组）",
    tip: "trim + toLowerCase 后 includes；空关键词返回全部",
    doc: "docs/06B 第二节",
  },
  {
    fn: handleLogin,
    name: "handleLogin(event)",
    what: "登录并保存 Token",
    tip: "登录接口要 auth:false；Token 存 localStorage 的 token key",
    doc: "docs/06B 动手练习 · auth.js",
  },
  {
    fn: handleBorrow,
    name: "handleBorrow(bookId)",
    what: "借书 + 重新拉列表",
    tip: "借完要 loadBooks()，绝不在前端改 available",
    doc: "docs/07 第 7 节时序图",
  },
];

function runSelfCheck() {
  const table = TODO_LIST.map((item) => ({
    状态: isNotDone(item.fn) ? "❌ 未完成" : "✅ 已完成",
    函数: item.name,
    作用: item.what,
    关键提示: item.tip,
    对应文档: item.doc,
  }));

  console.log("%c===== 阶段 6 前端脚手架 · 自检报告 =====", "color:#2d6a4f;font-weight:bold;font-size:13px");
  console.table(table);

  const rowCount = el.bookTbody.querySelectorAll("tr").length;
  const token = localStorage.getItem(TOKEN_KEY);

  console.log("%c----- 行为自检（代码写了 ≠ 跑通了）-----", "color:#1d3557;font-weight:bold");
  console.table([
    { 检查项: "localStorage 里有 token", 结果: token ? "✅ 有" : "⚠️ 没有：还没登录，或 handleLogin 忘了存" },
    { 检查项: "表格已渲染出行", 结果: rowCount > 0 ? `✅ ${rowCount} 行` : "⚠️ 表格是空的：看 renderBooks 或 loadBooks 的报错" },
    { 检查项: "搜索框输入后行数变化", 结果: "手动试：输入 javascript，mock 数据应只剩 1 行" },
    { 检查项: "前端有没有自己算库存", 结果: "手动搜：全文不应出现 available - 1 / avail--" },
    { 检查项: "USE_MOCK 开关", 结果: USE_MOCK ? "true（本地假数据）" : `false（真实后端 ${API_BASE}）` },
  ]);

  const left = TODO_LIST.filter((item) => isNotDone(item.fn)).length;
  if (left === 0) {
    console.log("%c🎉 5 个 TODO 全部完成。下一步：把 USE_MOCK 改成 false 接真实后端，见 README.md", "color:#2d6a4f;font-weight:bold");
    toast("自检通过：TODO 全部完成 🎉", "success");
  } else {
    console.log(`%c还剩 ${left} 个 TODO 没做，加油 💪`, "color:#b45309;font-weight:bold");
    toast(`自检：还有 ${left} 个 TODO 未完成（详见控制台）`, "info");
  }
  return left;
}

// 让学习者可以直接在控制台敲 runSelfCheck()
window.runSelfCheck = runSelfCheck;

/* ============================================================
 * 11. 启动
 * ============================================================ */

function bootstrap() {
  showPage("login");
  el.mockHint.hidden = !USE_MOCK;
  el.modeBadge.textContent = USE_MOCK ? "mock 模式" : `后端模式 ${API_BASE}`;

  // 刷新不掉登录：localStorage 里有 Token 就直接进列表页
  const savedToken = localStorage.getItem(TOKEN_KEY);
  if (savedToken) {
    if (USE_MOCK) mockToken = savedToken; // mock 后端也认这个 Token
    state.user = { username: "restored", name: "已登录用户" };
    enterBooksPage();
  }

  bindEvents();

  console.log(
    "%c👋 欢迎来到阶段 6 纯 JS 练习。先在控制台运行 runSelfCheck() 看看有哪些 TODO，或点右下角「自检」按钮。",
    "color:#1d3557;font-weight:bold"
  );
}

bootstrap();
