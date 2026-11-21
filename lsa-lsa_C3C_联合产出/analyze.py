#!/usr/bin/env python3
"""analyze.py — 个人收支与投资组合分析工具（C3C 联合产出）

用法：
    python analyze.py --transactions data/transactions.csv \
                      --nav data/nav.csv --budget 8000 --out report.html

只需要 Python 3.8+，不依赖任何第三方库。
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import finance_metrics as fm

PALETTE = ["#2563eb", "#0891b2", "#16a34a", "#d97706", "#dc2626", "#7c3aed"]


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def money(value: float) -> str:
    return f"¥{value:,.2f}"


def svg_bar(items: list[dict]) -> str:
    """支出占比横向条形图（纯 SVG，无 JS）。"""
    if not items:
        return "<p>无支出数据</p>"
    rows = []
    for idx, item in enumerate(items):
        y = 20 + idx * 34
        width = max(2, item["share"] * 520)
        color = PALETTE[idx % len(PALETTE)]
        rows.append(
            f'<text x="8" y="{y + 13}" font-size="12" fill="#1f2937">'
            f'{html.escape(item["category"])}</text>'
            f'<rect x="96" y="{y}" width="{width:.1f}" height="18" rx="3" fill="{color}"/>'
            f'<text x="{96 + width + 8:.1f}" y="{y + 13}" font-size="12" fill="#374151">'
            f'{pct(item["share"])}</text>'
        )
    height = 40 + len(items) * 34
    return (
        f'<svg viewBox="0 0 760 {height}" width="100%" role="img" '
        f'aria-label="支出科目占比条形图">'
        f'{"".join(rows)}</svg>'
    )


def svg_line(nav_rows: list[dict]) -> str:
    """净值折线图（纯 SVG，无 JS）。"""
    values = [r["nav"] for r in nav_rows]
    low, high = min(values), max(values)
    span = high - low or 1
    points = []
    for idx, value in enumerate(values):
        x = 60 + idx * (640 / max(1, len(values) - 1))
        y = 190 - (value - low) / span * 150
        points.append(f"{x:.1f},{y:.1f}")
    poly = " ".join(points)
    dots = "".join(
        f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="3" fill="#2563eb"/>'
        for p in points
    )
    return (
        '<svg viewBox="0 0 760 230" width="100%" role="img" aria-label="净值走势折线图">'
        f'<line x1="60" y1="190" x2="700" y2="190" stroke="#9ca3af"/>'
        f'<line x1="60" y1="40" x2="60" y2="190" stroke="#9ca3af"/>'
        f'<polyline points="{poly}" fill="none" stroke="#2563eb" stroke-width="2"/>'
        f'{dots}'
        f'<text x="8" y="46" font-size="11" fill="#6b7280">{high:.3f}</text>'
        f'<text x="8" y="190" font-size="11" fill="#6b7280">{low:.3f}</text>'
        f'<text x="60" y="215" font-size="11" fill="#6b7280">{html.escape(nav_rows[0]["date"])}</text>'
        f'<text x="620" y="215" font-size="11" fill="#6b7280">{html.escape(nav_rows[-1]["date"])}</text>'
        "</svg>"
    )


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def build_report(transactions, nav_rows, budget: float) -> str:
    monthly = fm.monthly_summary(transactions)
    shares = fm.category_share(transactions)
    latest_shares = fm.category_share(transactions, monthly[-1]["month"])
    perf = fm.portfolio_metrics(nav_rows)
    health = fm.budget_health(monthly[-1], budget)
    sample_note = (
        "样本仅 %d 个观测点（不足 60 个），年化收益与夏普比率为短样本外推值，"
        "只用于演示计算口径，不构成投资判断。" % perf["observations"]
        if perf["observations"] < 60
        else "样本量满足基本统计参考要求。"
    )

    monthly_table = table(
        ["月份", "收入", "支出", "净结余", "结余率"],
        [
            [m["month"], money(m["income"]), money(m["expense"]),
             money(m["net"]), pct(m["savings_rate"])]
            for m in monthly
        ],
    )
    share_table = table(
        ["支出科目", "金额", "占比"],
        [[s["category"], money(s["amount"]), pct(s["share"])] for s in shares],
    )
    perf_table = table(
        ["指标", "数值", "口径说明"],
        [
            ["区间", f'{perf["start_date"]} ~ {perf["end_date"]}', f'{perf["observations"]} 个观测点'],
            ["累计收益", pct(perf["total_return"]), "末值/初值 - 1"],
            ["年化收益", pct(perf["annual_return"]), "252 交易日年化"],
            ["年化波动", pct(perf["annual_volatility"]), "日收益标准差 × √252"],
            ["夏普比率", str(perf["sharpe_ratio"]), "(年化收益 - 2%) / 年化波动"],
            ["最大回撤", pct(perf["max_drawdown"]), "历史峰值至随后谷值最大跌幅"],
        ],
    )
    health_table = table(
        ["月份", "预算", "预算控制分", "结余率分", "综合分", "结论", "建议"],
        [[health["month"], money(health["monthly_budget"]), health["budget_score"],
          health["savings_score"], health["score"], health["label"], health["advice"]]],
    )
    latest_table = table(
        ["科目", "金额", "占比"],
        [[s["category"], money(s["amount"]), pct(s["share"])] for s in latest_shares],
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>C3C 个人财务分析报告</title>
<style>
:root {{ color-scheme: light; }}
body {{ margin: 0; padding: 32px; background: #f5f7fb; color: #1f2937;
       font-family: "Microsoft YaHei", "PingFang SC", system-ui, sans-serif; }}
main {{ max-width: 1000px; margin: 0 auto; background: #fff; padding: 32px;
        border-radius: 14px; box-shadow: 0 8px 28px rgba(15,23,42,.08); }}
h1 {{ margin: 0 0 4px; font-size: 26px; }}
h2 {{ margin-top: 32px; font-size: 18px; border-left: 4px solid #2563eb;
      padding-left: 10px; }}
.sub {{ color: #6b7280; margin-bottom: 24px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }}
th, td {{ border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; }}
th {{ background: #eff6ff; }}
.badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px;
          background: #dbeafe; color: #1d4ed8; font-weight: 600; }}
footer {{ margin-top: 36px; padding-top: 16px; border-top: 1px solid #e5e7eb;
          color: #6b7280; font-size: 12px; }}
</style>
</head>
<body>
<main>
<h1>个人收支与投资组合分析报告</h1>
<p class="sub">C3C 联合产出 · 生成工具 analyze.py · 领域口径 finance_metrics.py</p>
<p>最新月份 <span class="badge">{html.escape(health["month"])}</span> 预算健康度：
<strong>{health["score"]} 分（{health["label"]}）</strong></p>

<h2>一、逐月收支汇总</h2>
{monthly_table}

<h2>二、全期支出结构</h2>
{share_table}
{svg_bar(shares)}

<h2>三、最新月份支出结构（{html.escape(health["month"])}）</h2>
{latest_table}

<h2>四、投资组合表现</h2>
{perf_table}
<p>{html.escape(sample_note)}</p>
{svg_line(nav_rows)}

<h2>五、预算健康度判读</h2>
{health_table}
<p>{html.escape(health["advice"])}</p>

<footer>
数据来源：data/transactions.csv、data/nav.csv｜
计算口径：252 交易日年化、无风险利率 2%、预算控制 60% + 结余率 40%｜{html.escape(sample_note)}｜
生成方式：python analyze.py --transactions data/transactions.csv --nav data/nav.csv --budget {budget} --out report.html
</footer>
</main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="生成个人财务 HTML 分析报告")
    parser.add_argument("--transactions", default="data/transactions.csv")
    parser.add_argument("--nav", default="data/nav.csv")
    parser.add_argument("--budget", type=float, default=8000.0)
    parser.add_argument("--out", default="report.html")
    args = parser.parse_args()

    transactions = fm.load_transactions(args.transactions)
    nav_rows = fm.load_nav(args.nav)
    report = build_report(transactions, nav_rows, args.budget)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    monthly = fm.monthly_summary(transactions)
    perf = fm.portfolio_metrics(nav_rows)
    health = fm.budget_health(monthly[-1], args.budget)
    print(f"已生成报告: {out_path.resolve()}")
    print(f"交易记录: {len(transactions)} 条 / 月份: {len(monthly)} 个")
    print(f"最新月份: {health['month']} 健康度 {health['score']} ({health['label']})")
    print(f"年化收益 {pct(perf['annual_return'])} / 夏普 {perf['sharpe_ratio']} / 最大回撤 {pct(perf['max_drawdown'])}")


if __name__ == "__main__":
    main()
