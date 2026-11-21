"""finance_metrics 单元测试：由 CS 搭档 lsa 编写，金融搭档 lsa 核对口径。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import finance_metrics as fm

BASE = Path(__file__).resolve().parents[1] / "data"


class TestFinanceMetrics(unittest.TestCase):
    def setUp(self):
        self.txs = fm.load_transactions(BASE / "transactions.csv")
        self.nav = fm.load_nav(BASE / "nav.csv")

    def test_load_transactions(self):
        self.assertEqual(len(self.txs), 21)
        self.assertEqual(self.txs[0]["month"], "2026-09")

    def test_monthly_summary(self):
        rows = fm.monthly_summary(self.txs)
        self.assertEqual([r["month"] for r in rows], ["2026-09", "2026-10", "2026-11"])
        self.assertEqual(rows[0]["income"], 18000.0)
        self.assertEqual(rows[0]["expense"], 6300.0)
        self.assertEqual(rows[0]["net"], 11700.0)
        self.assertEqual(rows[2]["expense"], 11000.0)

    def test_category_share(self):
        rows = fm.category_share(self.txs, "2026-11")
        self.assertEqual(rows[0]["category"], "房租")
        self.assertAlmostEqual(sum(r["share"] for r in rows), 1.0, places=3)

    def test_portfolio_metrics(self):
        perf = fm.portfolio_metrics(self.nav)
        self.assertEqual(perf["observations"], 15)
        self.assertAlmostEqual(perf["total_return"], 0.092, places=3)
        self.assertGreater(perf["annual_return"], 0)
        self.assertGreater(perf["annual_volatility"], 0)
        self.assertAlmostEqual(perf["max_drawdown"], 0.0409, places=3)

    def test_budget_health(self):
        latest = fm.monthly_summary(self.txs)[-1]
        result = fm.budget_health(latest, 8000)
        self.assertEqual(result["label"], "关注")
        self.assertGreater(result["score"], 60)
        self.assertLess(result["score"], 80)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            fm.portfolio_metrics([{"date": "2026-01-01", "nav": 1.0}])
        with self.assertRaises(ValueError):
            fm.budget_health({"month": "2026-01", "expense": 1, "savings_rate": 0}, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
