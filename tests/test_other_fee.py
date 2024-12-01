import unittest
from datetime import date
from decimal import Decimal

from ibkr_steuerrechner.flex_query import read_report
from ibkr_steuerrechner.money import Money
from ibkr_steuerrechner.other_fee import OtherFee
from ibkr_steuerrechner.report import Report


class OtherFeeTests(unittest.TestCase):
    def test_expense(self):
        df = read_report("resources/other_fee/expense.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(2, len(result._other_fees))
        self.assertEqual(OtherFee(date.fromisoformat("20220303"),
                                  Money(Decimal("-1.35"), "EUR"),
                                  "M******66:OPRA NP L1 FOR MAR 2022"), result._other_fees[0])
        self.assertEqual(OtherFee(date.fromisoformat("20220303"),
                                  Money(Decimal("-0.2565"), "EUR"),
                                  "VAT m******66:OPRA NP L1"), result._other_fees[1])

    def test_refund(self):
        df = read_report("resources/other_fee/refund.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(1, len(result._other_fees))
        self.assertEqual(OtherFee(date.fromisoformat("20220404"),
                                  Money(Decimal("1.35"), "EUR"),
                                  "M******66:OPRA NP L1 FOR MAR 2022"), result._other_fees[0])


if __name__ == '__main__':
    unittest.main()
