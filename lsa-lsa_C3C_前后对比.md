# lsa-lsa_C3C_前后对比：学之前 vs 学之后

证据口径：所有「之后」能力均附可复核产物（代码文件、测试输出、Git 提交号、报告文本），不使用「感觉学会了」之类空泛表述。

## 一、搭档 lsa（A，CS 方向）

| 能力项 | 学之前 | 学之后 | 具体证据 |
|--------|--------|--------|----------|
| 年化收益计算 | 只知道「收益乘倍数」，说不出交易日口径 | 能按 252 交易日正确实现并解释外推局限 | `finance_metrics.py` 中 `annual_return`；`test_portfolio_metrics` 通过 |
| 夏普比率 | 听说过，不知道无风险利率怎么处理 | 能写 `(年化收益 - 2%) / 年化波动`，并处理分母为 0 | `portfolio_metrics()` 与 `test_bad_input` |
| 最大回撤 | 误以为是「最小值 - 起点」 | 能实现峰值到随后谷值的路径依赖算法 | 样例序列期望 0.0409，测试通过；教学记录 01 有纠错对话 |
| 预算健康度判读 | 只能报数字，给不出结论 | 独立产出 2026-11 判读：74.6 分 /「关注」/ 点名购物 3200 元为可控项 | 教学记录 03 第三节；`report.html` 第五节 |
| 主观权重意识 | 把输出当客观事实 | 主动在报告披露 6:4 权重且说明是教学设定 | `report.html` 页脚口径说明 |

**前后代码片段（最大回撤）：**

```python
# 学之前（A 的初稿，错误）
max_drawdown = min(values) - values[0]

# 学之后（按 B 的口径实现，正确）
peak = values[0]
max_drawdown = 0.0
for value in values:
    peak = max(peak, value)
    max_drawdown = max(max_drawdown, (peak - value) / peak)
```

## 二、搭档 lsa（B，非 CS 方向）

| 能力项 | 学之前 | 学之后 | 具体证据 |
|--------|--------|--------|----------|
| 运行 Python 文件 | 不知道 `.py` 怎么执行 | 能独立执行 `python analyze.py ...` 并解释输出 | 教学记录 02 终端输出；`report.html` 已生成 |
| CSV 读取与类型 | 手工表求和，常把文本数字当数字 | 能解释 `DictReader`、`utf-8-sig`、`float()` 的作用 | `tests/test_finance_metrics.py` 由 B 独立编写 |
| 函数与复用 | 每个表都从头改公式 | 能说明为何把读取逻辑封装成函数 | 学习笔记 lsaB 第 3 节 |
| 单元测试 | 认为测试是程序员的事 | 能写 6 条断言并用 `assertAlmostEqual` 处理精度 | `Ran 6 tests in 0.007s / OK` |
| Git 提交 | 从未提交过代码 | 独立完成 3 次提交，能区分告警与错误 | `41b2ff8`、`09120ad`、`d085c9c`，作者 lsa |
| 报告安全 | 不知道动态文本要转义 | 在 `sample_note` 上使用 `html.escape` | `analyze.py` 的 `build_report()` |

**前后命令能力（Git）：**

```bash
# 学之前：只会说「保存一下」
# 学之后：独立完成
$ git init -q
$ git config user.name lsa
$ git config user.email lsa@example.com
$ git add analyze.py
$ git commit -q -m "Teach CSV parsing and SVG report rendering"
$ git log --pretty=format:'%h | %an | %s'
09120ad | lsa | Teach CSV parsing and SVG report rendering
```

## 三、双向迁移是否成立

- A 从 B 学到的是**领域方法论**：指标口径、风险判读、权重披露；并在独立判读任务中被复核通过。
- B 从 A 学到的是**工程技术**：Python 数据处理、测试、Git；并独立提交代码改动。
- 两人各自都完成了「原本不会」的任务，方向相反，满足 CHALLENGE.md 规则 2 与 Level 3 要求。

## 四、仍未完全掌握的部分（诚实记录）

- B 仍不能独立设计 CLI 参数体系或 SVG 渲染逻辑，目前停留在复用与局部修改层面。
- A 仍不能在无领域清单的情况下自行设定财务评分权重，说明迁移的是「使用与校验方法」，不是领域专家身份。
- 这正说明 1+1>2 的边界：协作放大能力，但不等于互换专业。
