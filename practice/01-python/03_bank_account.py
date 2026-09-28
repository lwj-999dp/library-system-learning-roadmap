"""练习 3：银行账户类（阶段 1 · Python 基础）

【题目要求】
    用面向对象写一个银行账户，学会「数据 + 行为」打包在一起：
      1. balance 用 @property 做成只读属性，外部只能看、不能直接改
      2. deposit  存款：金额必须 > 0，否则 ValueError
      3. withdraw 取款：金额必须 > 0；余额不够时抛自定义异常 InsufficientBalanceError
    类名、字段名、异常名都已经定好，你只补 3 个 TODO。

【验收标准】（对应 docs/01-Python基础.md 的「动手练习 · 练习 3」）
    [ ] python 03_bank_account.py 里 3 个自测项全部显示 [x]
    [ ] account.balance 能读；account.balance = 100 会报 AttributeError（只读属性）
    [ ] 余额不足抛的是 InsufficientBalanceError（它是 ValueError 的子类）
    [ ] 能说清 @property 解决了什么问题：防止外部绕过校验直接改坏余额

【路线图文档】../../docs/01-Python基础.md  （阶段 1 · Python 基础）

【怎么用这个文件】
    把每个方法里的 `raise NotImplementedError(...)` 换成你自己的实现。
    末尾的 assert 自测代码请勿删除 —— 那是你的验收工具。
"""

class InsufficientBalanceError(ValueError):
    """余额不足时抛的异常（继承 ValueError，所以老代码的 except ValueError 也接得住）"""


class BankAccount:
    """一个银行账户：能存、能取、能查余额，还会记账（history）"""

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner                 # 户主，公开属性，可以随便改
        self._balance = balance            # 余额，下划线开头表示「内部使用，别直接碰」
        self.history: list[str] = []       # 流水，每笔一条字符串

    # ------------------------------------------------------------------
    # TODO(练习 3-1)：把 balance 做成只读属性
    # 提示：
    #   1) 在方法上写 `@property` 装饰器，方法名就叫 balance
    #   2) 返回 self._balance 即可
    #   3) 只写 getter、不写 setter，外部写 account.balance = 1 就会 AttributeError
    # 预期结果：
    #   BankAccount("小明", 100).balance == 100
    #   account.balance = 999  -> AttributeError（这就是 @property 的价值）
    # ------------------------------------------------------------------

    @property
    def balance(self) -> float:
        """余额（只读）：外面只能读，想改必须走 deposit / withdraw"""
        raise NotImplementedError("练习 3-1：balance 只读属性")

    # ------------------------------------------------------------------
    # TODO(练习 3-2)：存款
    # 提示：
    #   1) `if amount <= 0:` -> raise ValueError("存款金额必须为正数")
    #   2) 通过校验后 `self._balance += amount`
    #   3) 顺手记一笔流水：`self.history.append(f"+{amount}")`
    #   4) 方法没有返回值（返回 None），不要写成 return self._balance
    # 预期结果：
    #   account.deposit(50)  -> balance 增加 50，history 多一条 "+50"
    #   account.deposit(0)   -> ValueError
    #   account.deposit(-5)  -> ValueError
    # ------------------------------------------------------------------
    def deposit(self, amount: float) -> None:
        """存款：amount 必须为正数，否则抛 ValueError"""
        raise NotImplementedError("练习 3-2：存款")

    # ------------------------------------------------------------------
    # TODO(练习 3-3)：取款
    # 提示：
    #   1) 先校验金额：`if amount <= 0:` -> raise ValueError("取款金额必须为正数")
    #   2) 再校验余额：`if amount > self._balance:` -> raise InsufficientBalanceError(...)
    #      异常消息里带上当前余额，方便排查：f"余额不足：当前 {self._balance}"
    #   3) 通过后 `self._balance -= amount`，并 append 一条 f"-{amount}" 流水
    #   4) 注意顺序：先校验再扣钱，绝不能先扣钱再报错
    # 预期结果：
    #   BankAccount("小明", 100).withdraw(30)  -> balance 变成 70
    #   withdraw(1000)                          -> InsufficientBalanceError
    #   withdraw(100)（余额刚好取光）             -> 成功，balance 变成 0
    # ------------------------------------------------------------------
    def withdraw(self, amount: float) -> None:
        """取款：金额为正且不超过余额，否则抛异常"""
        raise NotImplementedError("练习 3-3：取款")

    def __str__(self) -> str:
        """打印账户时好看一点（已经写好，不用改）"""
        return f"<BankAccount {self.owner} 余额 {self._balance}>"


# =====================================================================
# 入口：不用改
# =====================================================================
def main() -> int:
    passed = run_checks(CHECKS)
    if passed == len(CHECKS):
        account = BankAccount("小明", 100.0)
        print("\n演示（注意观察异常消息）：")
        account.deposit(50)
        print(f"  存入 50 后：{account}")
        account.withdraw(30)
        print(f"  取出 30 后：{account}")
        print(f"  流水：{account.history}")
        try:
            account.withdraw(9999)
        except InsufficientBalanceError as exc:
            print(f"  取 9999 被拦下：{exc}")
        print("\n加分项：写一个 CreditAccount(BankAccount)，允许透支 1000（重写 withdraw）。")
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


def _balance_ready(account: BankAccount) -> bool:
    """3-2 / 3-3 依赖 3-1 的 balance 属性：没写就给出明确提示，而不是指向错误的行号"""
    try:
        account.balance
    except NotImplementedError:
        return False
    return True


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


def _check_balance_property() -> None:
    """练习 3-1：只读属性"""
    account = BankAccount("小明", 100.0)
    assert account.balance == 100.0, f"balance 应该返回 100.0，实际 {account.balance!r}"
    assert BankAccount("小红").balance == 0.0, "默认余额应该是 0.0"

    try:
        account.balance = 999.0        # type: ignore[misc]  # 故意犯规，看会不会被拦住
    except AttributeError:
        pass
    else:
        raise AssertionError("balance 必须只读：只写 getter，不要写 setter")
    assert account.balance == 100.0, "外部改不动余额，账户必须还是 100.0"


def _check_deposit() -> None:
    """练习 3-2：存款（顺带检查流水）"""
    account = BankAccount("小明", 100.0)
    assert _balance_ready(account), "先完成练习 3-1（balance 只读属性），这一项才能自测"
    result = account.deposit(50)
    assert result is None, f"deposit 不应该有返回值，实际返回了 {result!r}"
    assert account.balance == 150.0, f"存 50 后应该是 150.0，实际 {account.balance}"
    assert len(account.history) == 1, f"存款后 history 应该有 1 条记录，实际 {account.history}"
    assert "50" in account.history[0], f"流水里应该能看到金额 50，实际 {account.history[0]!r}"

    for bad in (0, -1, -0.01):
        before = account.balance
        try:
            account.deposit(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"存款金额 {bad} 应该 raise ValueError")
        assert account.balance == before, f"存款金额 {bad} 被拒绝时，余额不能变"

    account.deposit(0.5)
    assert abs(account.balance - 150.5) < 1e-9, f"小数存款也要支持，实际 {account.balance}"


def _check_withdraw() -> None:
    """练习 3-3：取款（金额校验 + 余额校验 + 边界）"""
    account = BankAccount("小明", 100.0)
    assert _balance_ready(account), "先完成练习 3-1（balance 只读属性），这一项才能自测"
    account.withdraw(30)
    assert account.balance == 70.0, f"取 30 后应该是 70.0，实际 {account.balance}"
    assert len(account.history) == 1 and "30" in account.history[0], f"取款也应该记流水，实际 {account.history}"

    for bad in (0, -5):
        before = account.balance
        try:
            account.withdraw(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"取款金额 {bad} 应该 raise ValueError")
        assert account.balance == before, f"取款金额 {bad} 被拒绝时，余额不能变"

    try:
        account.withdraw(1000)
    except InsufficientBalanceError as exc:
        assert "70" in str(exc), f"异常消息里最好带上当前余额，实际 {str(exc)!r}"
    except ValueError as exc:
        raise AssertionError(f"应该抛 InsufficientBalanceError（不是普通 ValueError），实际 {type(exc).__name__}") from exc
    else:
        raise AssertionError("余额不足时必须抛 InsufficientBalanceError")
    assert account.balance == 70.0, "取款失败后余额不能被改动"

    account.withdraw(70)               # 刚好取光，属于合法操作
    assert account.balance == 0.0, f"余额刚好够时应该允许取光，实际 {account.balance}"

    assert issubclass(InsufficientBalanceError, ValueError), "InsufficientBalanceError 应该继承 ValueError"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("练习 3-1：balance 只读属性", _check_balance_property),
    ("练习 3-2：deposit 存款", _check_deposit),
    ("练习 3-3：withdraw 取款", _check_withdraw),
]


if __name__ == "__main__":
    raise SystemExit(main())
