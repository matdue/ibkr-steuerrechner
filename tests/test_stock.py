import unittest
from datetime import date
from decimal import Decimal

from ibkr_steuerrechner.flex_query import read_report
from ibkr_steuerrechner.money import Money
from ibkr_steuerrechner.report import Report
from ibkr_steuerrechner.stock import StockTrade, StockTransaction


class StockTests(unittest.TestCase):
    def test_buy_long_unclosed(self):
        df = read_report("resources/stock/buy_long_unclosed.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._stock_trades))
        self.assertEqual([
            StockTrade(
                "GAB PRK",
                "GABELLI EQUITY TRUST INC",
                [
                    StockTransaction("1101770",
                                      date.fromisoformat("20220223"),
                                      "Buy 200 GABELLI EQUITY TRUST INC ",
                                      "BUY",
                                      Decimal(200),
                                      Money(Decimal("-4424.5191"), "EUR"),
                                      Money(Decimal("-5002"), "USD")),
                    StockTransaction("3629427",
                                     date.fromisoformat("20220808"),
                                     "Buy 100 GABELLI EQUITY TRUST INC ",
                                     "BUY",
                                     Decimal(100),
                                     Money(Decimal("-2408.99216"), "EUR"),
                                     Money(Decimal("-2456"), "USD")),
                    StockTransaction("0850409",
                                     date.fromisoformat("20221122"),
                                     "Buy 100 GABELLI EQUITY TRUST INC ",
                                     "BUY",
                                     Decimal(100),
                                     Money(Decimal("-2185.6786"), "EUR"),
                                     Money(Decimal("-2252"), "USD"))
                ],
                False
            )
        ], result._stock_trades)

    def test_assign_long_unclosed(self):
        df = read_report("resources/stock/assign_long_unclosed.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._stock_trades))
        self.assertEqual([
            StockTrade(
                "HON",
                "HONEYWELL INTERNATIONAL INC",
                [
                    StockTransaction("3328647",
                                     date.fromisoformat("20220617"),
                                     "Buy 100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                     "BUY",
                                     Decimal(100),
                                     Money(Decimal("-17626.8"), "EUR"),
                                     Money(Decimal("-18500"), "USD"))
                ],
                False
            )
        ], result._stock_trades)

    def test_assign_long_close(self):
        df = read_report("resources/stock/assign_long_close.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._stock_trades))
        self.assertEqual([
            StockTrade(
                "HON",
                "HONEYWELL INTERNATIONAL INC",
                [
                    StockTransaction("3328647",
                                     date.fromisoformat("20220617"),
                                     "Buy 100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                     "BUY",
                                     Decimal(100),
                                     Money(Decimal("-17626.8"), "EUR"),
                                     Money(Decimal("-18500"), "USD")),
                    StockTransaction("3118332",
                                     date.fromisoformat("20220805"),
                                     "Sell -100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                     "SELL",
                                     Decimal(-100),
                                     Money(Decimal("17900.272322904"), "EUR"),
                                     Money(Decimal("18249.569075"), "USD"))
                ],
                True
            )
        ], result._stock_trades)

    def test_assign_long_close_next_year(self):
        df = read_report("resources/stock/assign_long_close_next_year.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._stock_trades))
        self.assertEqual([
            StockTrade(
                "BAC",
                "BANK OF AMERICA CORP",
                [
                    StockTransaction("1338170",
                                     date.fromisoformat("20220614"),
                                     "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                     "BUY",
                                     Decimal(100),
                                     Money(Decimal("-3733.587"), "EUR"),
                                     Money(Decimal("-3900"), "USD")),
                    StockTransaction("3333809",
                                     date.fromisoformat("20220617"),
                                     "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                     "BUY",
                                     Decimal(100),
                                     Money(Decimal("-3715.92"), "EUR"),
                                     Money(Decimal("-3900"), "USD")),
                    StockTransaction("8488811",
                                     date.fromisoformat("20240531"),
                                     "Sell -200 BANK OF AMERICA CORP (Assignment)",
                                     "SELL",
                                     Decimal(-200),
                                     Money(Decimal("7153.146"), "EUR"),
                                     Money(Decimal("7800"), "USD"))
                ],
                True
            )
        ], result._stock_trades)

    def test_assign_long_close_in_steps(self):
        df = read_report("resources/stock/assign_long_close_in_steps.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._stock_trades))
        self.assertEqual([
            StockTrade(
                "MO",
                "ALTRIA GROUP INC",
                [
                    StockTransaction("0074324",
                                     date.fromisoformat("20231101"),
                                     "Buy 200 ALTRIA GROUP INC (Assignment)",
                                     "BUY",
                                     Decimal(200),
                                     Money(Decimal("-7908.18"), "EUR"),
                                     Money(Decimal("-8400"), "USD")),
                    StockTransaction("5593418",
                                     date.fromisoformat("20231201"),
                                     "Sell -100 ALTRIA GROUP INC (Assignment)",
                                     "SELL",
                                     Decimal(-100),
                                     Money(Decimal("3875.841611877"), "EUR"),
                                     Money(Decimal("4199.9519"), "USD")),
                    StockTransaction("7583880",
                                     date.fromisoformat("20240321"),
                                     "Sell -100 ALTRIA GROUP INC (Assignment)",
                                     "SELL",
                                     Decimal(-100),
                                     Money(Decimal("3932.525"), "EUR"),
                                     Money(Decimal("4250"), "USD"))
                ],
                True
            )
        ], result._stock_trades)

    def test_profit_buy_long_unclosed(self):
        trade = StockTrade("GAB PRK", "GABELLI EQUITY TRUST INC")
        trade.add_transaction(StockTransaction("1101770",
                                               date.fromisoformat("20220223"),
                                               "Buy 200 GABELLI EQUITY TRUST INC ",
                                               "BUY",
                                               Decimal(200),
                                               Money(Decimal("-4424.5191"), "EUR"),
                                               Money(Decimal("-5002"), "USD")))
        trade.add_transaction(StockTransaction("3629427",
                                               date.fromisoformat("20220808"),
                                               "Buy 100 GABELLI EQUITY TRUST INC ",
                                               "BUY",
                                               Decimal(100),
                                               Money(Decimal("-2408.99216"), "EUR"),
                                               Money(Decimal("-2456"), "USD")))
        trade.add_transaction(StockTransaction("0850409",
                                               date.fromisoformat("20221122"),
                                               "Buy 100 GABELLI EQUITY TRUST INC ",
                                               "BUY",
                                               Decimal(100),
                                               Money(Decimal("-2185.6786"), "EUR"),
                                               Money(Decimal("-2252"), "USD")))

        returns, unconsumed_returns, unconsumed_accruals = trade.calculate_returns()

        self.assertEqual(0, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(3, len(unconsumed_accruals))

    def test_profit_assign_long_close(self):
        trade = StockTrade("HON", "HONEYWELL INTERNATIONAL INC")
        trade.add_transaction(StockTransaction("3328647",
                                               date.fromisoformat("20220617"),
                                               "Buy 100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                               "BUY",
                                               Decimal(100),
                                               Money(Decimal("-17626.8"), "EUR"),
                                               Money(Decimal("-18500"), "USD")))
        trade.add_transaction(StockTransaction("3118332",
                                               date.fromisoformat("20220805"),
                                               "Sell -100 HONEYWELL INTERNATIONAL INC (Assignment)",
                                               "SELL",
                                               Decimal(-100),
                                               Money(Decimal("17900.272322904"), "EUR"),
                                               Money(Decimal("18249.569075"), "USD")))

        returns, unconsumed_returns, unconsumed_accruals = trade.calculate_returns()

        self.assertEqual(1, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))

        profit = returns[0].calculate_profit()
        self.assertEqual(Money(Decimal("273.472322904"), "EUR"), profit.profit_base)
        self.assertEqual(1, len(profit.accruals))

    def test_profit_assign_long_close_next_year(self):
        trade = StockTrade("BAC", "BANK OF AMERICA CORP")
        trade.add_transaction(StockTransaction("1338170",
                                               date.fromisoformat("20220614"),
                                               "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                               "BUY",
                                               Decimal(100),
                                               Money(Decimal("-3733.587"), "EUR"),
                                               Money(Decimal("-3900"), "USD")))
        trade.add_transaction(StockTransaction("3333809",
                                               date.fromisoformat("20220617"),
                                               "Buy 100 BANK OF AMERICA CORP (Assignment)",
                                               "BUY",
                                               Decimal(100),
                                               Money(Decimal("-3715.92"), "EUR"),
                                               Money(Decimal("-3900"), "USD")))
        trade.add_transaction(StockTransaction("8488811",
                                               date.fromisoformat("20240531"),
                                               "Sell -200 BANK OF AMERICA CORP (Assignment)",
                                               "SELL",
                                               Decimal(-200),
                                               Money(Decimal("7153.146"), "EUR"),
                                               Money(Decimal("7800"), "USD")))

        returns, unconsumed_returns, unconsumed_accruals = trade.calculate_returns()

        self.assertEqual(1, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))

        profit = returns[0].calculate_profit()
        self.assertEqual(Money(Decimal("-296.361"), "EUR"), profit.profit_base)
        self.assertEqual(2, len(profit.accruals))
        self.assertEqual(2024, returns[0].transaction.date.year)

    def test_profit_assign_long_close_in_steps(self):
        trade = StockTrade("MO", "ALTRIA GROUP INC")
        trade.add_transaction(StockTransaction("0074324",
                                               date.fromisoformat("20231101"),
                                               "Buy 200 ALTRIA GROUP INC (Assignment)",
                                               "BUY",
                                               Decimal(200),
                                               Money(Decimal("-7908.18"), "EUR"),
                                               Money(Decimal("-8400"), "USD")))
        trade.add_transaction(StockTransaction("5593418",
                                               date.fromisoformat("20231201"),
                                               "Sell -100 ALTRIA GROUP INC (Assignment)",
                                               "SELL",
                                               Decimal(-100),
                                               Money(Decimal("3875.841611877"), "EUR"),
                                               Money(Decimal("4199.9519"), "USD")))
        trade.add_transaction(StockTransaction("7583880",
                                               date.fromisoformat("20240321"),
                                               "Sell -100 ALTRIA GROUP INC (Assignment)",
                                               "SELL",
                                               Decimal(-100),
                                               Money(Decimal("3932.525"), "EUR"),
                                               Money(Decimal("4250"), "USD")))

        returns, unconsumed_returns, unconsumed_accruals = trade.calculate_returns()

        self.assertEqual(2, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))

        profit = returns[0].calculate_profit()
        self.assertEqual(Money(Decimal("-78.248388123"), "EUR"), profit.profit_base)
        self.assertEqual(1, len(profit.accruals))
        self.assertEqual(100, profit.accruals[0].consumed_quantity)

        profit = returns[1].calculate_profit()
        self.assertEqual(Money(Decimal("-21.565"), "EUR"), profit.profit_base)
        self.assertEqual(1, len(profit.accruals))
        self.assertEqual(100, profit.accruals[0].consumed_quantity)

    def test_profit_multiple_transactions(self):
        trade = StockTrade("XXX", "X Company")
        trade.add_transaction(StockTransaction("001",
                                               date.fromisoformat("20231101"),
                                               "Buy 200 X Company",
                                               "BUY",
                                               Decimal(200),
                                               Money(Decimal("-200"), "EUR"),
                                               Money(Decimal("-200"), "USD")))
        trade.add_transaction(StockTransaction("002",
                                               date.fromisoformat("20231102"),
                                               "Sell 100 X Company",
                                               "SELL",
                                               Decimal(-100),
                                               Money(Decimal("110"), "EUR"),
                                               Money(Decimal("110"), "USD")))
        trade.add_transaction(StockTransaction("003",
                                               date.fromisoformat("20231103"),
                                               "Buy 200 X Company",
                                               "BUY",
                                               Decimal(200),
                                               Money(Decimal("-180"), "EUR"),
                                               Money(Decimal("-180"), "USD")))
        trade.add_transaction(StockTransaction("004",
                                               date.fromisoformat("20231104"),
                                               "Sell 300 X Company",
                                               "SELL",
                                               Decimal(-300),
                                               Money(Decimal("360"), "EUR"),
                                               Money(Decimal("360"), "USD")))

        returns, unconsumed_returns, unconsumed_accruals = trade.calculate_returns()

        self.assertEqual(2, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))

        profit = returns[0].calculate_profit()
        self.assertEqual(Money(Decimal("10"), "EUR"), profit.profit_base)
        self.assertEqual(1, len(profit.accruals))
        self.assertEqual(100, profit.accruals[0].consumed_quantity)

        profit = returns[1].calculate_profit()
        self.assertEqual(Money(Decimal("80"), "EUR"), profit.profit_base)
        self.assertEqual(2, len(profit.accruals))
        self.assertEqual(100, profit.accruals[0].consumed_quantity)
        self.assertEqual(200, profit.accruals[1].consumed_quantity)


if __name__ == '__main__':
    unittest.main()
