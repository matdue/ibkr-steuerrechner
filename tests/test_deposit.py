import unittest
from datetime import date
from decimal import Decimal

from deposit import Deposit
from money import Money
from testutils import read_report


class DepositTests(unittest.TestCase):
    def test_deposit(self):
        result = read_report("resources/deposit/deposit.csv")

        self.assertEqual(1, len(result._deposits))
        self.assertEqual(Deposit(date.fromisoformat("20220113"),
                                 Money(Decimal(5000), "EUR"),
                                 "Electronic Fund Transfer"), result._deposits[0])

    def test_withdrawal(self):
        result = read_report("resources/deposit/withdrawal.csv")

        self.assertEqual(1, len(result._deposits))
        self.assertEqual(Deposit(date.fromisoformat("20230814"),
                                 Money(Decimal(-3000), "EUR"),
                                 "Disbursement Initiated by John Doe"), result._deposits[0])


if __name__ == '__main__':
    unittest.main()
