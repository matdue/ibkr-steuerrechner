import unittest
from datetime import date
from decimal import Decimal

from interest import Interest
from money import Money
from testutils import read_report


class InterestTests(unittest.TestCase):
    def test_debit(self):
        result = read_report("resources/interest/debit.csv")

        self.assertEqual(1, len(result._interests))
        self.assertEqual(Interest(date.fromisoformat("20220706"),
                                  Money(Decimal("-9.6538464"), "EUR"),
                                  "USD Debit Interest for Jun-2022"), result._interests[0])

    def test_credit(self):
        result = read_report("resources/interest/credit.csv")

        self.assertEqual(2, len(result._interests))
        self.assertEqual(Interest(date.fromisoformat("20230503"),
                                  Money(Decimal("8.3706696"), "EUR"),
                                  "USD Credit Interest for Apr-2023"), result._interests[0])
        self.assertEqual(Interest(date.fromisoformat("20230503"),
                                  Money(Decimal("6.19"), "EUR"),
                                  "EUR Credit Interest for Apr-2023"), result._interests[1])


if __name__ == '__main__':
    unittest.main()
