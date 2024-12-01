import unittest
from datetime import date
from decimal import Decimal

from ibkr_steuerrechner.flex_query import read_report
from ibkr_steuerrechner.foreign_currency_bucket import ForeignCurrencyFlow, TaxRelevance
from ibkr_steuerrechner.forex import Forex
from ibkr_steuerrechner.money import Money
from ibkr_steuerrechner.report import Report


class DepositTests(unittest.TestCase):
    def test_sell_eur_buy_usd(self):
        df = read_report("resources/forex/sell_eur_buy_usd.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._forexes))
        self.assertEqual(Forex("7283145",
                               date.fromisoformat("20220512"),
                               "Net Amount in Base from Forex Trade: -10,000 EUR.USD",
                               Money(Decimal("-10015.809655"), "EUR"),
                               Money(Decimal("10371.5"), "USD")), result._forexes[0])
        self.assertEqual(1, len(result._foreign_currency_buckets))
        foreign_currency_bucket = result._foreign_currency_buckets["USD"]
        self.assertEqual(1, len(foreign_currency_bucket.flows))
        self.assertEqual(ForeignCurrencyFlow("7283145",
                                             date.fromisoformat("20220512"),
                                             "Net Amount in Base from Forex Trade: -10,000 EUR.USD",
                                             Money(Decimal("-10015.809655"), "EUR"),
                                             Money(Decimal("10371.5"), "USD"),
                                             Decimal("0.96339"),
                                             TaxRelevance.TAX_RELEVANT), foreign_currency_bucket.flows[0])
