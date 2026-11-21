# lsa-lsa_C3C_学习笔记_搭档 B（姓名 lsa）

- 对应教学：第 2 次会话（2026-11-18），搭档 lsa（A）教我 Python 与 Git
- 学习方向：CS → 非 CS
- 学习方：搭档 lsa（B）

## 一、学了什么

1. **CSV 读取**：`csv.DictReader` 把表头映射成字典键；金额是字符串，
   必须 `float(raw["amount"])` 才能参与计算。
2. **编码处理**：读 Excel 导出的 CSV 要用 `encoding="utf-8-sig"`，
   否则表头会带 BOM 字符，取不到 `date` 字段。
3. **函数封装**：重复读取两个数据文件，写成
   `load_transactions(path)` / `load_nav(path)`，换数据只改参数。
4. **单元测试**：`assertEqual` 用于条数、月份等确定值；
   比率等浮点数用 `assertAlmostEqual`，并指定精度位数。
5. **Git 最小工作流**：`git init` → `git config user.name/user.email` →
   `git add` → `git commit -m` → `git log` 查看历史；`git status` 确认工作区干净。
6. **HTML 安全**：把动态文本写进报告前用 `html.escape`，避免特殊字符破坏页面。

## 二、卡在哪里

- **卡点 1：打开 CSV 表头乱码。** 我用 `utf-8` 读，`raw["date"]` 一直报 KeyError。
  看不懂报错里的 `\ufeff` 是什么意思。
- **卡点 2：字符串直接相加。** 我写 `total += raw["amount"]`，
  得到的是字符串拼接，结果完全不对，一时不知道问题在哪。
- **卡点 3：浮点断言总失败。** `assertEqual(0.1 + 0.2, 0.3)` 失败，
  我以为是公式写错了。
- **卡点 4：把 Git 告警当报错。** 看到
  `LF will be replaced by CRLF` 就以为提交失败，
  其实 `git log` 已经有记录了。

## 三、怎么突破的

1. lsa（A）让我打印 `list(raw.keys())`，看到 `\ufeffdate` 后改用
   `utf-8-sig`，立刻解决；我把这一步写进自己的排查笔记。
2. 在读取时显式 `float()` 转换，并用 `type()` 打印确认是 `float` 而不是 `str`。
3. 改用 `assertAlmostEqual(..., places=3)`，理解浮点误差是表示问题，不是逻辑错误。
4. 用 `git status --short` 验证：无输出即工作区干净；告警只是换行风格提示。
5. 由我独立念命令完成一次提交，lsa（A）全程不动手，提交号 `41b2ff8`。
6. 在第 3 次会话中，我独立给 `analyze.py` 加样本量警示并提交
   `09120ad`、`d085c9c`，把学到的 `html.escape` 真正用在改动里。

## 四、学完之后能独立做到的事

不看搭档提示，我可以独立完成：读取一个新的 CSV、写断言测试、用 Git 提交一次改动、
读懂终端输出并区分告警与错误。虽然还不能从零设计大型程序，
但已经能把手工财务规则变成可重复运行的工具。

## 五、证据

- `../lsa-lsa_C3C_教学记录/02_第2次教学会话_A教B.md`（聊天记录与终端输出）
- Git 提交：`41b2ff8`、`09120ad`、`d085c9c`，作者均为 lsa
- `../lsa-lsa_C3C_联合产出/tests/test_finance_metrics.py`
- `python -m unittest discover -s tests -v` → `Ran 6 tests ... OK`
