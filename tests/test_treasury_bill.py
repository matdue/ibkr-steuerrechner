import unittest
from datetime import date
from decimal import Decimal

from ibkr_steuerrechner.flex_query import read_report
from ibkr_steuerrechner.money import Money
from ibkr_steuerrechner.report import Report
from ibkr_steuerrechner.treasury_bill import TreasuryBillTrade, TreasuryBillTransaction


class TreasuryBillTests(unittest.TestCase):
    def test_buy_long_unclosed(self):
        df = read_report("resources/treasury_bill/buy_long_unclosed.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._treasury_bill_trades))
        self.assertEqual([
            TreasuryBillTrade(
                "912797HR1",
                "B 05/23/24",
                [
                    TreasuryBillTransaction("0959089",
                                            date.fromisoformat("20231122"),
                                            "Buy 5,000 B 05/23/24 ",
                                            "BUY",
                                            Decimal(5000),
                                            Money(Decimal("-4478.261841"), "EUR"),
                                            Money(Decimal("-4876.05"), "USD"))
                ],
                False
            )
        ], result._treasury_bill_trades)

    def test_buy_long_close(self):
        df = read_report("resources/treasury_bill/buy_long_close.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._treasury_bill_trades))
        self.assertEqual([
            TreasuryBillTrade(
                "912797HR1",
                "B 05/23/24",
                [
                    TreasuryBillTransaction("0959089",
                                            date.fromisoformat("20231122"),
                                            "Buy 5,000 B 05/23/24 ",
                                            "BUY",
                                            Decimal(5000),
                                            Money(Decimal("-4478.261841"), "EUR"),
                                            Money(Decimal("-4876.05"), "USD")),
                    TreasuryBillTransaction(None,
                                            date.fromisoformat("20240522"),
                                            "(US912797HR13) TBILL MATURITY (912797HR1, B 05/23/24, US912797HR13)",
                                            None,
                                            Decimal(-5000),
                                            Money(Decimal("4623"), "EUR"),
                                            Money(Decimal("5000"), "USD"))
                ],
                True
            )
        ], result._treasury_bill_trades)

    def test_profit_buy_long_unclosed(self):
        trade = TreasuryBillTrade("912797HR1", "B 05/23/24")
        trade.add_transaction(TreasuryBillTransaction("0959089",
                                                      date.fromisoformat("20231122"),
                                                      "Buy 5,000 B 05/23/24 ",
                                                      "BUY",
                                                      Decimal(5000),
                                                      Money(Decimal("-4478.261841"), "EUR"),
                                                      Money(Decimal("-4876.05"), "USD")))

        returns, unconsumed_returns, unconsumed_accruals = trade.calculate_returns()

        self.assertEqual(0, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(1, len(unconsumed_accruals))

    def test_profit_buy_long_close(self):
        trade = TreasuryBillTrade("912797HR1", "B 05/23/24")
        trade.add_transaction(TreasuryBillTransaction("0959089",
                                                      date.fromisoformat("20231122"),
                                                      "Buy 5,000 B 05/23/24 ",
                                                      "BUY",
                                                      Decimal(5000),
                                                      Money(Decimal("-4478.261841"), "EUR"),
                                                      Money(Decimal("-4876.05"), "USD")))
        trade.add_transaction(TreasuryBillTransaction(None,
                                                      date.fromisoformat("20240522"),
                                                      "(US912797HR13) TBILL MATURITY (912797HR1, B 05/23/24, US912797HR13)",
                                                      None,
                                                      Decimal(-5000),
                                                      Money(Decimal("4623"), "EUR"),
                                                      Money(Decimal("5000"), "USD")))

        returns, unconsumed_returns, unconsumed_accruals = trade.calculate_returns()

        self.assertEqual(1, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))

        profit = returns[0].calculate_profit()
        self.assertEqual(Money(Decimal("144.738159"), "EUR"), profit.profit_base)
        self.assertEqual(1, len(profit.accruals))


if __name__ == '__main__':
    unittest.main()
