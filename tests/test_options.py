import unittest
from datetime import date
from decimal import Decimal

from flex_query import read_report
from money import Money
from options import OptionTrade, OptionTransaction
from report import Report


class OptionsTests(unittest.TestCase):
    def test_validator_buy_or_sell(self):
        with self.assertRaises(ValueError):
            OptionTransaction(
                "tradeId",
                date.fromisoformat("20220301"),
                "Buy 1 XXX 14APR23 35.0 P ",
                "NEITHER_BUY_NOR_SELL",
                Decimal(-1),
                Money(Decimal("-50"), "EUR"),
                Money(Decimal("-60"), "USD")
            )

    def test_short_expire(self):
        df = read_report("resources/options/short_expire.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._option_trades))
        self.assertEqual([
            OptionTrade(
                "O     220318P00065000",
                "O 18MAR22 65.0 P",
                date.fromisoformat("20220318"),
                [
                    OptionTransaction("3336143",
                                      date.fromisoformat("20220207"),
                                      "Sell -1 O 18MAR22 65.0 P ",
                                      "SELL",
                                      Decimal(-1),
                                      Money(Decimal("74.29"), "EUR"),
                                      Money(Decimal("85"), "USD"))
                ],
                True
            )
            ], result._option_trades)

    def test_long_expire(self):
        df = read_report("resources/options/long_expire.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._option_trades))
        self.assertEqual([
            OptionTrade(
                "PENN  220414P00035000",
                "PENN 14APR22 35.0 P",
                date.fromisoformat("20220414"),
                [
                    OptionTransaction("4296309",
                                      date.fromisoformat("20220301"),
                                      "Buy 1 PENN 14APR22 35.0 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-50.34232"), "EUR"),
                                      Money(Decimal("-56"), "USD"))
                ],
                True
            )
        ], result._option_trades)

    def test_short_close(self):
        df = read_report("resources/options/short_close.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._option_trades))
        self.assertEqual([
            OptionTrade(
                "BAC   220318P00044000",
                "BAC 18MAR22 44.0 P",
                date.fromisoformat("20220318"),
                [
                    OptionTransaction("3336300",
                                      date.fromisoformat("20220207"),
                                      "Sell -1 BAC 18MAR22 44.0 P ",
                                      "SELL",
                                      Decimal(-1),
                                      Money(Decimal("43.7"), "EUR"),
                                      Money(Decimal("50"), "USD")),
                    OptionTransaction("3471618",
                                      date.fromisoformat("20220307"),
                                      "Buy 1 BAC 18MAR22 44.0 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-522.37143"), "EUR"),
                                      Money(Decimal("-567"), "USD"))
                ],
                True
            )
            ], result._option_trades)

    def test_long_close(self):
        df = read_report("resources/options/long_close.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._option_trades))
        self.assertEqual([
            OptionTrade(
                "PENN  220414P00035000",
                "PENN 14APR22 35.0 P",
                date.fromisoformat("20220414"),
                [
                    OptionTransaction("4296309",
                                      date.fromisoformat("20220301"),
                                      "Buy 1 PENN 14APR22 35.0 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-50.34232"), "EUR"),
                                      Money(Decimal("-56"), "USD")),
                    OptionTransaction("6239672",
                                      date.fromisoformat("20220304"),
                                      "Sell -1 PENN 14APR22 35.0 P ",
                                      "SELL",
                                      Decimal(-1),
                                      Money(Decimal("72.27868"), "EUR"),
                                      Money(Decimal("79"), "USD"))
                ],
                True
            )
        ], result._option_trades)

    def test_short_two_closes(self):
        df = read_report("resources/options/short_two_closes.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._option_trades))
        self.assertEqual([
            OptionTrade(
                "FCX   221007P00036000",
                "FCX 07OCT22 36 P",
                date.fromisoformat("20221007"),
                [
                    OptionTransaction("3147997",
                                      date.fromisoformat("20220830"),
                                      "Sell -2 FCX 07OCT22 36 P ",
                                      "SELL",
                                      Decimal(-2),
                                      Money(Decimal("1304.041"), "EUR"),
                                      Money(Decimal("1306"), "USD")),
                    OptionTransaction("6050118",
                                      date.fromisoformat("20220928"),
                                      "Buy 1 FCX 07OCT22 36 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-864.734"), "EUR"),
                                      Money(Decimal("-842"), "USD")),
                    OptionTransaction("6050123",
                                      date.fromisoformat("20220928"),
                                      "Buy 1 FCX 07OCT22 36 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-864.734"), "EUR"),
                                      Money(Decimal("-842"), "USD"))
                ],
                True
            )
        ], result._option_trades)

    def test_short_two_closes_surplus_open(self):
        df = read_report("resources/options/short_two_closes_surplus_open.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(2, len(result._option_trades))
        self.assertEqual([
            OptionTrade(
                "FCX   221007P00036000",
                "FCX 07OCT22 36 P",
                date.fromisoformat("20221007"),
                [
                    OptionTransaction("3147997",
                                      date.fromisoformat("20220830"),
                                      "Sell -2 FCX 07OCT22 36 P ",
                                      "SELL",
                                      Decimal(-2),
                                      Money(Decimal("1304.041"), "EUR"),
                                      Money(Decimal("1306"), "USD")),
                    OptionTransaction("6050118",
                                      date.fromisoformat("20220928"),
                                      "Buy 1 FCX 07OCT22 36 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-864.734"), "EUR"),
                                      Money(Decimal("-842"), "USD")),
                    OptionTransaction("6050123",
                                      date.fromisoformat("20220928"),
                                      "Buy 1 FCX 07OCT22 36 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-864.734"), "EUR"),
                                      Money(Decimal("-842"), "USD"))
                ],
                True
            ),
            OptionTrade(
                "FCX   221007P00036000",
                "FCX 07OCT22 36 P",
                date.fromisoformat("20221007"),
                [
                    OptionTransaction("6050124",
                                      date.fromisoformat("20220928"),
                                      "Buy 1 FCX 07OCT22 36 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-864.734"), "EUR"),
                                      Money(Decimal("-842"), "USD"))
                ],
                True
            )
        ], result._option_trades)

    def test_long_closes_surplus_open(self):
        df = read_report("resources/options/long_close_surplus_open.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(2, len(result._option_trades))
        self.assertEqual([
            OptionTrade(
                "PENN  220414P00035000",
                "PENN 14APR22 35.0 P",
                date.fromisoformat("20220414"),
                [
                    OptionTransaction("4296309",
                                      date.fromisoformat("20220301"),
                                      "Buy 1 PENN 14APR22 35.0 P ",
                                      "BUY",
                                      Decimal(1),
                                      Money(Decimal("-50.34232"), "EUR"),
                                      Money(Decimal("-56"), "USD")),
                    OptionTransaction("6239672",
                                      date.fromisoformat("20220304"),
                                      "Sell -2 PENN 14APR22 35.0 P ",
                                      "SELL",
                                      Decimal(-1),
                                      Money(Decimal("72.278680"), "EUR"),
                                      Money(Decimal("79.0"), "USD"))
                ],
                True
            ),
            OptionTrade(
                "PENN  220414P00035000",
                "PENN 14APR22 35.0 P",
                date.fromisoformat("20220414"),
                [
                    OptionTransaction("6239672",
                                      date.fromisoformat("20220304"),
                                      "Sell -2 PENN 14APR22 35.0 P ",
                                      "SELL",
                                      Decimal(-1),
                                      Money(Decimal("72.278680"), "EUR"),
                                      Money(Decimal("79.0"), "USD"))
                ],
                True
            )
        ], result._option_trades)

    def test_profit_stillhalter_one_open(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR22 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertTrue(2022 in profit.keys())
        self.assertEqual(Money(Decimal(50), "EUR"), profit[2022].total)

    def test_profit_stillhalter_one_open_one_close_same_year(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR22 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Buy 1 XXX 14APR22 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertTrue(2022 in profit.keys())
        self.assertEqual(Money(Decimal("44.50"), "EUR"), profit[2022].total)

    def test_profit_stillhalter_one_open_one_close_different_year(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("50"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("-5.50"), "EUR"), profit[2023].total)

    def test_profit_stillhalter_one_open_one_close_different_year_before_cut_off(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({2022: date(2023, 5, 1)})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("44.50"), "EUR"), profit[2022].total)
        self.assertIsNone(profit[2023].total)

    def test_profit_stillhalter_one_open_one_close_different_year_after_cut_off(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({2022: date(2023, 2, 1)})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("50"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("-5.50"), "EUR"), profit[2023].total)

    def test_profit_stillhalter_two_open_close_different_years(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 2 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-2),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-2.75"), "EUR"),
                    Money(Decimal("-3"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("47.25"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("-5.50"), "EUR"), profit[2023].total)

    def test_profit_stillhalter_one_open_one_open_two_close(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("150"), "EUR"),
                    Money(Decimal("160"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 2 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(2),
                    Money(Decimal("-5.50"), "EUR"),
                    Money(Decimal("-6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("150"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("44.50"), "EUR"), profit[2023].total)

    def test_profit_stillhalter_one_open_one_open_two_close_with_cut_off(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("150"), "EUR"),
                    Money(Decimal("160"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230301"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("50"), "EUR"),
                    Money(Decimal("60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Buy 2 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(2),
                    Money(Decimal("-9"), "EUR"),
                    Money(Decimal("-10"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({2022: date(2023, 6, 1)})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("145.50"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("45.50"), "EUR"), profit[2023].total)

    def test_profit_termin_one_open(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR22 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertTrue(2022 in profit.keys())
        self.assertEqual(Money(Decimal(-50), "EUR"), profit[2022].total)

    def test_profit_termin_one_open_one_close_same_year(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR22 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Sell 1 XXX 14APR22 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertTrue(2022 in profit.keys())
        self.assertEqual(Money(Decimal("-44.50"), "EUR"), profit[2022].total)

    def test_profit_termin_one_open_one_close_different_year(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(-1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("-50"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("5.50"), "EUR"), profit[2023].total)

    def test_profit_termin_one_open_one_close_different_year_before_cut_off(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(-1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({2022: date(2023, 5, 1)})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("-50"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("5.50"), "EUR"), profit[2023].total)

    def test_profit_termin_one_open_one_close_different_year_after_cut_off(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({2022: date(2023, 2, 1)})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("-50"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("5.50"), "EUR"), profit[2023].total)

    def test_profit_termin_two_open_close_different_years(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 2 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(2),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("2.75"), "EUR"),
                    Money(Decimal("3"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 1 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-1),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("-47.25"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("5.50"), "EUR"), profit[2023].total)

    def test_profit_termin_one_open_one_open_two_close(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-150"), "EUR"),
                    Money(Decimal("-160"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 2 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-2),
                    Money(Decimal("5.50"), "EUR"),
                    Money(Decimal("6"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("-150"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("-44.50"), "EUR"), profit[2023].total)

    def test_profit_termin_one_open_one_open_two_close_with_cut_off(self):
        trade = OptionTrade(
            "XXX",
            "Description",
            date.fromisoformat("20220414"),
            [
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20220301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-150"), "EUR"),
                    Money(Decimal("-160"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230301"),
                    "Buy 1 XXX 14APR23 35.0 P ",
                    "BUY",
                    Decimal(1),
                    Money(Decimal("-50"), "EUR"),
                    Money(Decimal("-60"), "USD")
                ),
                OptionTransaction(
                    "tradeId",
                    date.fromisoformat("20230421"),
                    "Sell 2 XXX 14APR23 35.0 P ",
                    "SELL",
                    Decimal(-2),
                    Money(Decimal("9"), "EUR"),
                    Money(Decimal("10"), "USD")
                )
            ]
        )

        profit = trade.calculate_profit_per_year({2022: date(2023, 6, 1)})

        self.assertEqual([2022, 2023], list(profit.keys()))
        self.assertEqual(Money(Decimal("-150"), "EUR"), profit[2022].total)
        self.assertEqual(Money(Decimal("-41"), "EUR"), profit[2023].total)


if __name__ == '__main__':
    unittest.main()
