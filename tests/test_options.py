import unittest
from datetime import date
from decimal import Decimal

from money import Money
from option import Option
from testutils import read_report
from transaction import Transaction, OpenCloseIndicator, BuySell


class OptionsTests(unittest.TestCase):
    def test_short_expire(self):
        result = read_report("resources/options/short_expire.csv")

        self.assertEqual(1, len(result._options))
        self.assertEqual([
            Option(
                "O     220318P00065000",
                "OPT",
                [
                    Transaction("3336143",
                                date.fromisoformat("20220207"),
                                "Sell -1 O 18MAR22 65.0 P ",
                                BuySell.SELL,
                                OpenCloseIndicator.OPEN,
                                Decimal(-1),
                                Money(Decimal("74.29"), "EUR"),
                                Money(Decimal("85"), "USD"),
                                Decimal("0.874"))
                ]
            )
        ], result._options)

    def test_long_expire(self):
        result = read_report("resources/options/long_expire.csv")

        self.assertEqual(1, len(result._options))
        self.assertEqual([
            Option(
                "PENN  220414P00035000",
                "OPT",
                [
                    Transaction("4296309",
                                date.fromisoformat("20220301"),
                                "Buy 1 PENN 14APR22 35.0 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(1),
                                Money(Decimal("-50.34232"), "EUR"),
                                Money(Decimal("-56"), "USD"),
                                Decimal("0.89897"))
                ]
            )
        ], result._options)

    def test_short_close(self):
        result = read_report("resources/options/short_close.csv")

        self.assertEqual(1, len(result._options))
        self.assertEqual([
            Option(
                "BAC   220318P00044000",
                "OPT",
                [
                    Transaction("3336300",
                                date.fromisoformat("20220207"),
                                "Sell -1 BAC 18MAR22 44.0 P ",
                                BuySell.SELL,
                                OpenCloseIndicator.OPEN,
                                Decimal(-1),
                                Money(Decimal("43.7"), "EUR"),
                                Money(Decimal("50"), "USD"),
                                Decimal("0.874")),
                    Transaction("3471618",
                                date.fromisoformat("20220307"),
                                "Buy 1 BAC 18MAR22 44.0 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.CLOSE,
                                Decimal(1),
                                Money(Decimal("-522.37143"), "EUR"),
                                Money(Decimal("-567"), "USD"),
                                Decimal("0.92129"))
                ],
                True
            )
        ], result._options)

    def test_long_close(self):
        result = read_report("resources/options/long_close.csv")

        self.assertEqual(1, len(result._options))
        self.assertEqual([
            Option(
                "PENN  220414P00035000",
                "OPT",
                [
                    Transaction("4296309",
                                date.fromisoformat("20220301"),
                                "Buy 1 PENN 14APR22 35.0 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(1),
                                Money(Decimal("-50.34232"), "EUR"),
                                Money(Decimal("-56"), "USD"),
                                Decimal("0.89897")),
                    Transaction("6239672",
                                date.fromisoformat("20220304"),
                                "Sell -1 PENN 14APR22 35.0 P ",
                                BuySell.SELL,
                                OpenCloseIndicator.CLOSE,
                                Decimal(-1),
                                Money(Decimal("72.27868"), "EUR"),
                                Money(Decimal("79"), "USD"),
                                Decimal("0.91492"))
                ],
                True
            )
        ], result._options)

    def test_short_two_closes(self):
        result = read_report("resources/options/short_two_closes.csv")

        self.assertEqual(1, len(result._options))
        self.assertEqual([
            Option(
                "FCX   221007P00036000",
                "OPT",
                [
                    Transaction("3147997",
                                date.fromisoformat("20220830"),
                                "Sell -2 FCX 07OCT22 36 P ",
                                BuySell.SELL,
                                OpenCloseIndicator.OPEN,
                                Decimal(-2),
                                Money(Decimal("1304.041"), "EUR"),
                                Money(Decimal("1306"), "USD"),
                                Decimal("0.9985")),
                    Transaction("6050118",
                                date.fromisoformat("20220928"),
                                "Buy 1 FCX 07OCT22 36 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.CLOSE,
                                Decimal(1),
                                Money(Decimal("-864.734"), "EUR"),
                                Money(Decimal("-842"), "USD"),
                                Decimal("1.027")),
                    Transaction("6050123",
                                date.fromisoformat("20220928"),
                                "Buy 1 FCX 07OCT22 36 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.CLOSE,
                                Decimal(1),
                                Money(Decimal("-864.734"), "EUR"),
                                Money(Decimal("-842"), "USD"),
                                Decimal("1.027"))
                ],
                True
            )
        ], result._options)

    def test_short_two_closes_surplus_open(self):
        result = read_report("resources/options/short_two_closes_surplus_open.csv")

        self.assertEqual(2, len(result._options))
        self.assertEqual([
            Option(
                "FCX   221007P00036000",
                "OPT",
                [
                    Transaction("3147997",
                                date.fromisoformat("20220830"),
                                "Sell -2 FCX 07OCT22 36 P ",
                                BuySell.SELL,
                                OpenCloseIndicator.OPEN,
                                Decimal(-2),
                                Money(Decimal("1304.041"), "EUR"),
                                Money(Decimal("1306"), "USD"),
                                Decimal("0.9985")),
                    Transaction("6050118",
                                date.fromisoformat("20220928"),
                                "Buy 1 FCX 07OCT22 36 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.CLOSE,
                                Decimal(1),
                                Money(Decimal("-864.734"), "EUR"),
                                Money(Decimal("-842"), "USD"),
                                Decimal("1.027")),
                    Transaction("6050123",
                                date.fromisoformat("20220928"),
                                "Buy 1 FCX 07OCT22 36 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.CLOSE,
                                Decimal(1),
                                Money(Decimal("-864.734"), "EUR"),
                                Money(Decimal("-842"), "USD"),
                                Decimal("1.027"))
                ],
                True
            ),
            Option(
                "FCX   221007P00036000",
                "OPT",
                [
                    Transaction("6050124",
                                date.fromisoformat("20220928"),
                                "Buy 1 FCX 07OCT22 36 P ",
                                BuySell.BUY,
                                OpenCloseIndicator.OPEN,
                                Decimal(1),
                                Money(Decimal("-864.734"), "EUR"),
                                Money(Decimal("-842"), "USD"),
                                Decimal("1.027"))
                ],
                False
            )
        ], result._options)

    def test_profit_short_one_open(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR22 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.OPEN,
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD"),
                    Decimal("0.83333")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(1, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("50"), "EUR"), profit)

    def test_profit_short_one_open_one_close_same_year(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR22 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.OPEN,
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Buy 1 XXX 14APR22 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.CLOSE,
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(2, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("50"), "EUR"), profit)

        profit = transaction_collections[1].profit()
        self.assertEqual(Money(Decimal("-5.50"), "EUR"), profit)

    def test_profit_short_one_open_one_close_different_year(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.OPEN,
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.CLOSE,
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("50"), "EUR"), profit)

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-5.50"), "EUR"), profit)

    def test_profit_short_two_open_close_different_years(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 2 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.OPEN,
                    Decimal(-2),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.CLOSE,
                    Decimal(1),
                    Money(Decimal("-2.75"), "EUR"),
                    Money(Decimal("-3"), "USD"),
                    Decimal("0.91667")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.CLOSE,
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(2, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("50"), "EUR"), profit)
        profit = transaction_collections[1].profit()
        self.assertEqual(Money(Decimal("-2.75"), "EUR"), profit)

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-5.50"), "EUR"), profit)

    def test_profit_short_one_open_one_open_two_close(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.OPEN,
                    Decimal(-1),
                    Money(Decimal("150"), "EUR"),
                    Money(Decimal("160"), "USD"),
                    Decimal("0.9375")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.OPEN,
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 2 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.CLOSE,
                    Decimal(2),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("150"), "EUR"), profit)

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(2, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("50"), "EUR"), profit)
        profit = transaction_collections[1].profit()
        self.assertEqual(Money(Decimal("-5.50"), "EUR"), profit)

    def test_profit_long_one_open(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR22 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.OPEN,
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD"),
                    Decimal("0.83333")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(0, len(transaction_collections))

    def test_profit_long_one_open_one_close_same_year(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR22 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.OPEN,
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Sell 1 XXX 14APR22 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.CLOSE,
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(1, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-44.50"), "EUR"), profit)

    def test_profit_long_one_open_one_close_different_year(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.OPEN,
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.CLOSE,
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(1, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-44.50"), "EUR"), profit)

    def test_profit_long_two_open_close_different_years(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 2 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.OPEN,
                    Decimal(2),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.CLOSE,
                    Decimal(-1),
                    Money(Decimal("2.75"), "EUR"),
                    Money(Decimal("3"), "USD"),
                    Decimal("0.91667")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.CLOSE,
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2022)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-22.25"), "EUR"), profit)

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(1, len(transaction_collections))
        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-19.50"), "EUR"), profit)

    def test_profit_long_one_open_one_open_two_close(self):
        trade = Option(
            "XXX",
            "OPT",
            [
                Transaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.OPEN,
                    Decimal(1),
                    Money(Decimal("-150"), "EUR"),
                    Money(Decimal("-160"), "USD"),
                    Decimal("0.9375")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    BuySell.BUY,
                    OpenCloseIndicator.OPEN,
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD"),
                    Decimal("0.83333")
                ),
                Transaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 2 XXX 14APR23 35.0 P ",
                    BuySell.SELL,
                    OpenCloseIndicator.CLOSE,
                    Decimal(-2),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD"),
                    Decimal("0.91667")
                )
            ]
        )

        transaction_collections = trade.transaction_collections(2023)
        self.assertEqual(1, len(transaction_collections))

        profit = transaction_collections[0].profit()
        self.assertEqual(Money(Decimal("-194.50"), "EUR"), profit)


if __name__ == '__main__':
    unittest.main()
