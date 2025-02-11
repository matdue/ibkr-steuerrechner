import unittest
from datetime import date
from decimal import Decimal

from money import Money
from testutils import read_report
from transaction import Transaction, BuySell, OpenCloseIndicator
from treasury_bill import TreasuryBill


class TreasuryBillTests(unittest.TestCase):
    def test_buy_long_unclosed(self):
        result = read_report("resources/treasury_bill/buy_long_unclosed.csv")

        self.assertEqual(1, len(result._treasury_bills))
        self.assertEqual([
            TreasuryBill(
                "912797HR1",
                "BILL",
                [
                    Transaction("0959089",
                                date.fromisoformat("20231122"),
                                "Buy 5,000 B 05/23/24 ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(5000),
                                Money(Decimal("-4478.261841"), "EUR"),
                                Money(Decimal("-4876.05"), "USD"),
                                Decimal("0.91842"))
                ],
                False
            )
        ], result._treasury_bills)

    def test_buy_long_close(self):
        result = read_report("resources/treasury_bill/buy_long_close.csv")

        self.assertEqual(1, len(result._treasury_bills))
        self.assertEqual([
            TreasuryBill(
                "912797HR1",
                "BILL",
                [
                    Transaction("0959089",
                                date.fromisoformat("20231122"),
                                "Buy 5,000 B 05/23/24 ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(5000),
                                Money(Decimal("-4478.261841"), "EUR"),
                                Money(Decimal("-4876.05"), "USD"),
                                Decimal("0.91842")),
                    Transaction(None,
                                date.fromisoformat("20240522"),
                                "(US912797HR13) TBILL MATURITY (912797HR1, B 05/23/24, US912797HR13)",
                                None,
                                OpenCloseIndicator.CLOSE,
                                Decimal(-5000),
                                Money(Decimal("4623"), "EUR"),
                                Money(Decimal("5000"), "USD"),
                                Decimal("0.9246"))
                ],
                True
            )
        ], result._treasury_bills)

    def test_profit_buy_long_unclosed(self):
        t_bill = TreasuryBill("912797HR1", "BILL")
        t_bill.add_transaction(Transaction("0959089",
                                           date.fromisoformat("20231122"),
                                           "Buy 5,000 B 05/23/24 ",
                                           BuySell.BUY,
                                           OpenCloseIndicator.OPEN,
                                           Decimal(5000),
                                           Money(Decimal("-4478.261841"), "EUR"),
                                           Money(Decimal("-4876.05"), "USD"),
                                           Decimal("0.91842")))

        transaction_collections = t_bill.transaction_collections(2023)
        self.assertEqual(0, len(transaction_collections))

    def test_profit_buy_long_close(self):
        t_bill = TreasuryBill("912797HR1", "BILL")
        t_bill.add_transaction(Transaction("0959089",
                                           date.fromisoformat("20231122"),
                                           "Buy 5,000 B 05/23/24 ",
                                           BuySell.BUY,
                                           OpenCloseIndicator.OPEN,
                                           Decimal(5000),
                                           Money(Decimal("-4478.261841"), "EUR"),
                                           Money(Decimal("-4876.05"), "USD"),
                                           Decimal("0.91842")))
        t_bill.add_transaction(Transaction(None,
                                           date.fromisoformat("20240522"),
                                           "(US912797HR13) TBILL MATURITY (912797HR1, B 05/23/24, US912797HR13)",
                                           None,
                                           OpenCloseIndicator.CLOSE,
                                           Decimal(-5000),
                                           Money(Decimal("4623"), "EUR"),
                                           Money(Decimal("5000"), "USD"),
                                           Decimal("0.9246")))

        transaction_collections = t_bill.transaction_collections(2023)
        self.assertEqual(0, len(transaction_collections))
        transaction_collections = t_bill.transaction_collections(2024)
        self.assertEqual(1, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("144.738159"), "EUR"), profit)


if __name__ == '__main__':
    unittest.main()
