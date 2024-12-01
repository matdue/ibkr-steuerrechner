import unittest
from datetime import date
from decimal import Decimal

from dividend import Dividend
from flex_query import read_report
from money import Money
from report import Report


class DepositTests(unittest.TestCase):
    def test_ordinary(self):
        df = read_report("resources/dividends/ordinary.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(4, len(result._dividends))
        self.assertEqual([
            Dividend(date.fromisoformat("20220328"),
                     date.fromisoformat("20220328"),
                     Money(Decimal("56.88875"), "EUR"),
                     "GAB PRK(US3623978463) Cash Dividend USD 0.3125 per Share (Ordinary Dividend)",
                     "1058032",
                     False,
                     False),
            Dividend(date.fromisoformat("20220328"),
                     date.fromisoformat("20220328"),
                     Money(Decimal("-8.5378636"), "EUR"),
                     "GAB PRK(US3623978463) Cash Dividend USD 0.3125 per Share - US Tax",
                     "1058032",
                     True,
                     False),
            Dividend(date.fromisoformat("20220328"),
                     date.fromisoformat("20230213"),
                     Money(Decimal("8.7462872"), "EUR"),
                     "GAB PRK(US3623978463) Cash Dividend USD 0.3125 per Share - US Tax",
                     "1058032",
                     True,
                     True),
            Dividend(date.fromisoformat("20220328"),
                     date.fromisoformat("20230213"),
                     Money(Decimal("-0.6806812"), "EUR"),
                     "GAB PRK(US3623978463) Cash Dividend USD 0.3125 per Share - US Tax",
                     "1058032",
                     True,
                     True)
        ], result._dividends)

    def test_payment_in_lieu(self):
        df = read_report("resources/dividends/payment_in_lieu.csv")
        result = Report()

        df.apply(lambda row: result.process(row), axis=1)
        result.finish(date.today())

        self.assertEqual(2, len(result._dividends))
        self.assertEqual([
            Dividend(date.fromisoformat("20240501"),
                     date.fromisoformat("20240501"),
                     Money(Decimal("56.0064"), "EUR"),
                     "MPW(US58463J3041) Payment in Lieu of Dividend (Ordinary Dividend)",
                     "7220595",
                     False,
                     False),
            Dividend(date.fromisoformat("20240501"),
                     date.fromisoformat("20240501"),
                     Money(Decimal("-8.40096"), "EUR"),
                     "MPW(US58463J3041) Payment in Lieu of Dividend - US Tax",
                     "7220595",
                     True,
                     False)
        ], result._dividends)


if __name__ == '__main__':
    unittest.main()
