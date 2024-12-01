import unittest
from decimal import Decimal

from ibkr_steuerrechner.money import Money, CurrencyMismatchError


class MoneyTests(unittest.TestCase):
    def test_add(self):
        m = Money(Decimal(100), "EUR")
        result = m + Money(Decimal(5), "EUR")
        self.assertEqual(Money(Decimal(105), "EUR"), result)

    def test_radd(self):
        result = 0 + Money(Decimal(5), "EUR")
        self.assertEqual(Money(Decimal(5), "EUR"), result)

    def test_sub(self):
        m = Money(Decimal(100), "EUR")
        result = m - Money(Decimal(5), "EUR")
        self.assertEqual(Money(Decimal(95), "EUR"), result)

    def test_mul(self):
        m = Money(Decimal(100), "EUR")
        result = m * 5
        self.assertEqual(Money(Decimal(500), "EUR"), result)

    def test_truediv(self):
        m = Money(Decimal(100), "EUR")
        result = m / 5
        self.assertEqual(Money(Decimal(20), "EUR"), result)

    def test_eq(self):
        m = Money(Decimal(100), "EUR")
        result = m == Money(Decimal(100), "EUR")
        self.assertTrue(result)

        result = m == Money(Decimal(200), "EUR")
        self.assertFalse(result)

    def test_ne(self):
        m = Money(Decimal(100), "EUR")
        result = m != Money(Decimal(200), "EUR")
        self.assertTrue(result)

        result = m != Money(Decimal(100), "EUR")
        self.assertFalse(result)

    def test_lt(self):
        m = Money(Decimal(100), "EUR")
        result = m < Money(Decimal(200), "EUR")
        self.assertTrue(result)

        result = m < Money(Decimal(100), "EUR")
        self.assertFalse(result)

    def test_le(self):
        m = Money(Decimal(100), "EUR")
        result = m <= Money(Decimal(200), "EUR")
        self.assertTrue(result)

        result = m <= Money(Decimal(100), "EUR")
        self.assertTrue(result)

        result = m <= Money(Decimal(90), "EUR")
        self.assertFalse(result)

    def test_gt(self):
        m = Money(Decimal(100), "EUR")
        result = m > Money(Decimal(50), "EUR")
        self.assertTrue(result)

        result = m > Money(Decimal(100), "EUR")
        self.assertFalse(result)

    def test_ge(self):
        m = Money(Decimal(100), "EUR")
        result = m >= Money(Decimal(50), "EUR")
        self.assertTrue(result)

        result = m >= Money(Decimal(100), "EUR")
        self.assertTrue(result)

        result = m >= Money(Decimal(200), "EUR")
        self.assertFalse(result)

    def test_neg(self):
        m = Money(Decimal(100), "EUR")
        result = -m
        self.assertEqual(Money(Decimal(-100), "EUR"), result)

        m = Money(Decimal(0), "EUR")
        result = -m
        self.assertEqual(Money(Decimal(0), "EUR"), result)

    def test_as_zero(self):
        m = Money(Decimal(100), "EUR")
        result = m.as_zero()
        self.assertEqual(Money(Decimal(0), "EUR"), result)

    def test_with_value(self):
        m = Money(Decimal(100), "EUR")
        result = m.with_value(Decimal(200))
        self.assertEqual(Money(Decimal(200), "EUR"), result)

    def test_is_positive(self):
        m = Money(Decimal(100), "EUR")
        self.assertTrue(m.is_positive())
        self.assertFalse(m.is_zero())
        self.assertFalse(m.is_negative())
        self.assertTrue((m.is_non_negative()))

    def test_is_zero(self):
        m = Money(Decimal(0), "EUR")
        self.assertFalse(m.is_positive())
        self.assertTrue(m.is_zero())
        self.assertFalse(m.is_negative())
        self.assertTrue((m.is_non_negative()))

    def test_is_negative(self):
        m = Money(Decimal(-100), "EUR")
        self.assertFalse(m.is_positive())
        self.assertFalse(m.is_zero())
        self.assertTrue(m.is_negative())
        self.assertFalse((m.is_non_negative()))

    def test_add_with_wrong_currency(self):
        m = Money(Decimal(100), "EUR")
        with self.assertRaises(CurrencyMismatchError) as cm:
            m + Money(Decimal(5), "USD")

        the_exception = cm.exception
        self.assertEqual("Expected currency EUR, got currency USD", str(the_exception))
        self.assertEqual("EUR", the_exception.expected_currency)
        self.assertEqual("USD", the_exception.found_currency)

    def test_sign(self):
        positive_money = Money(Decimal(100), "EUR")
        null_money = Money(Decimal(0), "EUR")
        negative_money = Money(Decimal(-100), "EUR")

        self.assertEqual(1, positive_money.sign())
        self.assertEqual(1, null_money.sign())
        self.assertEqual(-1, negative_money.sign())

    def test_copy_sign(self):
        negative_money = Money(Decimal(-100), "EUR")

        money_to_test = Money(Decimal(10), "EUR").copy_sign(negative_money)

        self.assertEqual(Money(Decimal(-10), "EUR"), money_to_test)

    def test_quantize(self):
        money = Money(Decimal("100.00"), "EUR")

        money_to_test = Money(Decimal(10), "EUR").quantize(money)

        self.assertEqual(Money(Decimal("10.00"), "EUR"), money_to_test)
        self.assertEqual(-2, money_to_test.amount.as_tuple().exponent)


if __name__ == '__main__':
    unittest.main()
