"""练习 1：命令行通讯录（阶段 1 · Python 基础）

【题目要求】
    用 dict 把联系人存在内存里（进程一结束就丢，这是故意的），实现 4 个函数：
      1. add_contact    新增联系人（重名 / 空的姓名或电话要抛 ValueError）
      2. find_contact   按姓名查电话，查不到返回 None
      3. delete_contact 按姓名删除，删掉了返回 True，没这个人返回 False
      4. list_contacts  返回排序好的展示行，交给调用方 print
    数据不许用全局变量存：由 main() 持有，作为参数传进函数。

【验收标准】（对应 docs/01-Python基础.md 的「动手练习 · 练习 1」）
    [ ] python 01_contacts.py 里 4 个自测项全部显示 [x]
    [ ] 4 个自测项全通过后，同一命令会进入交互模式，add / find / del / list / quit 都能用
    [ ] 能口头回答：为什么 find_contact 用 d.get(name) 而不是 d[name]？

【路线图文档】../../docs/01-Python基础.md  （阶段 1 · Python 基础）

【怎么用这个文件】
    每个待办函数里都有一行 `raise NotImplementedError(...)`，它只是占位符，
    作用是让你「一行不写也能直接运行」并看到进度。把它换成你自己的实现即可。
    末尾的 assert 自测代码请勿删除 —— 那是你的验收工具。
"""

# =====================================================================
# 待办区：下面 4 个函数就是你要写的代码
# 类型注解看不懂没关系，先照着签名写：contacts 是 {姓名: 电话} 的字典
# =====================================================================


def add_contact(contacts: dict[str, str], name: str, phone: str) -> None:
    """新增联系人：直接修改传进来的 contacts（不需要 return）"""
    # TODO(练习 1-1)：新增联系人
    # 提示：
    #   1) 先校验：姓名或电话去空格后为空 -> raise ValueError("姓名和电话都不能为空")
    #   2) 再查重：`if name in contacts:` -> raise ValueError(f"{name} 已存在")
    #   3) 最后写入：`contacts[name] = phone`
    # 预期结果：
    #   d = {}; add_contact(d, "张三", "138")      -> d == {"张三": "138"}
    #   add_contact({"张三": "138"}, "张三", "1")   -> 抛 ValueError
    #   add_contact({}, "  ", "138")               -> 抛 ValueError
    raise NotImplementedError("练习 1-1：新增联系人")


def find_contact(contacts: dict[str, str], name: str) -> str | None:
    """按姓名查电话：找到返回电话（str），找不到返回 None（不要抛异常）"""
    # TODO(练习 1-2)：查找联系人
    # 提示：`contacts.get(name)` 一步到位；用 `contacts[name]` 的话必须自己处理 KeyError
    # 预期结果：
    #   find_contact({"张三": "138"}, "张三") -> "138"
    #   find_contact({"张三": "138"}, "李四") -> None
    raise NotImplementedError("练习 1-2：查找联系人")


def delete_contact(contacts: dict[str, str], name: str) -> bool:
    """按姓名删除：删掉了返回 True，本来就没有这个人返回 False（不要抛异常）"""
    # TODO(练习 1-3)：删除联系人
    # 提示：`contacts.pop(name, None)` 的第二个参数是「找不到时的默认值」，
    #       它返回 None 就说明这个人不存在，别用 `del contacts[name]`（会抛 KeyError）
    # 预期结果：
    #   d = {"a": "1"}; delete_contact(d, "a") -> True，且 d 变成 {}
    #   delete_contact({}, "a")                -> False
    raise NotImplementedError("练习 1-3：删除联系人")


def list_contacts(contacts: dict[str, str]) -> list[str]:
    """返回所有联系人的展示行，按姓名排序，每行形如 "张三        138\""""
    # TODO(练习 1-4)：列出全部联系人
    # 提示：
    #   1) `sorted(contacts.items())` 会按姓名字典序排好，返回 [(姓名, 电话), ...]
    #   2) 用列表生成式一次生成：f"{name:<10} {phone}"（<10 表示左对齐占 10 个字符宽）
    #   3) 空字典要返回空列表 []，不要返回 None
    # 预期结果：
    #   list_contacts({"b": "2", "a": "1"}) -> ["a          1", "b          2"]
    #   （只要求顺序对、每行同时含姓名和电话；空格数不用和示例完全一致）
    raise NotImplementedError("练习 1-4：列出全部联系人")


# =====================================================================
# 交互入口：不用改。等 4 个 TODO 都做完，运行本文件就进入交互模式
# =====================================================================
def main() -> int:
    """先打印自测报告；全部通过后进入命令行交互模式"""
    passed = run_checks(CHECKS)
    if passed < len(CHECKS):
        print("\n补完上面 4 个 TODO 后再运行：python 01_contacts.py")
        return 0

    print("\n进入交互模式（help 看命令，quit 退出）。试试：add 张三 13800000000")
    contacts: dict[str, str] = {}          # 数据由 main 持有，函数只管处理

    while True:
        try:
            command = input("通讯录 > ").strip()
        except (EOFError, KeyboardInterrupt):      # Ctrl+C / Ctrl+Z 优雅退出
            print()
            break
        if command in {"quit", "exit", "q"}:
            break
        if command in {"help", "?"}:
            print("  add 姓名 电话 ｜ find 姓名 ｜ del 姓名 ｜ list ｜ quit")
            continue

        action, _, rest = command.partition(" ")        # partition 只切第一个空格
        rest = rest.strip()
        try:
            if action == "add":
                name, _, phone = rest.partition(" ")
                add_contact(contacts, name.strip(), phone.strip())
                print(f"[ok] 已添加 {name.strip()}")
            elif action == "find":
                phone = find_contact(contacts, rest)
                print(f"  {rest} -> {phone}" if phone else f"  没有找到 {rest}")
            elif action == "del":
                removed = delete_contact(contacts, rest)
                print(f"[ok] 已删除 {rest}" if removed else f"  没有找到 {rest}")
            elif action == "list":
                lines = list_contacts(contacts)
                print("\n".join(f"  {line}" for line in lines) if lines else "  （通讯录是空的）")
            else:
                print("  未知命令，输入 help 查看用法")
        except ValueError as exc:      # add_contact 校验失败时抛的
            print(f"[error] {exc}")

    print("再见。")
    return 0


# =====================================================================
# 自测区：下面的代码不用改，它是你的「验收工具」
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


def run_checks(checks: list[tuple[str, Callable[[], None]]]) -> int:
    """依次执行自测项：TODO 没做打印 [ ]，断言失败打印 [ ]，其他异常打印 [!]"""
    print("=" * 70)
    passed = 0
    for title, check in checks:
        try:
            check()                     # 每个自测项内部都用 assert
        except NotImplementedError as exc:
            print(f"[ ] {_pad(title, 30)} —— 未完成（第 {_todo_line(exc)} 行 TODO）")
        except AssertionError as exc:
            print(f"[ ] {_pad(title, 30)} —— 未通过：{exc or '断言失败'}")
        except Exception as exc:        # 学习脚手架故意兜底：报错也照常打印进度
            print(f"[!] {_pad(title, 30)} —— 报错：{type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"[x] {_pad(title, 30)} —— 通过")
    print("-" * 70)
    print(f"进度：{passed}/{len(checks)} 项通过")
    if passed == len(checks):
        print("恭喜，这个练习做完了：对照文件顶部「验收标准」自查，然后 git commit。")
    else:
        print("还没做完：按上面的行号找到 `# TODO`，读「提示」和「预期结果」再动手。")
    return passed


def _check_add() -> None:
    """练习 1-1：新增（含重名与空值校验）"""
    data: dict[str, str] = {}
    add_contact(data, "张三", "13800000000")
    assert data == {"张三": "13800000000"}, f"新增后字典应该是 {{'张三': '13800000000'}}，实际 {data}"
    add_contact(data, "李四", "13900000000")
    assert len(data) == 2, f"应该有 2 个联系人，实际 {len(data)} 个"

    try:
        add_contact(data, "张三", "111")
    except ValueError:
        pass
    else:
        raise AssertionError("重名时应该 raise ValueError")
    assert data["张三"] == "13800000000", "重名被拒绝后，原来的电话不能被改掉"

    for bad_name, bad_phone in (("", "138"), ("  ", "138"), ("王五", ""), ("王五", "   ")):
        try:
            add_contact(data, bad_name, bad_phone)
        except ValueError:
            continue
        raise AssertionError(f"姓名={bad_name!r} 电话={bad_phone!r} 时应该 raise ValueError")


def _check_find() -> None:
    """练习 1-2：查找"""
    data = {"张三": "138", "李四": "139"}
    assert find_contact(data, "张三") == "138", "找到时应该返回电话字符串"
    assert find_contact(data, "王五") is None, "找不到时应该返回 None，而不是抛异常或返回空字符串"
    assert find_contact({}, "任何人") is None, "空字典里查任何人都是 None"


def _check_delete() -> None:
    """练习 1-3：删除"""
    data = {"张三": "138", "李四": "139"}
    assert delete_contact(data, "张三") is True, "删除成功应该返回 True"
    assert data == {"李四": "139"}, f"删除后字典里不该再有张三，实际 {data}"
    assert delete_contact(data, "张三") is False, "删一个不存在的人应该返回 False"
    assert data == {"李四": "139"}, "删除失败时不能改动原来的字典"


def _check_list() -> None:
    """练习 1-4：列出（排序 + 展示格式）"""
    data = {"张三": "138", "李四": "139", "王五": "137"}
    lines = list_contacts(data)
    assert isinstance(lines, list), f"应该返回 list，实际返回 {type(lines).__name__}"
    assert len(lines) == 3, f"3 个联系人应该返回 3 行，实际 {len(lines)} 行"
    assert all(isinstance(line, str) for line in lines), "每一行都必须是字符串"

    names = [name for name in data if any(name in line for line in lines)]
    assert names, "每行里至少要能看到联系人姓名"
    order = [next(i for i, line in enumerate(lines) if name in line) for name in ("张三", "李四", "王五")]
    assert order == sorted(order), "必须按姓名排序输出（用 sorted(contacts.items())）"
    for name, phone in data.items():
        line = next(line for line in lines if name in line)
        assert phone in line, f"{name} 那一行里必须包含电话 {phone}，实际是 {line!r}"

    assert list_contacts({}) == [], "空字典应该返回空列表 []"


# 自测清单：加一项就在 _check_xxx 里写 assert，不用改 run_checks
CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("练习 1-1：新增联系人", _check_add),
    ("练习 1-2：查找联系人", _check_find),
    ("练习 1-3：删除联系人", _check_delete),
    ("练习 1-4：列出联系人", _check_list),
]


if __name__ == "__main__":
    raise SystemExit(main())
