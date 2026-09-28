# 阶段 1 · Python 基础练习（脚手架）

> **这里不是答案，也不是空文件，而是「自带自测的填空题」。**
> 每个文件都能直接运行，跑一下就知道自己哪几项还没做、错在哪。

对应文档：[`docs/01-Python基础.md`](../../docs/01-Python基础.md) ｜ 预计总耗时：约 20 h（官方建议）

---

## 5 个练习

| 文件 | 练什么 | 预计耗时 | 自测项 | 验收标准 |
|---|---|:---:|:---:|---|
| [`01_contacts.py`](01_contacts.py) | dict / list / 函数 / 循环 / input | 3 h | 4 项 | 增删查列 4 个函数全绿，并能进入交互模式敲命令 |
| [`02_wordcount.py`](02_wordcount.py) | 文件读写 / 字符串 / `Counter` / 排序 | 4 h | 5 项 | 切词正确、`SAMPLE_TEXT` 统计出 python=3、Top3 稳定有序 |
| [`03_bank_account.py`](03_bank_account.py) | 类 / `@property` / 异常 / 自定义异常 | 4 h | 3 项 | 余额只读、金额校验、余额不足抛 `InsufficientBalanceError` |
| [`04_csv_report.py`](04_csv_report.py) | `csv` / `io.StringIO` / 列表推导 / `datetime` | 5 h | 4 项 | 解析 6 条记录、分类汇总、平均借阅天数 11.4 |
| [`05_file_organizer.py`](05_file_organizer.py) | `pathlib` / `shutil` / dry-run 安全设计 | 4 h | 5 项 | 扫描/分类/计划正确，**默认 dry-run 不动任何文件** |

---

## 怎么运行

```powershell
cd practice/01-python
python 01_contacts.py        # 自带自测，不需要装任何第三方库
python 02_wordcount.py
python 03_bank_account.py
python 04_csv_report.py
python 05_file_organizer.py            # 只看自测
python 05_file_organizer.py D:\demo    # 预览整理计划（dry-run，不动文件）
python 05_file_organizer.py D:\demo --apply   # 确认无误后才真的移动
```

只有 Python 3.12+ 标准库，**不用 pip install 任何东西**。

运行后你会看到：

```
======================================================================
[ ] 练习 4-1：解析 CSV          —— 未完成（第 58 行 TODO）
[x] 练习 4-2：借阅天数 datetime  —— 通过
[!] 练习 4-3：按分类汇总         —— 报错：KeyError: '分类'
----------------------------------------------------------------------
进度：1/4 项通过
```

三种标记的含义：

| 标记 | 含义 | 你该做什么 |
|---|---|---|
| `[ ] …… 未完成（第 X 行 TODO）` | 那个函数还是 `raise NotImplementedError` 占位 | 跳到第 X 行，读 TODO 上方的「提示」和「预期结果」 |
| `[ ] …… 未通过：……` | 代码写了，但结果和预期不符 | 消息里写清了期望值和实际值，对着改 |
| `[!] …… 报错：XxxError` | 代码抛异常了（比如 `KeyError`） | 先用 `print` 打出中间结果定位 |
| `[x] …… 通过` | 这一项过关 | 继续下一项 |

---

## 怎么判断自己做完了

1. **一个文件里的自测项全部 `[x]`** —— 这个练习算过关；
2. 对照**文件顶部的「验收标准」**逐条自查（那里还有人能回答的问题）；
3. 对照 [`docs/01-Python基础.md`](../../docs/01-Python基础.md) 的「🏁 验收标准」整章自查；
4. 每个练习单独 `git commit` 一次（文档要求阶段 1 至少 20 次提交）。

> ⚠️ 自测通过 ≠ 学会了。**改完代码后，把 TODO 上方的注释盖住，从空白处再默写一遍函数体**，
> 能一次默写出来才是真的会了。

---

## 三条规则

| 规则 | 说明 |
|---|---|
| ✅ 先自己写，卡住 30 分钟再看文档 | 直接搜答案 = 白学，面试时手写不出来 |
| ✅ 看文档，不看答案 | 卡住先翻 [`docs/01-Python基础.md`](../../docs/01-Python基础.md) 对应小节，再翻[官方教程](https://docs.python.org/zh-cn/3/tutorial/) |
| ✅ 改坏了大不了重来 | 每个文件都能单独运行，删掉重写比反复纠结快 |
| ❌ 不要删掉末尾的 assert 自测代码 | 那是你的验收工具；只能往里加，不能删 |

## 常见问题

| 现象 | 原因 |
|---|---|
| `SyntaxError: 'gbk' codec can't decode ...` | 文件被别的编辑器存成了 GBK：用 VS Code 另存为 UTF-8 |
| Windows 控制台里中文变乱码 | 文件本身是 UTF-8，`python 文件名.py` 输出一般正常；乱码时先 `chcp 65001` |
| `IndentationError` | Tab 和空格混用了，VS Code 里设置「插入空格」、缩进 4 格 |
| `[!] 报错：AttributeError: 'NoneType'` | 函数没写 `return`，默认返回 `None`，调用方却按有返回值用 |
| 运行 `05_file_organizer.py` 好像没反应 | dry-run 默认只打印计划，不加 `--apply` 不会移动任何文件（这是故意的） |

[← 返回练习总览](../README.md) ｜ [阶段 1 文档](../../docs/01-Python基础.md) ｜ [里程碑](../../milestones.md)
