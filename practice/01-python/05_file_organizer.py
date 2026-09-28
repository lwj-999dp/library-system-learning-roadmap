"""练习 5：按扩展名整理文件（阶段 1 · Python 基础）

【题目要求】
    写一个「文件整理器」：把一个目录里的文件按扩展名分类，移到对应子目录里。
      1. scan_files   扫描目录下的文件（不递归、跳过隐藏文件、按名字排序）
      2. classify     根据扩展名决定分类（图片/文档/音频/视频/压缩包/代码/其他）
      3. build_plan   算出「哪个文件要移到哪」的计划表，先算清楚再动手
      4. move_file    执行移动；apply=False（默认）只返回说明文字，绝不碰磁盘文件

    ⚠️ 安全第一：本脚本**默认 dry-run**，只打印计划；加 --apply 才会真的移动。
       这是「先算计划、再执行」的经典写法，新手脚本最容易在这里误删文件。

【验收标准】（阶段 1 扩展练习：练 docs/01-Python基础.md「知识点 6 文件读写」里的 pathlib / 文件操作，并要求默认 dry-run）
    [ ] python 05_file_organizer.py 里 5 个自测项全部显示 [x]
    [ ] python 05_file_organizer.py <某个目录>            只打印计划，目录里文件一个不动
    [ ] python 05_file_organizer.py <某个目录> --apply    才真的移动，并打印每条结果
    [ ] 能说清 pathlib 比字符串拼路径好在哪（Path / 运算符、.suffix、.exists()）

【路线图文档】../../docs/01-Python基础.md  （阶段 1 · Python 基础）

【怎么用这个文件】
    把每个函数里的 `raise NotImplementedError(...)` 换成你自己的实现。
    先拿一个临时目录试手，别一上来就对自己的下载文件夹跑 --apply。
"""

import argparse
import shutil
from pathlib import Path

# 扩展名 -> 分类名（已经写好，不用改；想加新类型就往里加）
EXTENSION_MAP: dict[str, str] = {
    ".jpg": "图片", ".jpeg": "图片", ".png": "图片", ".gif": "图片", ".webp": "图片",
    ".pdf": "文档", ".docx": "文档", ".doc": "文档", ".txt": "文档", ".md": "文档", ".xlsx": "文档",
    ".mp3": "音频", ".wav": "音频", ".flac": "音频",
    ".mp4": "视频", ".mov": "视频", ".mkv": "视频",
    ".zip": "压缩包", ".rar": "压缩包", ".7z": "压缩包", ".gz": "压缩包", ".tar": "压缩包",
    ".py": "代码", ".js": "代码", ".ts": "代码", ".html": "代码", ".css": "代码", ".json": "代码",
}
FALLBACK_CATEGORY = "其他"      # 认不出来的扩展名（或根本没有扩展名）都归到这一类


# =====================================================================
# 待办区：下面 4 个函数就是你要写的代码
# =====================================================================


def scan_files(directory: Path) -> list[Path]:
    """列出目录下「直接子文件」，要求：不递归、跳过隐藏文件、按文件名字典序排好"""
    # TODO(练习 5-1)：扫描
    # 提示：
    #   1) `Path(directory).iterdir()` 拿到目录下所有条目（文件 + 子目录）
    #   2) 用 `p.is_file()` 过滤掉子目录（我们这一课不递归进子目录）
    #   3) 用 `not p.name.startswith(".")` 跳过 .gitignore 这类隐藏文件
    #   4) 排序用 key=lambda p: p.name.lower()，否则大小写不同的文件名排序会反直觉
    # 预期结果（假设目录里有 B.JPG、a.txt、.hidden.txt 和子目录 sub/）：
    #   [p.name for p in scan_files(目录)] -> ["a.txt", "B.JPG"]
    raise NotImplementedError("练习 5-1：扫描文件")


def classify(path: Path) -> str:
    """根据扩展名返回分类名；认不出来就返回 FALLBACK_CATEGORY"""
    # TODO(练习 5-2)：分类
    # 提示：
    #   1) `path.suffix` 直接给出扩展名，如 ".txt"；一定要 `.lower()`，
    #      否则 .JPG 会匹配不上表里的 ".jpg"
    #   2) 查表：`EXTENSION_MAP.get(后缀, FALLBACK_CATEGORY)`（get 的第二个参数是默认值）
    #   3) 没有扩展名（suffix 是空字符串）自然就落到「其他」
    # 预期结果：
    #   classify(Path("a.txt"))   -> "文档"
    #   classify(Path("b.JPG"))   -> "图片"（大小写不敏感）
    #   classify(Path("c"))       -> "其他"
    #   classify(Path("d.xyz"))   -> "其他"
    raise NotImplementedError("练习 5-2：分类")


def build_plan(files: list[Path], base_dir: Path) -> list[tuple[Path, Path]]:
    """算出整理计划：返回 [(源文件, 目标路径), ...]，目标路径 = base_dir / 分类 / 原文件名"""
    # TODO(练习 5-3)：生成计划
    # 提示：
    #   1) 用列表推导一次生成，返回的是「元组的列表」：[(src, dst), (src, dst), ...]
    #   2) 目标路径用 / 拼：`base_dir / classify(src) / src.name`（/ 比 os.path.join 好读）
    #   3) 源文件要**原样**放进元组，不要改成新 Path，否则调用方对不上号
    # 预期结果：
    #   build_plan([Path("a.txt")], Path("D:/tmp")) -> [(Path("a.txt"), Path("D:/tmp/文档/a.txt"))]
    #   build_plan([], 任意目录)                     -> []
    #   （加分项：如果目标已存在同名文件，改成 a-1.txt 避免覆盖）
    raise NotImplementedError("练习 5-3：生成计划")


def move_file(src: Path, dst: Path, *, apply: bool = False) -> str:
    """移动一个文件，返回一句说明文字。

    默认 apply=False（dry-run）：只返回「将要做什么」，磁盘上任何东西都不能变。
    apply=True 时才真的创建目录并移动文件。
    """
    # TODO(练习 5-4)：移动（默认 dry-run）
    # 提示：
    #   1) 先想清楚：dry-run 时函数应该在 return 之前就结束，绝不能走到 shutil.move
    #   2) apply=True 时：`dst.parent.mkdir(parents=True, exist_ok=True)` 先把分类目录建出来
    #      （exist_ok=True 表示目录已存在也不报错，parents=True 表示缺上级目录一起建）
    #   3) 再 `shutil.move(str(src), str(dst))`
    #   4) 返回的字符串建议：
    #      dry-run: f"[预览] {src.name} -> {dst.parent.name}/{dst.name}"
    #      已移动:  f"[已移动] {src.name} -> {dst.parent.name}/{dst.name}"
    # 预期结果：
    #   move_file(src, dst)              -> src 还在、dst 不存在，返回的文字里有「预览」
    #   move_file(src, dst, apply=True)  -> dst 存在、src 消失，返回的文字里有「已移动」
    raise NotImplementedError("练习 5-4：移动文件")


# =====================================================================
# 组织流程 + 命令行入口：不用改（它调用你写的 4 个函数）
# =====================================================================
def organize(directory: Path, *, apply: bool = False) -> list[str]:
    """扫描 -> 分类 -> 生成计划 -> 逐个移动，返回每一步的说明文字"""
    files = scan_files(directory)
    plan = build_plan(files, directory)
    return [move_file(src, dst, apply=apply) for src, dst in plan]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="按扩展名整理文件（默认 dry-run，只打印计划）",
        epilog="例：python 05_file_organizer.py D:/downloads          # 只看计划\n"
               "    python 05_file_organizer.py D:/downloads --apply  # 真的移动",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("directory", nargs="?", help="要整理的目录（不填就只跑自测）")
    parser.add_argument("--apply", action="store_true", help="真的移动文件；不加就是 dry-run")
    args = parser.parse_args()

    passed = run_checks(CHECKS)

    if args.directory is None:
        print("\n用法：python 05_file_organizer.py <目录> [--apply]")
        print("  不加 --apply = dry-run（默认）：只打印计划，绝不动你的文件")
        print("  建议先建个测试目录：mkdir D:/organize-demo 然后扔几个空文件进去")
        return 0

    if passed < len(CHECKS):
        print("\n还有 TODO 没做完，先补完再整理文件（免得半成品脚本乱搬你的东西）。")
        return 0

    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"\n找不到目录：{directory}（请确认路径写对，且是一个文件夹）")
        return 2

    mode = "真的移动（--apply）" if args.apply else "dry-run（只预览，不动文件）"
    print(f"\n模式：{mode}\n目录：{directory.resolve()}")
    print("-" * 70)
    messages = organize(directory, apply=args.apply)
    if not messages:
        print("这个目录里没有可整理的文件。")
    for message in messages:
        print("  " + message)
    print("-" * 70)
    if args.apply:
        print(f"完成：移动了 {len(messages)} 个文件。不满意就自己动手搬回去（这正是先看计划的意义）。")
    else:
        print(f"以上 {len(messages)} 条都只是预览。确认没问题后，加 --apply 再跑一次。")
    return 0


# =====================================================================
# 自测区：下面的代码不用改，它是你的「验收工具」
# =====================================================================
import tempfile
import traceback
import unicodedata
from collections.abc import Callable

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


def _make_demo_tree(root: Path) -> None:
    """造一棵测试用的小目录树：3 个文件 + 1 个隐藏文件 + 1 个子目录"""
    (root / "a.txt").write_text("hello", encoding="utf-8")
    (root / "B.JPG").write_text("fake image", encoding="utf-8")
    (root / ".hidden.txt").write_text("secret", encoding="utf-8")
    sub = root / "sub"
    sub.mkdir()
    (sub / "c.py").write_text("print(1)", encoding="utf-8")


def _check_scan() -> None:
    """练习 5-1：扫描"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_demo_tree(root)
        files = scan_files(root)
        assert isinstance(files, list), f"应该返回 list，实际 {type(files).__name__}"
        names = [p.name for p in files]
        assert names == ["a.txt", "B.JPG"], f"应该只返回 a.txt 和 B.JPG（跳过隐藏文件和子目录），实际 {names}"
        assert all(isinstance(p, Path) for p in files), "列表里每个元素都应该是 pathlib.Path"
        assert all(p.is_file() for p in files), "只返回文件，不能把子目录也返回"

        empty = root / "empty"
        empty.mkdir()
        assert scan_files(empty) == [], "空目录应该返回空列表"


def _check_classify() -> None:
    """练习 5-2：分类"""
    assert classify(Path("a.txt")) == "文档", "txt 应该归到文档"
    assert classify(Path("b.JPG")) == "图片", ".JPG 也要能匹配 .jpg（用 suffix.lower()）"
    assert classify(Path("c.mp4")) == "视频", "mp4 应该归到视频"
    assert classify(Path("d.zip")) == "压缩包", "zip 应该归到压缩包"
    assert classify(Path("e.py")) == "代码", "py 应该归到代码"
    assert classify(Path("noext")) == FALLBACK_CATEGORY, "没有扩展名的文件应该归到「其他」"
    assert classify(Path("weird.xyz")) == FALLBACK_CATEGORY, "认不出来的扩展名应该归到「其他」"
    assert classify(Path("archive.tar.gz")) == "压缩包", "多重扩展名只看最后一个（.gz）"


def _check_build_plan() -> None:
    """练习 5-3：生成计划"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src_txt = root / "a.txt"
        src_jpg = root / "b.JPG"
        base = root / "base"
        plan = build_plan([src_txt, src_jpg], base)
        expected = [
            (src_txt, base / "文档" / "a.txt"),
            (src_jpg, base / "图片" / "b.JPG"),
        ]
        assert plan == expected, f"计划应该是 {expected}，实际 {plan}"
        assert build_plan([], base) == [], "没有文件时计划应该是空列表"
        assert not base.exists(), "光生成计划不能碰磁盘（base 目录不该被创建）"
        assert not (base / "文档").exists(), "生成计划时不能创建任何目录"


def _check_move_dry_run() -> None:
    """练习 5-4（上）：dry-run 绝对不能动文件"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src = root / "a.txt"
        src.write_text("hello", encoding="utf-8")
        dst = root / "文档" / "a.txt"

        message = move_file(src, dst)
        assert isinstance(message, str), f"应该返回说明文字（str），实际 {type(message).__name__}"
        assert src.exists(), "dry-run 时源文件必须原地不动"
        assert not dst.exists(), "dry-run 时目标文件不能被创建"
        assert not dst.parent.exists(), "dry-run 时连分类目录都不能创建"
        assert ("预览" in message) or ("dry" in message.lower()), f"dry-run 的说明文字里要有「预览」，实际 {message!r}"
        assert "a.txt" in message, f"说明文字里要能看到文件名，实际 {message!r}"


def _check_move_apply() -> None:
    """练习 5-4（下）：apply=True 才真的移动"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src = root / "a.txt"
        src.write_text("hello", encoding="utf-8")
        dst = root / "文档" / "a.txt"

        message = move_file(src, dst, apply=True)
        assert dst.exists(), f"apply=True 时目标文件应该存在：{dst}"
        assert not src.exists(), "apply=True 时源文件应该已经被移走"
        assert dst.read_text(encoding="utf-8") == "hello", "移动后文件内容不能变"
        assert ("已移动" in message) or ("moved" in message.lower()), f"说明文字里要有「已移动」，实际 {message!r}"

        # 再顺手验证一下 organize 全流程（它用你写的 4 个函数串起来）
        root2 = root / "second"
        root2.mkdir()
        (root2 / "note.md").write_text("x", encoding="utf-8")
        (root2 / "pic.png").write_text("x", encoding="utf-8")
        messages = organize(root2, apply=False)
        assert len(messages) == 2, f"organize 应该返回 2 条预览，实际 {len(messages)} 条"
        assert (root2 / "note.md").exists() and (root2 / "pic.png").exists(), "organize 的默认行为必须是 dry-run"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("练习 5-1：扫描目录", _check_scan),
    ("练习 5-2：按扩展名分类", _check_classify),
    ("练习 5-3：生成整理计划", _check_build_plan),
    ("练习 5-4：dry-run 预览", _check_move_dry_run),
    ("练习 5-5：apply 真正移动", _check_move_apply),
]


if __name__ == "__main__":
    raise SystemExit(main())
