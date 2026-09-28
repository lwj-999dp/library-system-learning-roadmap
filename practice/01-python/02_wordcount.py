"""练习 2：读文本统计词频（阶段 1 · Python 基础）

【题目要求】
    给一段文本，统计每个单词出现了几次，并输出出现最多的前 N 个：
      1. load_text    不传路径就读内置的 SAMPLE_TEXT；传了路径就真的去读文件
      2. tokenize     切成单词列表：转小写、只保留英文字母
      3. count_words  用 collections.Counter 统计次数
      4. top_n        取前 N 名，次数相同的按字母顺序（结果必须稳定）

【验收标准】（对应 docs/01-Python基础.md 的「动手练习 · 练习 2」）
    [ ] python 02_wordcount.py 里 5 个自测项（4 个函数 + 1 个综合项）全部显示 [x]
    [ ] 能说清 Counter 和普通 dict 的区别，以及 most_common() 的坑
    [ ] 加分项：看到中文也能按「中文按字、英文按词」切（自测不检查这个）

【路线图文档】../../docs/01-Python基础.md  （阶段 1 · Python 基础）

【怎么用这个文件】
    把每个函数里的 `raise NotImplementedError(...)` 换成你自己的实现。
    想加更多自测就在 _check_xxx 里写 assert，末尾的 assert 代码请勿删除。
"""

import re
from collections import Counter

# 内置示例文本：故意不依赖外部文件，保证你 clone 下来就能跑
SAMPLE_TEXT = """
Python is a popular programming language. Python is easy to learn.
A library system needs books, readers and borrow records.
Books are borrowed by readers, and readers love books.
FastAPI makes building an API with Python fast and fun.
"""


# =====================================================================
# 待办区：下面 4 个函数就是你要写的代码
# =====================================================================


def load_text(path: str | None = None) -> str:
    """读取要统计的文本：path 为 None 时返回内置的 SAMPLE_TEXT"""
    # TODO(练习 2-1)：读取文本
    # 提示：
    #   1) path 是 None 就直接 `return SAMPLE_TEXT`
    #   2) 传了路径就用 pathlib：`Path(path).read_text(encoding="utf-8")`
    #   3) encoding 必须写！Windows 上不写默认是 GBK，中文会乱码或抛 UnicodeDecodeError
    # 预期结果：
    #   load_text()                  -> 返回上面那段 SAMPLE_TEXT，且包含 "Python"
    #   load_text("某个文本文件")      -> 返回文件全部内容
    raise NotImplementedError("练习 2-1：读取文本")


def tokenize(text: str) -> list[str]:
    """把文本切成单词列表：全部转小写、只保留英文字母（连续字母算一个词）"""
    # TODO(练习 2-2)：切词
    # 提示：
    #   `re.findall(r"[a-zA-Z]+", text.lower())` 一把梭：找出一段一段的字母
    #   也可以自己 split + strip 标点，但标点种类太多，正则更省事
    # 预期结果：
    #   tokenize("Python is fun. Python!") -> ["python", "is", "fun", "python"]
    #   tokenize("")                       -> []
    raise NotImplementedError("练习 2-2：切词")


def count_words(words: list[str]) -> Counter[str]:
    """统计每个词出现几次，返回 collections.Counter"""
    # TODO(练习 2-3)：计数
    # 提示：
    #   最简单：`return Counter(words)`（Counter 可以直接吃一个列表）
    #   想练基本功：先 `counts: Counter[str] = Counter()`，再 for 循环 counts[word] += 1
    #   对比着体会一下：Counter 访问不存在的键返回 0，而普通 dict["不存在的键"] 会抛 KeyError
    # 预期结果：
    #   count_words(["a", "b", "a"])["a"] == 2，["b"] == 1，["c"] == 0
    raise NotImplementedError("练习 2-3：计数")


def top_n(counter: Counter[str], n: int = 3) -> list[tuple[str, int]]:
    """取出现次数最多的前 n 个，返回 [(单词, 次数), ...]

    排序规则（必须遵守，否则自测过不了）：
      先按次数从多到少；次数相同时按单词字母顺序 —— 这样结果才稳定、可测试。
    """
    # TODO(练习 2-4)：取 Top N
    # 提示：
    #   `counter.most_common(n)` 能用，但「次数相同」时它按插入顺序排，结果不稳定
    #   要稳定就用 key：`sorted(counter.items(), key=lambda item: (-item[1], item[0]))`
    #   然后切片取前 n 个：`[:n]`
    # 预期结果：
    #   top_n(Counter({"a": 5, "b": 2, "r": 2}), 2) -> [("a", 5), ("b", 2)]
    #   n 比词还多时，有几个返回几个，不要报错
    raise NotImplementedError("练习 2-4：取 Top N")


# =====================================================================
# 入口：不用改
# =====================================================================
def main() -> int:
    passed = run_checks(CHECKS)
    if passed == len(CHECKS):
        print("\n来看看真实输出（SAMPLE_TEXT 的前 8 名）：")
        for rank, (word, count) in enumerate(top_n(count_words(tokenize(load_text())), 8), start=1):
            print(f"  {rank}. {word:<12} {count:>2} 次")
        print("\n加分项：把 SAMPLE_TEXT 换成一整本英文小说，看看统计要跑多久。")
    return 0


# =====================================================================
# 自测区：下面的代码不用改，它是你的「验收工具」
# =====================================================================
import tempfile
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


def _check_load() -> None:
    """练习 2-1：读取（内置常量 + 真实文件 + utf-8）"""
    default_text = load_text()
    assert isinstance(default_text, str), f"应该返回 str，实际 {type(default_text).__name__}"
    assert "Python" in default_text, "不传参数时应该返回内置的 SAMPLE_TEXT"

    with tempfile.TemporaryDirectory() as tmp:
        # 故意写一段中文：不写 encoding="utf-8" 在 Windows 上会乱码或直接报错
        sample = Path(tmp) / "sample.txt"
        sample.write_text("你好 Python\nhello world\n", encoding="utf-8")
        assert load_text(str(sample)) == "你好 Python\nhello world\n", "传路径时应该返回文件内容（用 utf-8 读）"


def _check_tokenize() -> None:
    """练习 2-2：切词"""
    assert tokenize("Python is fun. Python!") == ["python", "is", "fun", "python"], "应该转小写 + 只留字母"
    assert tokenize("") == [], "空字符串应该返回空列表"
    assert tokenize("A1 B2 C3") == ["a", "b", "c"], "数字不该算进单词里"

    words = tokenize(load_text())
    assert len(words) == 39, f"SAMPLE_TEXT 一共有 39 个英文单词，你切出来 {len(words)} 个"
    assert all(word.isalpha() and word.islower() for word in words), "每个词都应该是纯小写字母"


def _check_count() -> None:
    """练习 2-3：计数"""
    counter = count_words(["a", "b", "a", "c", "a"])
    assert isinstance(counter, Counter), f"应该返回 collections.Counter，实际 {type(counter).__name__}"
    assert counter["a"] == 3, f"a 应该出现 3 次，实际 {counter['a']} 次"
    assert counter["b"] == 1, f"b 应该出现 1 次，实际 {counter['b']} 次"
    assert counter["没出现过的词"] == 0, "Counter 里不存在的键应该返回 0（这正是它比 dict 好用的地方）"
    assert sum(counter.values()) == 5, f"所有次数加起来应该是 5，实际 {sum(counter.values())}"


def _check_top_n() -> None:
    """练习 2-4：Top N（含并列时的稳定排序）"""
    counter: Counter[str] = Counter({"a": 5, "b": 2, "r": 2, "c": 1})
    assert top_n(counter, 2) == [("a", 5), ("b", 2)], "并列第 2 名时应按字母顺序取 b，不是 r"
    assert top_n(counter, 10) == [("a", 5), ("b", 2), ("r", 2), ("c", 1)], "n 超出总数时应该全部返回"
    assert top_n(Counter(), 3) == [], "空 Counter 应该返回空列表"


def _check_end_to_end() -> None:
    """综合项：把 4 个函数串起来跑 SAMPLE_TEXT（依赖 2-1 ~ 2-4 全部完成）"""
    from_sample = count_words(tokenize(load_text()))
    assert from_sample["python"] == 3, f"SAMPLE_TEXT 里 python 出现 3 次，你数出 {from_sample['python']} 次"
    assert from_sample["books"] == 3, f"SAMPLE_TEXT 里 books（Books 要算同一个词）出现 3 次，你数出 {from_sample['books']} 次"

    top3 = top_n(from_sample, 3)
    assert top3 == [("and", 3), ("books", 3), ("python", 3)], f"前 3 名应该是 and/books/python 各 3 次，实际 {top3}"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("练习 2-1：读取文本", _check_load),
    ("练习 2-2：切词", _check_tokenize),
    ("练习 2-3：统计词频", _check_count),
    ("练习 2-4：取 Top N", _check_top_n),
    ("综合：SAMPLE_TEXT 全流程", _check_end_to_end),
]


if __name__ == "__main__":
    raise SystemExit(main())
