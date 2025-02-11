import unittest
from datetime import date
from decimal import Decimal

from money import Money
from stock import Stock
from testutils import read_report
from transaction import Transaction, BuySell, OpenCloseIndicator


class StockTests(unittest.TestCase):

    def test_buy_long_unclosed(self):
        result = read_report("resources/stock/buy_long_unclosed.csv")

        self.assertEqual(1, len(result._stocks))
        self.assertEqual([
            Stock(
                "GAB PRK",
                "STK",
                [
                    Transaction("1101770",
                                date.fromisoformat("20220223"),
                                "Buy 200 GABELLI EQUITY TRUST INC ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(200),
                                Money(Decimal("-4424.5191"), "EUR"),
                                Money(Decimal("-5002"), "USD"),
                                Decimal("0.88455")),
                    Transaction("3629427",
                                date.fromisoformat("20220808"),
                                "Buy 100 GABELLI EQUITY TRUST INC ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(100),
                                Money(Decimal("-2408.99216"), "EUR"),
                                Money(Decimal("-2456"), "USD"),
                                Decimal("0.98086")),
                    Transaction("0850409",
                                date.fromisoformat("20221122"),
                                "Buy 100 GABELLI EQUITY TRUST INC ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(100),
                                Money(Decimal("-2185.6786"), "EUR"),
                                Money(Decimal("-2252"), "USD"),
                                Decimal("0.97055"))
                ],
                False
            )
        ], result._stocks)

    def test_assign_long_unclosed(self):
        result = read_report("resources/stock/assign_long_unclosed.csv")

        self.assertEqual(1, len(result._stocks))
        self.assertEqual([
            Stock(
                "HON",
                "STK",
                [
                    Transaction("3328647",
                                date.fromisoformat("20220617"),
                                "Buy 100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(100),
                                Money(Decimal("-17626.8"), "EUR"),
                                Money(Decimal("-18500"), "USD"),
                                Decimal("0.9528"))
                ],
                False
            )
        ], result._stocks)

    def test_assign_long_close(self):
        result = read_report("resources/stock/assign_long_close.csv")

        self.assertEqual(1, len(result._stocks))
        self.assertEqual([
            Stock(
                "HON",
                "STK",
                [
                    Transaction("3328647",
                                date.fromisoformat("20220617"),
                                "Buy 100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(100),
                                Money(Decimal("-17626.8"), "EUR"),
                                Money(Decimal("-18500"), "USD"),
                                Decimal("0.9528")),
                    Transaction("3118332",
                                date.fromisoformat("20220805"),
                                "Sell -100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                BuySell.SELL,
                                OpenCloseIndicator.CLOSE,
                                Decimal(-100),
                                Money(Decimal("17900.272322904"), "EUR"),
                                Money(Decimal("18249.569075"), "USD"),
                                Decimal("0.98086"))
                ],
                True
            )
        ], result._stocks)

    def test_assign_long_close_next_year(self):
        result = read_report("resources/stock/assign_long_close_next_year.csv")

        self.assertEqual(1, len(result._stocks))
        self.assertEqual([
            Stock(
                "BAC",
                "STK",
                [
                    Transaction("1338170",
                                date.fromisoformat("20220614"),
                                "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(100),
                                Money(Decimal("-3733.587"), "EUR"),
                                Money(Decimal("-3900"), "USD"),
                                Decimal("0.95733")),
                    Transaction("3333809",
                                date.fromisoformat("20220617"),
                                "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(100),
                                Money(Decimal("-3715.92"), "EUR"),
                                Money(Decimal("-3900"), "USD"),
                                Decimal("0.9528")),
                    Transaction("8488811",
                                date.fromisoformat("20240531"),
                                "Sell -200 BANK OF AMERICA CORP (Assignment)",
                                BuySell.SELL,
                                OpenCloseIndicator.CLOSE,
                                Decimal(-200),
                                Money(Decimal("7153.146"), "EUR"),
                                Money(Decimal("7800"), "USD"),
                                Decimal("0.91707"))
                ],
                True
            )
        ], result._stocks)

    def test_assign_long_close_in_steps(self):
        result = read_report("resources/stock/assign_long_close_in_steps.csv")

        self.assertEqual(1, len(result._stocks))
        self.assertEqual([
            Stock(
                "MO",
                "STK",
                [
                    Transaction("0074324",
                                date.fromisoformat("20231101"),
                                "Buy 200 ALTRIA GROUP INC (Assignment)",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(200),
                                Money(Decimal("-7908.18"), "EUR"),
                                Money(Decimal("-8400"), "USD"),
                                Decimal("0.94145")),
                    Transaction("5593418",
                                date.fromisoformat("20231201"),
                                "Sell -100 ALTRIA GROUP INC (Assignment)",
                                BuySell.SELL,
                                OpenCloseIndicator.CLOSE,
                                Decimal(-100),
                                Money(Decimal("3875.841611877"), "EUR"),
                                Money(Decimal("4199.9519"), "USD"),
                                Decimal("0.92283")),
                    Transaction("7583880",
                                date.fromisoformat("20240321"),
                                "Sell -100 ALTRIA GROUP INC (Assignment)",
                                BuySell.SELL,
                                OpenCloseIndicator.CLOSE,
                                Decimal(-100),
                                Money(Decimal("3932.525"), "EUR"),
                                Money(Decimal("4250"), "USD"),
                                Decimal("0.9253"))
                ],
                True
            )
        ], result._stocks)

    def test_profit_buy_long_unclosed(self):
        trade = Stock("GAB PRK", "STK")
        trade.add_transaction(Transaction("1101770",
                                          date.fromisoformat("20220223"),
                                          "Buy 200 GABELLI EQUITY TRUST INC ",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(200),
                                          Money(Decimal("-4424.5191"), "EUR"),
                                          Money(Decimal("-5002"), "USD"),
                                          Decimal("0.88455")))
        trade.add_transaction(Transaction("3629427",
                                          date.fromisoformat("20220808"),
                                          "Buy 100 GABELLI EQUITY TRUST INC ",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(100),
                                          Money(Decimal("-2408.99216"), "EUR"),
                                          Money(Decimal("-2456"), "USD"),
                                          Decimal("0.98086")))
        trade.add_transaction(Transaction("0850409",
                                          date.fromisoformat("20221122"),
                                          "Buy 100 GABELLI EQUITY TRUST INC ",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(100),
                                          Money(Decimal("-2185.6786"), "EUR"),
                                          Money(Decimal("-2252"), "USD"),
                                          Decimal("0.97055")))

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(0, len(transaction_collections))

    def test_profit_assign_long_close(self):
        trade = Stock("HON", "STK")
        trade.add_transaction(Transaction("3328647",
                                          date.fromisoformat("20220617"),
                                          "Buy 100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(100),
                                          Money(Decimal("-17626.8"), "EUR"),
                                          Money(Decimal("-18500"), "USD"),
                                          Decimal("0.9528")))
        trade.add_transaction(Transaction("3118332",
                                          date.fromisoformat("20220805"),
                                          "Sell -100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                          BuySell.SELL,
                                          OpenCloseIndicator.CLOSE,
                                          Decimal(-100),
                                          Money(Decimal("17900.272322904"), "EUR"),
                                          Money(Decimal("18249.569075"), "USD"),
                                          Decimal("0.98086")))

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(1, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("273.472322904"), "EUR"), profit)

    def test_profit_assign_long_close_next_year(self):
        trade = Stock("BAC", "STK")
        trade.add_transaction(Transaction("1338170",
                                          date.fromisoformat("20220614"),
                                          "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(100),
                                          Money(Decimal("-3733.587"), "EUR"),
                                          Money(Decimal("-3900"), "USD"),
                                          Decimal("0.95733")))
        trade.add_transaction(Transaction("3333809",
                                          date.fromisoformat("20220617"),
                                          "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(100),
                                          Money(Decimal("-3715.92"), "EUR"),
                                          Money(Decimal("-3900"), "USD"),
                                          Decimal("0.9528")))
        trade.add_transaction(Transaction("8488811",
                                          date.fromisoformat("20240531"),
                                          "Sell -200 BANK OF AMERICA CORP (Assignment)",
                                          BuySell.SELL,
                                          OpenCloseIndicator.CLOSE,
                                          Decimal(-200),
                                          Money(Decimal("7153.146"), "EUR"),
                                          Money(Decimal("7800"), "USD"),
                                          Decimal("0.91707")))

        transaction_collections = trade.transaction_collections(2024)
        self.assertEqual(1, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-296.361"), "EUR"), profit)

    def test_profit_assign_long_close_in_steps(self):
        trade = Stock("MO", "STK")
        trade.add_transaction(Transaction("0074324",
                                          date.fromisoformat("20231101"),
                                          "Buy 200 ALTRIA GROUP INC (Assignment)",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(200),
                                          Money(Decimal("-7908.18"), "EUR"),
                                          Money(Decimal("-8400"), "USD"),
                                          Decimal("0.94145")))
        trade.add_transaction(Transaction("5593418",
                                          date.fromisoformat("20231201"),
                                          "Sell -100 ALTRIA GROUP INC (Assignment)",
                                          BuySell.SELL,
                                          OpenCloseIndicator.CLOSE,
                                          Decimal(-100),
                                          Money(Decimal("3875.841611877"), "EUR"),
                                          Money(Decimal("4199.9519"), "USD"),
                                          Decimal("0.92283")))
        trade.add_transaction(Transaction("7583880",
                                          date.fromisoformat("20240321"),
                                          "Sell -100 ALTRIA GROUP INC (Assignment)",
                                          BuySell.SELL,
                                          OpenCloseIndicator.CLOSE,
                                          Decimal(-100),
                                          Money(Decimal("3932.525"), "EUR"),
                                          Money(Decimal("4250"), "USD"),
                                          Decimal("0.9253")))

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-78.248388123"), "EUR"), profit)

        transaction_collections = trade.transaction_collections(2024)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-21.565"), "EUR"), profit)

    def test_profit_multiple_transactions(self):
        trade = Stock("XXX", "STK")
        trade.add_transaction(Transaction("001",
                                          date.fromisoformat("20231101"),
                                          "Buy 200 X Company",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(200),
                                          Money(Decimal("-200"), "EUR"),
                                          Money(Decimal("-200"), "USD"),
                                          Decimal(1)))
        trade.add_transaction(Transaction("002",
                                          date.fromisoformat("20231102"),
                                          "Sell 100 X Company",
                                          BuySell.SELL,
                                          OpenCloseIndicator.CLOSE,
                                          Decimal(-100),
                                          Money(Decimal("110"), "EUR"),
                                          Money(Decimal("110"), "USD"),
                                          Decimal(1)))
        trade.add_transaction(Transaction("003",
                                          date.fromisoformat("20231103"),
                                          "Buy 200 X Company",
                                          BuySell.BUY,
                                          OpenCloseIndicator.OPEN,
                                          Decimal(200),
                                          Money(Decimal("-180"), "EUR"),
                                          Money(Decimal("-180"), "USD"),
                                          Decimal(1)))
        trade.add_transaction(Transaction("004",
                                          date.fromisoformat("20231104"),
                                          "Sell 300 X Company",
                                          BuySell.SELL,
                                          OpenCloseIndicator.CLOSE,
                                          Decimal(-300),
                                          Money(Decimal("360"), "EUR"),
                                          Money(Decimal("360"), "USD"),
                                          Decimal(1)))

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(2, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("10"), "EUR"), profit)

        profit = transaction_collections[1].profit()
        self.assertEqual(Money(Decimal("80"), "EUR"), profit)


if __name__ == '__main__':
    unittest.main()
