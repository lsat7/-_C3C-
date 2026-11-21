# 个人收支与投资组合分析工具（C3C 联合产出）

由搭档 lsa（CS 方向）与搭档 lsa（金融方向）联合完成：一人提供领域口径与验收标准，一人提供工程实现与自动化验证。

## 功能

- 读取收支流水 CSV，按月汇总收入、支出、净结余与结余率
- 统计支出科目占比，输出全期与最新月份两视图
- 读取净值序列，计算累计收益、年化收益、年化波动、夏普比率、最大回撤
- 按「预算控制 60% + 结余率 40%」输出预算健康度评分与建议
- 生成零依赖、可离线打开的 HTML 报告（内联 SVG 图表，无 JS、无 CDN）

## 环境要求

- Python 3.8 及以上（实测 Python 3.13.14）
- 不需要安装任何第三方库
- Git（仅复现提交记录时需要；运行工具本身不需要）

## 运行

在本目录执行：

```bash
python analyze.py --transactions data/transactions.csv --nav data/nav.csv --budget 8000 --out report.html
```

参数说明：

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `--transactions` | `data/transactions.csv` | 收支流水 CSV |
| `--nav` | `data/nav.csv` | 净值序列 CSV |
| `--budget` | `8000` | 月度预算（元） |
| `--out` | `report.html` | 报告输出路径 |

实测输出：

```
已生成报告: .../report.html
交易记录: 21 条 / 月份: 3 个
最新月份: 2026-11 健康度 74.6 (关注)
年化收益 387.54% / 夏普 16.504 / 最大回撤 4.09%
```

## 数据格式

`data/transactions.csv`：`date,category,amount,type,note`，其中 `type` 只能是 `income` 或 `expense`。

`data/nav.csv`：`date,nav`，净值必须为正数，程序按日期自动升序排列。

## 测试

```bash
python -m unittest discover -s tests -v
```

实测结果：`Ran 6 tests in 0.007s / OK`。覆盖加载、按月汇总、科目占比、组合指标、预算评分与异常输入。

## 目录结构

```
.
├── analyze.py              CLI 入口与 HTML 渲染
├── finance_metrics.py      领域规则模块（金融搭档定义口径）
├── data/
│   ├── transactions.csv    收支样例数据
│   └── nav.csv             净值样例数据
├── tests/
│   └── test_finance_metrics.py
└── report.html             实际生成的报告（可直接双击打开）
```

## 已复用的对方技能

- 金融搭档 lsa：252 交易日年化、`(年化收益 - 2%) / 年化波动` 的夏普口径、峰值—谷值最大回撤、预算健康度加权评分，已固化为 `finance_metrics.py` 与 6 条单元测试。
- CS 搭档 lsa：CSV 解析、函数封装、SVG 无依赖渲染、unittest 自动化验证与 Git 版本管理，已被另一搭档在独立任务中复用。

## 已知限制

- 年化指标在短样本上会显著放大：当前 15 个净值点对应约 2.5 个月，年化收益 387.54% 只是公式外推，报告和本文档均已标注警示，不可用于投资决策。
- 净值序列按等间隔交易日近似处理，未拆解节假日与真实交易日历。
- 预算健康度为教学用简化模型，未纳入收入波动、负债与通胀因素。
