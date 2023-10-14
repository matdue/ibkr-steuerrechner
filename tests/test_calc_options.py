import unittest
from decimal import Decimal

import pandas as pd
from pandas.testing import assert_frame_equal

from utils import calc_share_trade_profits


class LongTrades(unittest.TestCase):
    def test_long_expire(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": None, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(-2000)],
                                         "start_of_trade": [True, False]},
                                        index=result.index))

    def test_long_close_no_profit(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 2000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(0)],
                                          "start_of_trade": [True, False]},
                                        index=result.index))

    def test_long_close_with_profit(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 3000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(1000)],
                                         "start_of_trade": [True, False]},
                                        index=result.index))

    def test_long_close_with_losses(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 1000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(-1000)],
                                         "start_of_trade": [True, False]},
                                        index=result.index))

    def test_two_long_one_close(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": -200, "credit": 5100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(0), Decimal(100)],
                                         "start_of_trade": [True, False, False]},
                                        index=result.index))

    def test_one_long_two_close(self):
        df = pd.DataFrame([{"count": 200, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": -100, "credit": 1100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(200), Decimal(100)],
                                         "start_of_trade": [True, False, False]},
                                        index=result.index))

    def test_two_long_two_close(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": -100, "credit": 1100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(0), Decimal(-800), Decimal(-1900)],
                                         "start_of_trade": [True, False, False, False]},
                                        index=result.index))

    def test_two_long_two_close_asymmetric(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": 200, "credit": None, "debit": -6000},
                           {"count": -200, "credit": 4000, "debit": None},
                           {"count": -100, "credit": 2000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(0), Decimal(-1000), Decimal(-1000)],
                                         "start_of_trade": [True, False, False, False]},
                                        index=result.index))

    def test_one_long(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0)],
                                         "start_of_trade": [True]},
                                        index=result.index))

    def test_two_long_two_close_two_trades(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -1000},
                           {"count": -100, "credit": 1100, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(200), Decimal(0), Decimal(100)],
                                         "start_of_trade": [True, False, True, False]},
                                        index=result.index))

    def test_two_long_one_close_open_trade(self):
        df = pd.DataFrame([{"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -1000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(200), Decimal(0)],
                                         "start_of_trade": [True, False, True]},
                                        index=result.index))


class ShortTrades(unittest.TestCase):
    def test_short_expire(self):
        df = pd.DataFrame([{"count": -100, "credit": 2000, "debit": None},
                           {"count": 100, "credit": None, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(2000), Decimal(0)],
                                         "start_of_trade": [True, False]},
                                        index=result.index))

    def test_short_close_no_profit(self):
        df = pd.DataFrame([{"count": -100, "credit": 2000, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(0), Decimal(0)],
                                         "start_of_trade": [True, False]},
                                        index=result.index))

    def test_short_close_with_profit(self):
        df = pd.DataFrame([{"count": -100, "credit": 3000, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(1000), Decimal(0)],
                                         "start_of_trade": [True, False]},
                                        index=result.index))

    def test_short_close_with_losses(self):
        df = pd.DataFrame([{"count": -100, "credit": 1000, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(-1000), Decimal(0)],
                                         "start_of_trade": [True, False]},
                                        index=result.index))

    def test_one_short_two_close(self):
        df = pd.DataFrame([{"count": -200, "credit": 5100, "debit": None},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(100), Decimal(0), Decimal(0)],
                                         "start_of_trade": [True, False, False]},
                                        index=result.index))

    def test_two_short_one_close(self):
        df = pd.DataFrame([{"count": -100, "credit": 1100, "debit": None},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": 200, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(100), Decimal(200), Decimal(0)],
                                         "start_of_trade": [True, False, False]},
                                        index=result.index))

    def test_two_short_two_close(self):
        df = pd.DataFrame([{"count": -100, "credit": 1100, "debit": None},
                           {"count": -100, "credit": 1200, "debit": None},
                           {"count": 100, "credit": None, "debit": -3000},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(-1900), Decimal(-800), Decimal(0), Decimal(0)],
                                         "start_of_trade": [True, False, False, False]},
                                        index=result.index))

    def test_two_short_two_close_asymmetric(self):
        df = pd.DataFrame([{"count": -100, "credit": 2000, "debit": None},
                           {"count": -200, "credit": 4000, "debit": None},
                           {"count": 200, "credit": None, "debit": -6000},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(-1000), Decimal(-1000), Decimal(0), Decimal(0)],
                                         "start_of_trade": [True, False, False, False]},
                                        index=result.index))

    def test_one_short(self):
        df = pd.DataFrame([{"count": -100, "credit": 2000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(2000)],
                                         "start_of_trade": [True]},
                                        index=result.index))

    def test_two_short_two_close_two_trades(self):
        df = pd.DataFrame([{"count": -100, "credit": 1100, "debit": None},
                           {"count": 100, "credit": None, "debit": -1000},
                           {"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(100), Decimal(0), Decimal(200), Decimal(0)],
                                         "start_of_trade": [True, False, True, False]},
                                        index=result.index))

    def test_two_short_one_close_open_trade(self):
        df = pd.DataFrame([{"count": -100, "credit": 2200, "debit": None},
                           {"count": 100, "credit": None, "debit": -2000},
                           {"count": -100, "credit": 1000, "debit": None}])
        result = calc_share_trade_profits(df, "count", "debit", "credit")
        assert_frame_equal(result,
                           pd.DataFrame({"profit": [Decimal(200), Decimal(0), Decimal(1000)],
                                         "start_of_trade": [True, False, True]},
                                        index=result.index))
