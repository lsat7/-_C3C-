"""finance_metrics.py

领域规则模块：由搭档 lsa（金融背景）定义公式与判读口径，
搭档 lsa（CS 背景）负责实现为可复用 Python 模块。

本模块只依赖 Python 标准库，可独立导入使用。
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

TRADING_DAYS = 252
RISK_FREE_RATE = 0.02


def load_transactions(path: str | Path) -> list[dict]:
    """读取收支流水 CSV，返回规范化记录列表。"""
    rows = []
    with Path(path).open(encoding="utf-8-sig", newline="") as fh:
        for raw in csv.DictReader(fh):
            rows.append(
                {
                    "date": raw["date"].strip(),
                    "month": raw["date"].strip()[:7],
                    "category": raw["category"].strip(),
                    "amount": float(raw["amount"]),
                    "type": raw["type"].strip().lower(),
                    "note": raw.get("note", "").strip(),
                }
            )
    return rows


def load_nav(path: str | Path) -> list[dict]:
    """读取净值序列 CSV，按日期升序返回。"""
    rows = []
    with Path(path).open(encoding="utf-8-sig", newline="") as fh:
        for raw in csv.DictReader(fh):
            rows.append({"date": raw["date"].strip(), "nav": float(raw["nav"])})
    return sorted(rows, key=lambda r: r["date"])


def monthly_summary(transactions: list[dict]) -> list[dict]:
    """按月汇总收入、支出、净结余与结余率。"""
    bucket: dict[str, dict] = defaultdict(
        lambda: {"income": 0.0, "expense": 0.0}
    )
    for tx in transactions:
        if tx["type"] == "income":
            bucket[tx["month"]]["income"] += tx["amount"]
        elif tx["type"] == "expense":
            bucket[tx["month"]]["expense"] += tx["amount"]
        else:
            raise ValueError(f"未知交易类型: {tx['type']}")
    result = []
    for month in sorted(bucket):
        income = round(bucket[month]["income"], 2)
        expense = round(bucket[month]["expense"], 2)
        net = round(income - expense, 2)
        savings_rate = round(net / income, 4) if income > 0 else 0.0
        result.append(
            {
                "month": month,
                "income": income,
                "expense": expense,
                "net": net,
                "savings_rate": savings_rate,
            }
        )
    return result


def category_share(transactions: list[dict], month: str | None = None) -> list[dict]:
    """支出科目占比，按金额降序。month 为 None 时统计全部月份。"""
    bucket: dict[str, float] = defaultdict(float)
    for tx in transactions:
        if tx["type"] != "expense":
            continue
        if month is not None and tx["month"] != month:
            continue
        bucket[tx["category"]] += tx["amount"]
    total = sum(bucket.values())
    return [
        {
            "category": category,
            "amount": round(amount, 2),
            "share": round(amount / total, 4) if total else 0.0,
        }
        for category, amount in sorted(bucket.items(), key=lambda kv: -kv[1])
    ]


def portfolio_metrics(nav_rows: list[dict]) -> dict:
    """计算年化收益、年化波动、夏普比率与最大回撤。

    口径由金融搭档 lsa 指定：252 交易日年化，无风险利率 2%，
    最大回撤取历史峰值到随后谷值的最大跌幅，以正数百分比返回。
    """
    values = [r["nav"] for r in nav_rows]
    if len(values) < 2:
        raise ValueError("净值序列至少需要 2 个点")
    if any(v <= 0 for v in values):
        raise ValueError("净值必须为正数")

    returns = [values[i] / values[i - 1] - 1 for i in range(1, len(values))]
    years = len(returns) / TRADING_DAYS
    total_return = values[-1] / values[0] - 1
    annual_return = (values[-1] / values[0]) ** (1 / years) - 1

    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    volatility = math.sqrt(variance) * math.sqrt(TRADING_DAYS)
    sharpe = (
        (annual_return - RISK_FREE_RATE) / volatility if volatility > 0 else 0.0
    )

    peak = values[0]
    max_drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        max_drawdown = max(max_drawdown, (peak - value) / peak)

    return {
        "start_date": nav_rows[0]["date"],
        "end_date": nav_rows[-1]["date"],
        "observations": len(values),
        "total_return": round(total_return, 4),
        "annual_return": round(annual_return, 4),
        "annual_volatility": round(volatility, 4),
        "sharpe_ratio": round(sharpe, 3),
        "max_drawdown": round(max_drawdown, 4),
    }


def budget_health(month_row: dict, monthly_budget: float) -> dict:
    """预算健康度评分：预算控制 60% + 结余率 40%。"""
    if monthly_budget <= 0:
        raise ValueError("月预算必须大于 0")
    expense = month_row["expense"]
    savings_rate = month_row["savings_rate"]
    budget_score = (
        100.0
        if expense <= monthly_budget
        else max(0.0, 100.0 - (expense - monthly_budget) / monthly_budget * 100)
    )
    savings_score = min(100.0, max(0.0, savings_rate * 200))
    score = round(0.6 * budget_score + 0.4 * savings_score, 1)
    if score >= 80:
        label = "健康"
        advice = "保持当前支出结构与结余节奏。"
    elif score >= 60:
        label = "关注"
        advice = "压缩非必要支出，将结余率提升至 30% 以上。"
    else:
        label = "预警"
        advice = "支出超出预算或结余过低，需立即重排优先级。"
    return {
        "month": month_row["month"],
        "monthly_budget": monthly_budget,
        "budget_score": round(budget_score, 1),
        "savings_score": round(savings_score, 1),
        "score": score,
        "label": label,
        "advice": advice,
    }
