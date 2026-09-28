"""练习 4：读 CSV 生成统计报告（阶段 1 · Python 基础）

【题目要求】
    下面内置了一段「借阅记录」CSV 文本，你要把它变成一份统计报告：
      1. parse_records        用 csv.DictReader 把 CSV 变成 list[dict]，空行要跳过
      2. days_borrowed        用 datetime 算「借出 -> 归还」共几天；还没归还返回 None
      3. summary_by_category  按分类汇总借阅次数（返回 dict）
      4. format_report        拼出多行报告字符串（格式见下方「预期结果」）
    整个过程用 io.StringIO 把字符串当文件读，所以不需要任何外部 CSV 文件。

【验收标准】（阶段 1 扩展练习：对应 docs/01-Python基础.md 的「练习 2」CSV 部分 + 知识点 6「文件读写与 datetime」）
    [ ] python 04_csv_report.py 里 4 个自测项全部显示 [x]
    [ ] 报告中「总记录数」「未归还」「分类汇总」「平均借阅天数」四项都要正确
    [ ] 能说清为什么读文件要写 encoding="utf-8"，以及 strptime 和 strftime 的分工

【路线图文档】../../docs/01-Python基础.md  （阶段 1 · Python 基础）

【怎么用这个文件】
    把每个函数里的 `raise NotImplementedError(...)` 换成你自己的实现。
    末尾的 assert 自测代码请勿删除 —— 那是你的验收工具。
"""

import csv
import io
from datetime import date, datetime

# 内置示例数据：列名就是 CSV 的表头，最后一行 J004 还没归还（归还日期为空）
SAMPLE_CSV = """借阅编号,书名,分类,读者,借出日期,归还日期
J001,三体,科幻,张三,2024-05-01,2024-05-15
J002,活着,文学,李四,2024-05-03,2024-05-10
J003,人类简史,历史,王五,2024-05-05,2024-05-20
J004,三体,科幻,李四,2024-05-08,
J005,呐喊,文学,张三,2024-05-11,2024-05-18
J006,时间简史,科普,王五,2024-05-12,2024-05-26
"""

DATE_FORMAT = "%Y-%m-%d"          # CSV 里日期的写法，配合 datetime.strptime 用


# =====================================================================
# 待办区：下面 4 个函数就是你要写的代码
# =====================================================================


def parse_records(csv_text: str) -> list[dict[str, str]]:
    """把 CSV 文本解析成记录列表，每条记录是一个 {列名: 值} 的字典"""
    # TODO(练习 4-1)：解析 CSV
    # 提示：
    #   1) `csv.DictReader(io.StringIO(csv_text))` 会自动把第一行当表头，
    #      之后每一行都变成一个 dict，直接用列名取值：row["分类"]
    #   2) 用列表推导过滤掉空行：`if row.get("借阅编号")`
    #   3) DictReader 是迭代器，用一次就空了，要 list(...) 存下来
    # 预期结果：
    #   len(parse_records(SAMPLE_CSV)) == 6
    #   parse_records(SAMPLE_CSV)[0]["书名"] == "三体"
    #   parse_records("") -> []（只有空字符串也不能报错）
    raise NotImplementedError("练习 4-1：解析 CSV")


def days_borrowed(record: dict[str, str]) -> int | None:
    """算这条记录借了多少天：借出日期 -> 归还日期；还没归还（归还日期为空）返回 None"""
    # TODO(练习 4-2)：算借阅天数（练 datetime）
    # 提示：
    #   1) 先看 `record["归还日期"]`：空字符串或缺失就 `return None`
    #   2) 用 `datetime.strptime(文本, DATE_FORMAT)` 把字符串变成 datetime 对象
    #   3) 两个 datetime 相减得到 timedelta，取 `.days` 就是天数（int）
    #   4) 别用字符串直接相减，那是错的；strftime 是反过来「把时间格式化成字符串」
    # 预期结果：
    #   days_borrowed({"借出日期": "2024-05-01", "归还日期": "2024-05-15"}) == 14
    #   days_borrowed({"借出日期": "2024-05-08", "归还日期": ""})            is None
    raise NotImplementedError("练习 4-2：算借阅天数")


def summary_by_category(records: list[dict[str, str]]) -> dict[str, int]:
    """按「分类」汇总借阅次数，返回 {分类: 次数}"""
    # TODO(练习 4-3)：按分类汇总
    # 提示：
    #   1) 可以用 `Counter(r["分类"] for r in records)`，再 dict(...) 转回来
    #   2) 也可以自己 for 循环累积：counts[cat] = counts.get(cat, 0) + 1
    #   3) 返回的是普通 dict（键是分类名，值是次数），不是列表
    # 预期结果：
    #   对 SAMPLE_CSV 来说 -> {"科幻": 2, "文学": 2, "历史": 1, "科普": 1}
    #   summary_by_category([]) -> {}
    raise NotImplementedError("练习 4-3：按分类汇总")


def format_report(records: list[dict[str, str]]) -> str:
    """拼出一份多行文本报告（返回值里用 \\n 换行，让调用方去 print）"""
    # TODO(练习 4-4)：输出格式化报告
    # 提示：
    #   1) 先把要用的数字都算出来：总记录数 len(records)、未归还条数（days_borrowed 返回 None 的条数）
    #   2) 分类汇总按「次数从多到少、次数相同按分类名」排序：
    #      sorted(summary.items(), key=lambda kv: (-kv[1], kv[0]))
    #   3) 平均借阅天数 = 已归还记录的 days 之和 / 已归还条数，保留 1 位小数：f"{avg:.1f}"
    #      没有任何已归还记录时要避免除以 0（返回 None 的记录不参与平均）
    #   4) 用列表收集每一行，最后 "\n".join(行列表) 返回，比反复 += 字符串快也更好读
    # 预期结果（行次序、空格、冒号全半角都随意，但关键字和数字必须对，自测用正则匹配）：
    #   图书借阅统计报告
    #   ================
    #   总记录数：6 条
    #   未归还：1 条
    #   分类汇总（共 4 个分类）：
    #     文学  2 次        <- 次数相同的按分类名排序，所以「文学」排在「科幻」前面
    #     科幻  2 次
    #     历史  1 次
    #     科普  1 次
    #   平均借阅天数：11.4 天
    raise NotImplementedError("练习 4-4：输出格式化报告")


# =====================================================================
# 入口：不用改
# =====================================================================
def main() -> int:
    passed = run_checks(CHECKS)
    if passed == len(CHECKS):
        print("\n你的报告长这样：")
        print(format_report(parse_records(SAMPLE_CSV)))
        total = sum(days_borrowed(r) or 0 for r in parse_records(SAMPLE_CSV))
        print(f"\n（自测小抄：所有已归还记录的天数之和 = {total}）")
        print("加分项：把报告写成 report.json，用 json.dump(..., ensure_ascii=False, indent=2)。")
    return 0


# =====================================================================
# 自测区：下面的代码不用改，它是你的「验收工具」
# =====================================================================
import re
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


# 自测用的固定数据（和 SAMPLE_CSV 内容一致，但写成了 Python 字面量）：
# 这样 4-2 / 4-3 / 4-4 的自测不依赖 4-1 是否正确，谁的 TODO 没做就报谁的行号
_SAMPLE_RECORDS: list[dict[str, str]] = [
    {"借阅编号": "J001", "书名": "三体", "分类": "科幻", "读者": "张三", "借出日期": "2024-05-01", "归还日期": "2024-05-15"},
    {"借阅编号": "J002", "书名": "活着", "分类": "文学", "读者": "李四", "借出日期": "2024-05-03", "归还日期": "2024-05-10"},
    {"借阅编号": "J003", "书名": "人类简史", "分类": "历史", "读者": "王五", "借出日期": "2024-05-05", "归还日期": "2024-05-20"},
    {"借阅编号": "J004", "书名": "三体", "分类": "科幻", "读者": "李四", "借出日期": "2024-05-08", "归还日期": ""},
    {"借阅编号": "J005", "书名": "呐喊", "分类": "文学", "读者": "张三", "借出日期": "2024-05-11", "归还日期": "2024-05-18"},
    {"借阅编号": "J006", "书名": "时间简史", "分类": "科普", "读者": "王五", "借出日期": "2024-05-12", "归还日期": "2024-05-26"},
]


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


def _expect(condition: bool, message: str) -> None:
    """把条件写成 assert，失败时带上人话消息"""
    assert condition, message


def _check_parse() -> None:
    """练习 4-1：解析"""
    records = parse_records(SAMPLE_CSV)
    _expect(isinstance(records, list), f"应该返回 list，实际 {type(records).__name__}")
    _expect(len(records) == 6, f"SAMPLE_CSV 有 6 条记录，你解析出 {len(records)} 条")
    _expect(isinstance(records[0], dict), f"每条记录应该是 dict，实际 {type(records[0]).__name__}")
    _expect(records[0]["书名"] == "三体", f"第一条的书名应该是三体，实际 {records[0].get('书名')!r}")
    _expect(records[0]["分类"] == "科幻", f"第一条的分类应该是科幻，实际 {records[0].get('分类')!r}")
    _expect(records[3]["归还日期"] == "", f"J004 的归还日期应该是空字符串，实际 {records[3].get('归还日期')!r}")
    _expect(parse_records("") == [], "只有空字符串时应该返回空列表")
    _expect(parse_records("借阅编号,书名,分类,读者,借出日期,归还日期\n") == [], "只有表头、没有数据行时应该返回空列表")
    _expect(parse_records(SAMPLE_CSV) == _SAMPLE_RECORDS, f"解析结果应该和 CSV 内容一一对应，实际 {parse_records(SAMPLE_CSV)}")


def _check_days() -> None:
    """练习 4-2：借阅天数（datetime）"""
    _expect(
        days_borrowed({"借出日期": "2024-05-01", "归还日期": "2024-05-15"}) == 14,
        "5-01 到 5-15 应该是 14 天",
    )
    _expect(
        days_borrowed({"借出日期": "2024-05-03", "归还日期": "2024-05-10"}) == 7,
        "5-03 到 5-10 应该是 7 天",
    )
    _expect(days_borrowed({"借出日期": "2024-05-08", "归还日期": ""}) is None, "未归还应该返回 None")
    _expect(days_borrowed({"借出日期": "2024-05-08"}) is None, "缺少归还日期这一列也应该返回 None")

    all_days = [days_borrowed(record) for record in _SAMPLE_RECORDS]
    _expect(all_days == [14, 7, 15, None, 7, 14], f"6 条记录的天数应该是 [14, 7, 15, None, 7, 14]，实际 {all_days}")
    _expect(sum(d or 0 for d in all_days) == 57, f"已归还记录天数之和应该是 57，实际 {sum(d or 0 for d in all_days)}")
    _expect(isinstance(date.today(), date), "顺带记住：date.today() 拿今天的日期，datetime.now() 拿此刻时间")


def _check_summary() -> None:
    """练习 4-3：按分类汇总"""
    summary = summary_by_category(_SAMPLE_RECORDS)
    _expect(isinstance(summary, dict), f"应该返回 dict，实际 {type(summary).__name__}")
    expected = {"科幻": 2, "文学": 2, "历史": 1, "科普": 1}
    _expect(summary == expected, f"分类汇总应该是 {expected}，实际 {summary}")
    _expect(summary_by_category([]) == {}, "空列表应该汇总成空字典")


def _check_report() -> None:
    """练习 4-4：报告格式（用正则宽松匹配，不挑空格和全半角）"""
    report = format_report(_SAMPLE_RECORDS)
    _expect(isinstance(report, str), f"应该返回 str，实际 {type(report).__name__}")
    _expect(report.count("\n") >= 5, f"报告至少要有 6 行，实际 {report.count(chr(10)) + 1} 行")
    _expect(re.search(r"总记录数\s*[：:]\s*6\s*条", report) is not None, f"报告里缺少「总记录数：6 条」，实际报告：\n{report}")
    _expect(re.search(r"未归还\s*[：:]\s*1\s*条", report) is not None, f"报告里缺少「未归还：1 条」，实际报告：\n{report}")
    _expect(
        re.search(r"平均借阅天数\s*[：:]\s*11\.4\s*天", report) is not None,
        f"平均借阅天数应该是 11.4（57 / 5，保留 1 位小数，未归还不参与），实际报告：\n{report}",
    )
    for category, count in (("科幻", 2), ("文学", 2), ("历史", 1), ("科普", 1)):
        pattern = rf"{category}\s*[：:]?\s*{count}\s*次"
        _expect(re.search(pattern, report) is not None, f"报告里缺少「{category} {count} 次」，实际报告：\n{report}")

    _expect("分类汇总" in report, "报告里要有「分类汇总」这一节")
    summary_part = report.split("分类汇总", 1)[1]
    expected_order = ["文学", "科幻", "历史", "科普"]     # 次数是 2 2 1 1，次数相同按分类名排序
    order = [summary_part.index(cat) for cat in expected_order]
    _expect(order == sorted(order), f"分类汇总要按次数从多到少、次数相同按分类名排序（文学在科幻前面），实际报告：\n{report}")

    empty_report = format_report([])
    _expect(isinstance(empty_report, str), "空记录也要能生成报告（不能崩、不能返回 None）")
    _expect(re.search(r"总记录数\s*[：:]\s*0\s*条", empty_report) is not None, "空记录时总记录数应该是 0 条")


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("练习 4-1：解析 CSV", _check_parse),
    ("练习 4-2：借阅天数 datetime", _check_days),
    ("练习 4-3：按分类汇总", _check_summary),
    ("练习 4-4：格式化报告", _check_report),
]


if __name__ == "__main__":
    raise SystemExit(main())
