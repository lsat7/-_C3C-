# C3C 联合成果（交付物说明）

本文件是 C3C「双人协作与技能迁移」的**联合成果说明**，可运行的完整产出位于
[`lsa-lsa_C3C_联合产出/`](./lsa-lsa_C3C_联合产出/)。

## 成果是什么

一个**零第三方依赖**的个人收支与投资组合分析工具：读取收支流水与净值序列 CSV，
输出月度汇总、支出科目占比、累计/年化收益、年化波动、夏普比率、最大回撤、
预算健康度评分，并生成**可离线双击打开**的 HTML 报告（内联 SVG 图表，无 JS、无 CDN）。
用 Python 标准库实现，不需要安装任何第三方包。

## 分工与联合方式

- 搭档 lsa（B，金融方向）：提供领域口径与验收标准——年化收益、夏普比率、最大回撤、
  预算健康度权重的定义与边界条件；
- 搭档 lsa（A，CS 方向）：提供工程实现与自动化验证——数据读取、指标计算模块、
  报告生成、单元测试与 Git 提交记录。

## 交付物清单

| 文件 | 说明 |
|---|---|
| [`analyze.py`](./lsa-lsa_C3C_联合产出/analyze.py) | 项目入口：读取 CSV → 计算指标 → 生成 HTML 报告 |
| [`finance_metrics.py`](./lsa-lsa_C3C_联合产出/finance_metrics.py) | 领域模块：年化收益、波动、夏普、最大回撤、健康度评分 |
| [`data/transactions.csv`](./lsa-lsa_C3C_联合产出/data/transactions.csv) | 收支流水样例数据（21 条 / 3 个月） |
| [`data/nav.csv`](./lsa-lsa_C3C_联合产出/data/nav.csv) | 净值序列样例数据 |
| [`report.html`](./lsa-lsa_C3C_联合产出/report.html) | 已生成的离线 HTML 报告 |
| [`tests/test_finance_metrics.py`](./lsa-lsa_C3C_联合产出/tests/test_finance_metrics.py) | 单元测试：6 条，覆盖各口径与边界（含除零） |
| [`README.md`](./lsa-lsa_C3C_联合产出/README.md) | 运行方式、参数说明、数据格式 |

## 复现方式

```bash
cd lsa-lsa_C3C_联合产出
python analyze.py --transactions data/transactions.csv --nav data/nav.csv --budget 8000 --out report.html
python -m unittest discover -s tests -v
```

## 实测结果（可复核）

```
已生成报告: .../report.html
交易记录: 21 条 / 月份: 3 个
最新月份: 2026-11 健康度 74.6 (关注)
年化收益 387.54% / 夏普 16.504 / 最大回撤 4.09%
```

- 单元测试：`Ran 6 tests ... OK`
- 关于年化收益 387.54%：净值序列仅 15 个点，报告已按第 3 次会话的结论加入
  **样本量警示**（`obs < 60` 时提示年化指标仅供参考），避免用短样本外推误导读者。

## 相关材料

- 协作记录：[`lsa-lsa_C3C_协作记录.md`](./lsa-lsa_C3C_协作记录.md)
- 前后对比：[`lsa-lsa_C3C_前后对比.md`](./lsa-lsa_C3C_前后对比.md)
- AI 使用日志：[`lsa-lsa_C3C_AI日志.md`](./lsa-lsa_C3C_AI日志.md)
- 复盘（AAR）：[`lsa-lsa_C3C_AAR.md`](./lsa-lsa_C3C_AAR.md)
