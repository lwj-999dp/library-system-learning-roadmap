"""阶段 2 练习：FastAPI 内存版图书 CRUD（里程碑 ③）

【怎么运行】
    1) 装依赖（在仓库根目录执行，用你的 venv）：
           pip install -r practice/requirements.txt
    2) 启动服务：
           uvicorn main:app --reload --app-dir practice/02-memory-api
    3) 浏览器打开 http://127.0.0.1:8000/docs ，点 Try it out 逐个试
    4) 只想看自己做完没有（不用启服务）：
           python practice/02-memory-api/main.py

【题目要求】
    数据只用模块级列表 `books` 存，**不连数据库**（进程重启就丢，这是故意的）：
      1. 补完 4 个接口的函数体：
         GET /books、POST /books、PUT /books/{book_id}、DELETE /books/{book_id}
      2. 补完 BookCreate 的字段校验：书名 1~100 字、作者 1~50 字、库存 0~999 且默认 1
    已经写好的部分：app 实例、BookUpdate、Book、3 本预置图书、find_book 工具函数。

【验收标准】（对应 docs/02-Web与HTTP基础.md 的「动手练习 · 练习 2」）
    [ ] python practice/02-memory-api/main.py 里所有自测项都显示 [x]
    [ ] GET /books 返回 3 本预置图书；GET /books?keyword=三体 只返回 1 本
    [ ] POST /books 合法数据返回 **201**（不是 200），响应体带新 id（B004）
    [ ] PUT /books/B001 只传 {"stock": 9} 时，author 不能变成 null
    [ ] PUT/DELETE 一个不存在的 id 返回 **404**
    [ ] DELETE 成功返回 **204**（响应体为空）
    [ ] POST 一个非法 body（如 stock: "abc" 或 title: ""）返回 **422**，不是 500
    [ ] 能说清 422 是谁的错（客户端参数错），以及为什么 /docs 不用自己写前端

【路线图文档】../../docs/02-Web与HTTP基础.md  （阶段 2 · Web 与 HTTP 基础）

【怎么用这个文件】
    每个待办处有 `# TODO(...)` 注释和一行 `raise NotImplementedError(...)` 占位。
    写完一个接口，就跑一次 `python main.py`，看那一项从 [ ] 变成 [x]。
    ⚠️ NotImplementedError 会让接口返回 500 —— 那是「还没写」，不是 bug。
"""

# ⚠️ 这里**故意不写** `from __future__ import annotations`：
# 它会把注解变成字符串，FastAPI 解析 `-> None` 时拿到 NoneType，
# 就会给 DELETE 204 接口推断出一个「响应体」，导入模块时直接崩：
#   AssertionError: Status code 204 must not have a response body
# Python 3.12 本来就支持 str | None 这种写法，不需要这个 future 导入。
try:
    from fastapi import FastAPI, HTTPException, status
    from pydantic import BaseModel, Field, ValidationError
except ModuleNotFoundError as exc:      # 没装依赖时给人话提示，而不是一堆红色堆栈
    raise SystemExit(
        f"缺少依赖：{exc.name}\n"
        "请先在仓库根目录执行：pip install -r practice/requirements.txt"
    ) from exc

app = FastAPI(title="Library API", version="0.2.0")


# =====================================================================
# Pydantic 模型
# =====================================================================
class BookCreate(BaseModel):
    """新增图书时前端要传的字段"""

    # TODO(模型 A)：给下面 3 个字段补上校验（Field 已经从 pydantic 导入好了）
    # 提示：
    #   title  -> Field(min_length=1, max_length=100, description="书名")
    #   author -> Field(min_length=1, max_length=50, description="作者")
    #   stock  -> Field(default=1, ge=0, le=999, description="库存，0 表示全借出")
    #   注意：description 只是文档文字，真正干活的是 min_length / ge / le
    # 预期结果：
    #   BookCreate(title="", author="x")                -> ValidationError（书名不能空）
    #   BookCreate(title="x" * 101, author="y")         -> ValidationError（书名太长）
    #   BookCreate(title="x", author="y", stock=-1)     -> ValidationError（库存不能为负）
    #   BookCreate(title="x", author="y", stock=1000)   -> ValidationError（库存上限 999）
    #   BookCreate(title="x", author="y", stock="abc")  -> ValidationError（类型不对）
    #   BookCreate(title="x", author="y").stock         -> 1（默认值）
    title: str
    author: str
    stock: int = 1


class BookUpdate(BaseModel):
    """更新时字段全部可选，只改传上来的那些（已经写好，不用改）"""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=50)
    stock: int | None = Field(default=None, ge=0, le=999)


class Book(BookCreate):
    """返回给前端的完整图书：比入参多一个 id（已经写好，不用改）"""

    id: str


# =====================================================================
# 内存「数据库」：进程重启就没了（故意的，阶段 4 才换成 MySQL）
# =====================================================================
books: list[Book] = [
    Book(id="B001", title="三体", author="刘慈欣", stock=3),
    Book(id="B002", title="活着", author="余华", stock=1),
    Book(id="B003", title="人类简史", author="尤瓦尔·赫拉利", stock=0),
]
_next_id = 4          # 自增主键，模拟数据库的 AUTO_INCREMENT


def find_book(book_id: str) -> Book:
    """按 id 找书，找不到就抛 404（已经写好，不用改；这样每个接口都少写一遍循环）"""
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"图书 {book_id} 不存在")


# =====================================================================
# 接口：下面 4 个 TODO 就是你要写的代码
# =====================================================================
@app.get("/health", tags=["系统"])
def health() -> dict:
    """健康检查：部署后用来确认服务还活着（已经写好，不用改）"""
    return {"ok": True, "service": "library-api"}


@app.get("/books", response_model=list[Book], tags=["图书"])
def list_books(keyword: str | None = None) -> list[Book]:
    """GET /books，或 GET /books?keyword=三体"""
    # TODO(接口 1)：返回图书列表，keyword 有值时按书名模糊过滤
    # 提示：
    #   1) keyword 是 None（或空字符串）时直接 `return books`
    #   2) 有 keyword 时用列表生成式：[b for b in books if keyword.lower() in b.title.lower()]
    #   3) 返回新列表，别去修改 books 本身
    # 预期结果：
    #   list_books()          -> 3 本预置图书（三体 / 活着 / 人类简史）
    #   list_books("三体")     -> 只有《三体》1 本
    #   list_books("人类")     -> 只有《人类简史》1 本
    #   list_books("不存在")   -> []
    raise NotImplementedError("接口 1：GET /books")


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["图书"])
def create_book(payload: BookCreate) -> Book:
    """新增图书，成功返回 201（不是 200）"""
    # TODO(接口 2)：把 payload 变成一本带 id 的书，存进 books 并返回
    # 提示：
    #   1) 要改模块级变量 _next_id，函数里必须先写 `global _next_id`
    #   2) 拼 id：f"B{_next_id:03d}" -> B004、B005（03d 表示补零到 3 位）
    #   3) 造对象：book = Book(id=新id, **payload.model_dump())
    #      model_dump() 把 Pydantic 对象变成普通 dict，** 负责展开成关键字参数
    #   4) 别忘了 books.append(book) 和 _next_id += 1，最后 return book
    # 预期结果：
    #   create_book(BookCreate(title="呐喊", author="鲁迅", stock=2))
    #     -> 返回 id 为 "B004" 的 Book，books 长度从 3 变成 4
    #   下一次再新增 -> id 是 "B005"（自增不能乱）
    raise NotImplementedError("接口 2：POST /books")


@app.put("/books/{book_id}", response_model=Book, tags=["图书"])
def update_book(book_id: str, payload: BookUpdate) -> Book:
    """更新图书；exclude_unset 保证只改前端传了的字段"""
    # TODO(接口 3)：局部更新一本书
    # 提示：
    #   1) book = find_book(book_id)     # 不存在时它会自动抛 404，你不用自己判断
    #   2) for key, value in payload.model_dump(exclude_unset=True).items():
    #          setattr(book, key, value)
    #   3) exclude_unset=True 是关键：不加的话没传的字段会变成 None，author 就被清空了
    #   4) return book
    # 预期结果：
    #   update_book("B001", BookUpdate(stock=9))  -> stock 变成 9，author 还是「刘慈欣」
    #   update_book("B999", BookUpdate(stock=1))  -> HTTPException 404
    raise NotImplementedError("接口 3：PUT /books/{book_id}")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["图书"])
def delete_book(book_id: str) -> None:
    """删除成功返回 204，响应体为空"""
    # TODO(接口 4)：删除一本书
    # 提示：
    #   1) 一行就够：books.remove(find_book(book_id))
    #      find_book 负责「不存在就 404」，remove 负责从列表里拿掉
    #   2) 返回 None（204 表示没有响应体，别 return 被删掉的那本书）
    # 预期结果：
    #   delete_book("B003") -> 列表里没有 B003 了
    #   再 delete_book("B003") -> HTTPException 404
    raise NotImplementedError("接口 4：DELETE /books/{book_id}")


# =====================================================================
# 自测区：不用启动 uvicorn，直接调用上面这些函数来检查逻辑
# （想看真实 HTTP 状态码，请启动服务后开 /docs，或照着 README 里的 curl 敲一遍）
# =====================================================================
import traceback
import unicodedata
from collections.abc import Callable
from pathlib import Path

_SOURCE_LINES = Path(__file__).read_text(encoding="utf-8").splitlines()


def _display_width(text: str) -> int:
    """算字符串在终端里的显示宽度：中文/全角算 2 列，英文数字算 1 列（对齐用）"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def _pad(text: str, width: int) -> str:
    """按显示宽度补空格，让中文标题也能对齐"""
    return text + " " * max(width - _display_width(text), 1)


def _todo_line(exc: BaseException) -> int:
    """从异常的调用栈里找到本文件中抛 NotImplementedError 的那一行，
    再往上找最近的 `# TODO` 注释，返回它的行号，方便直接跳过去补代码。"""
    here = Path(__file__).resolve()
    line = 0
    for frame in reversed(traceback.extract_tb(exc.__traceback__)):
        if Path(frame.filename).resolve() == here:
            line = frame.lineno
            break
    if line == 0:
        return 0
    for index in range(line - 1, max(line - 41, 0), -1):
        if "# TODO" in _SOURCE_LINES[index]:
            return index + 1
    return line


def _todo_line_of(keyword: str) -> int:
    """按关键字找 `# TODO` 注释的行号，用在「校验没生效」这类断言消息里指路"""
    for index, text in enumerate(_SOURCE_LINES, start=1):
        if "# TODO" in text and keyword in text:
            return index
    return 0


def run_checks(checks: list[tuple[str, Callable[[], None]]]) -> int:
    """依次执行自测项：TODO 没做打印 [ ]，断言失败打印 [ ]，其他异常打印 [!]"""
    print("=" * 74)
    passed = 0
    for title, check in checks:
        try:
            check()
        except NotImplementedError as exc:
            print(f"[ ] {_pad(title, 30)} —— 未完成（第 {_todo_line(exc)} 行 TODO）")
        except AssertionError as exc:
            print(f"[ ] {_pad(title, 30)} —— 未通过：{exc or '断言失败'}")
        except Exception as exc:        # 脚手架故意兜底：报错也照常打印后面的进度
            print(f"[!] {_pad(title, 30)} —— 报错：{type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"[x] {_pad(title, 30)} —— 通过")
    print("-" * 74)
    print(f"进度：{passed}/{len(checks)} 项通过")
    if passed == len(checks):
        print("逻辑全部通过！接下来务必亲手用 /docs 或 curl 确认状态码：201 / 204 / 404 / 422。")
    else:
        print("还没做完：按上面的行号找到 `# TODO`，写完再跑一次 python main.py。")
    return passed


def _check_health() -> None:
    """环境检查：app 能导入，健康检查能返回（这项一开始就是 [x]）"""
    assert health() == {"ok": True, "service": "library-api"}, "health() 应该返回 {'ok': True, 'service': 'library-api'}"
    assert any(getattr(route, "path", None) == "/health" for route in app.routes), "/health 路由应该注册到 app 上"


def _check_route_meta() -> None:
    """路由配置检查：状态码 201/204 与 response_model（已给定，用来对照 /docs 的状态码）"""
    routes = {getattr(route, "path", None): route for route in app.routes}
    post = routes.get("/books")
    delete = routes.get("/books/{book_id}")
    assert post is not None, "找不到 POST /books 路由"
    assert post.status_code == 201, f"POST /books 的状态码应该是 201，实际 {post.status_code}"
    assert delete is not None, "找不到 DELETE /books/{{book_id}} 路由"
    assert delete.status_code == 204, f"DELETE /books/{{book_id}} 的状态码应该是 204，实际 {delete.status_code}"


def _check_list() -> None:
    """接口 1：GET /books（列表 + keyword 过滤）"""
    all_books = list_books()
    assert isinstance(all_books, list), f"应该返回 list，实际 {type(all_books).__name__}"
    assert len(all_books) == 3, f"应该有 3 本预置图书，实际 {len(all_books)} 本"
    titles = {book.title for book in all_books}
    assert titles == {"三体", "活着", "人类简史"}, f"预置图书应该是三体/活着/人类简史，实际 {titles}"

    hit = list_books("三体")
    assert isinstance(hit, list) and len(hit) == 1 and hit[0].id == "B001", f"keyword=三体 应该只命中 B001，实际 {hit}"
    assert len(list_books("人类")) == 1, "keyword 应该按书名模糊匹配（能命中《人类简史》）"
    assert list_books("这本书不存在") == [], "匹配不上时应该返回空列表 []，不是 404"
    assert list_books("") != [] or True, "keyword 传空字符串时按「不过滤」处理更友好"


def _check_create() -> None:
    """接口 2：POST /books（自增 id + 入列表）"""
    before = len(books)
    created = create_book(BookCreate(title="呐喊", author="鲁迅", stock=2))
    assert isinstance(created, Book), f"应该返回 Book 对象，实际 {type(created).__name__}"
    assert created.id == "B004", f"第一本新书的 id 应该是 B004（f'B{{_next_id:03d}}'），实际 {created.id!r}"
    assert (created.title, created.author, created.stock) == ("呐喊", "鲁迅", 2), f"返回内容不对：{created}"
    assert len(books) == before + 1, f"新书必须 append 进 books，实际长度 {len(books)}"
    assert any(book.id == "B004" for book in books), "books 里应该能找到 B004"

    second = create_book(BookCreate(title="朝花夕拾", author="鲁迅"))
    assert second.id == "B005", f"id 必须自增（_next_id += 1 别忘写），实际 {second.id!r}"
    assert second.stock == 1, "stock 不传时应该用默认值 1"


def _check_update() -> None:
    """接口 3：PUT /books/{id}（只改传了的字段 + 404）"""
    updated = update_book("B001", BookUpdate(stock=9))
    assert updated.stock == 9, f"stock 应该被改成 9，实际 {updated.stock}"
    assert updated.author == "刘慈欣", f"只传了 stock，author 不能被清空，实际 {updated.author!r}"
    assert updated.title == "三体", "只传了 stock，title 也不能被清空"

    target = find_book("B001")
    assert target.stock == 9, "update_book 要直接改 books 里的那本书（同一对象），不是返回一个新对象"

    try:
        update_book("B999", BookUpdate(stock=1))
    except HTTPException as exc:
        assert exc.status_code == 404, f"改不存在的 id 应该 404，实际 {exc.status_code}"
    else:
        raise AssertionError("改不存在的 id 必须抛 404（用 find_book 就有了）")


def _check_delete() -> None:
    """接口 4：DELETE /books/{id}（删除 + 再删一次 404）"""
    result = delete_book("B003")
    assert result is None, f"204 表示没有响应体，所以应该 return None，实际返回 {result!r}"
    assert all(book.id != "B003" for book in books), "B003 应该已经从 books 里删掉"

    try:
        delete_book("B003")
    except HTTPException as exc:
        assert exc.status_code == 404, f"再删一次应该 404，实际 {exc.status_code}"
    else:
        raise AssertionError("删除不存在的 id 必须抛 404")


def _check_validation_text() -> None:
    """模型 A（上）：书名 / 作者的长度校验"""
    pointer = _todo_line_of("模型 A")
    for bad_title in ("", "x" * 101):
        try:
            BookCreate(title=bad_title, author="鲁迅")
        except ValidationError:
            continue
        raise AssertionError(f"书名 {bad_title[:12]!r}（长度 {len(bad_title)}）应该被拦下，见第 {pointer} 行 TODO")
    for bad_author in ("", "y" * 51):
        try:
            BookCreate(title="呐喊", author=bad_author)
        except ValidationError:
            continue
        raise AssertionError(f"作者长度 {len(bad_author)} 应该被拦下，见第 {pointer} 行 TODO")

    ok = BookCreate(title="呐喊", author="鲁迅", stock=2)
    assert (ok.title, ok.author, ok.stock) == ("呐喊", "鲁迅", 2), "合法数据必须能正常创建"


def _check_validation_stock() -> None:
    """模型 A（下）：库存范围、类型与默认值"""
    pointer = _todo_line_of("模型 A")
    for bad_stock in (-1, 1000, "abc"):
        try:
            BookCreate(title="呐喊", author="鲁迅", stock=bad_stock)
        except ValidationError:
            continue
        raise AssertionError(f"stock={bad_stock!r} 应该被拦下（ge=0, le=999），见第 {pointer} 行 TODO")

    for good_stock in (0, 999):
        BookCreate(title="呐喊", author="鲁迅", stock=good_stock)      # 边界值必须放行

    assert BookCreate(title="呐喊", author="鲁迅").stock == 1, "stock 不传时默认值应该是 1"
    assert BookCreate(title="呐喊", author="鲁迅", stock="2").stock == 2, "Pydantic 会把合法字符串 '2' 转成 int 2"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("环境：app 与 /health", _check_health),
    ("路由：状态码 201 / 204", _check_route_meta),
    ("接口 1：GET /books", _check_list),
    ("接口 2：POST /books", _check_create),
    ("接口 3：PUT /books/{id}", _check_update),
    ("接口 4：DELETE /books/{id}", _check_delete),
    ("模型 A：书名 / 作者校验", _check_validation_text),
    ("模型 A：库存范围与默认值", _check_validation_stock),
]


if __name__ == "__main__":
    passed = run_checks(CHECKS)
    print()
    print("下一步（真实 HTTP 测试，自测只能验证逻辑，验证不了状态码）：")
    print("  uvicorn main:app --reload --app-dir practice/02-memory-api")
    print("  浏览器打开 http://127.0.0.1:8000/docs ，点 Try it out")
    print("  或在另一个终端敲 README.md 里的 curl 命令")
    raise SystemExit(0)
