import unittest
from decimal import Decimal

import pandas as pd
from pandas.testing import assert_series_equal

from utils import calc_share_trade_profits


class LongTrades(unittest.TestCase):
    def test_long_close_no_profit(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 2000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 0], name="profit", index=result.index).apply(Decimal))

    def test_long_close_with_profit(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 3000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 1000], name="profit", index=result.index).apply(Decimal))

    def test_long_close_with_losses(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 1000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, -1000], name="profit", index=result.index).apply(Decimal))

    def test_two_long_one_close(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": -200, "credit": 5100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 0, 100], name="profit", index=result.index).apply(Decimal))

    def test_one_long_two_close(self):
        df = pd.DataFrame([{"count": 200, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": -100, "credit": 1100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 200, 100], name="profit", index=result.index).apply(Decimal))

    def test_two_long_two_close(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": -100, "credit": 1100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 0, -800, -1900], name="profit", index=result.index).apply(Decimal))

    def test_two_long_two_close_asymmetric(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": 200, "credit": None, "debit": -6000},
                           {"count": -200, "credit": 4000, "debit": None},
                           {"count": -100, "credit": 2000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 0, -1000, -1000], name="profit", index=result.index).apply(Decimal))

    def test_one_long(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0], name="profit", index=result.index).apply(Decimal))

    def test_two_long_two_close_two_trades(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -1000},
                           {"count": -100, "credit": 1100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 200, 0, 100], name="profit", index=result.index).apply(Decimal))

    def test_two_long_one_close_open_trade(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -1000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 200, 0], name="profit", index=result.index).apply(Decimal))


class ShortTrades(unittest.TestCase):
    def test_short_close_no_profit(self):
        df = pd.DataFrame([{"count": -100, "credit": 2000, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([0, 0], name="profit", index=result.index).apply(Decimal))

    def test_short_close_with_profit(self):
        df = pd.DataFrame([{"count": -100, "credit": 3000, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([1000, 0], name="profit", index=result.index).apply(Decimal))

    def test_short_close_with_losses(self):
        df = pd.DataFrame([{"count": -100, "credit": 1000, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([-1000, 0], name="profit", index=result.index).apply(Decimal))

    def test_one_short_two_close(self):
        df = pd.DataFrame([{"count": -200, "credit": 5100, "debit": None},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([100, 0, 0], name="profit", index=result.index).apply(Decimal))

    def test_two_short_one_close(self):
        df = pd.DataFrame([{"count": -100, "credit": 1100, "debit": None},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": 200, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([100, 200, 0], name="profit", index=result.index).apply(Decimal))

    def test_two_short_two_close(self):
        df = pd.DataFrame([{"count": -100, "credit": 1100, "debit": None},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([-1900, -800, 0, 0], name="profit", index=result.index).apply(Decimal))

    def test_two_short_two_close_asymmetric(self):
        df = pd.DataFrame([{"count": -100, "credit": 2000, "debit": None},
                           {"count": -200, "credit": 4000, "debit": None},
                           {"count": 200, "credit": None, "debit": -6000},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([-1000, -1000, 0, 0], name="profit", index=result.index).apply(Decimal))

    def test_one_short(self):
        df = pd.DataFrame([{"count": -100, "credit": 2000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([2000], name="profit", index=result.index).apply(Decimal))

    def test_two_short_two_close_two_trades(self):
        df = pd.DataFrame([{"count": -100, "credit": 1100, "debit": None},
                           {"count": 100, "credit": None, "debit": -1000},
                           {"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([100, 0, 200, 0], name="profit", index=result.index).apply(Decimal))

    def test_two_short_one_close_open_trade(self):
        df = pd.DataFrame([{"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 1000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_series_equal(result,
                            pd.Series([200, 0, 1000], name="profit", index=result.index).apply(Decimal))