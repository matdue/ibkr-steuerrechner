import unittest
from datetime import date
from decimal import Decimal

from money import Money
from other_fee import OtherFee
from testutils import read_report


class OtherFeeTests(unittest.TestCase):
    def test_expense(self):
        result = read_report("resources/other_fee/expense.csv")

        self.assertEqual(2, len(result._other_fees))
        self.assertEqual(OtherFee(date.fromisoformat("20220303"),
                                  Money(Decimal("-1.35"), "EUR"),
                                  "M******66:OPRA NP L1 FOR MAR 2022"), result._other_fees[0])
        self.assertEqual(OtherFee(date.fromisoformat("20220303"),
                                  Money(Decimal("-0.2565"), "EUR"),
                                  "VAT m******66:OPRA NP L1"), result._other_fees[1])

    def test_refund(self):
        result = read_report("resources/other_fee/refund.csv")

        self.assertEqual(1, len(result._other_fees))
        self.assertEqual(OtherFee(date.fromisoformat("20220404"),
                                  Money(Decimal("1.35"), "EUR"),
                                  "M******66:OPRA NP L1 FOR MAR 2022"), result._other_fees[0])


if __name__ == '__main__':
    unittest.main()
