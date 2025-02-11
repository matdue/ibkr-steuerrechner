import unittest
from datetime import date
from decimal import Decimal

from forex import Forex
from money import Money
from testutils import read_report
from transaction import Transaction, OpenCloseIndicator, BuySell, AcquisitionType


class DepositTests(unittest.TestCase):
    def test_sell_eur_buy_usd(self):
        result = read_report("resources/forex/sell_eur_buy_usd.csv")

        self.assertEqual(1, len(result._forexes))
        self.assertEqual(Forex("7283145",
                               date.fromisoformat("20220512"),
                               "Net Amount in Base from Forex Trade: -10,000 EUR.USD",
                               Money(Decimal("-10015.809655"), "EUR"),
                               Money(Decimal("10371.5"), "USD")), result._forexes[0])
        self.assertEqual(1, len(result._foreign_currency_accounts))
        foreign_currency_bucket = result._foreign_currency_accounts["USD"]
        self.assertEqual(1, len(foreign_currency_bucket.transactions))
        self.assertEqual(Transaction("7283145",
                                     date.fromisoformat("20220512"),
                                     "Net Amount in Base from Forex Trade: -10,000 EUR.USD",
                                     BuySell.BUY,
                                     OpenCloseIndicator.OPEN,
                                     Decimal("10371.50"),
                                     Money(Decimal("10015.81"), "EUR"),
                                     Money(Decimal("10371.50"), "USD"),
                                     Decimal("0.96571"),
                                     AcquisitionType.GENUINE), foreign_currency_bucket.transactions[0])
