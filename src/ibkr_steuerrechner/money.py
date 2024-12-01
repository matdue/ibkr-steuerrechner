import numbers
from dataclasses import dataclass
from decimal import Decimal
from typing import Self


class CurrencyMismatchError(Exception):
    def __init__(self, msg: str, expected_currency: str, found_currency: str):
        super().__init__(msg)
        self.expected_currency = expected_currency
        self.found_currency = found_currency


@dataclass
class Money:
    amount: Decimal
    currency: str

    def _validate_money_with_same_currency(self, other: Self):
        if not isinstance(other, Money):
            raise TypeError("Operand must be of type Money")
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"Expected currency {self.currency}, got currency {other.currency}",
                                        self.currency,
                                        other.currency)

    @staticmethod
    def _validate_number(other):
        if not isinstance(other, numbers.Number):
            raise TypeError("Operand must be a number")

    def __add__(self, other: Self) -> Self:
        self._validate_money_with_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __sub__(self, other: Self) -> Self:
        self._validate_money_with_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, other) -> Self:
        self._validate_number(other)
        return Money(self.amount * other, self.currency)

    def __truediv__(self, other) -> Self:
        self._validate_number(other)
        return Money(self.amount / other, self.currency)

    def __eq__(self, other) -> bool:
        self._validate_money_with_same_currency(other)
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other) -> bool:
        self._validate_money_with_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other) -> bool:
        self._validate_money_with_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other) -> bool:
        self._validate_money_with_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other) -> bool:
        self._validate_money_with_same_currency(other)
        return self.amount >= other.amount

    def __ne__(self, other) -> Self:
        return not self.__eq__(other)

    def __neg__(self) -> Self:
        return Money(-self.amount, self.currency)

    def __abs__(self) -> Self:
        return Money(abs(self.amount), self.currency)

    def __float__(self):
        return float(self.amount)

    def as_zero(self) -> Self:
        return Money(Decimal(0).quantize(self.amount), self.currency)

    def with_value(self, value: Decimal) -> Self:
        return Money(value, self.currency)

    def with_value_keep_precision(self, value: Decimal) -> Self:
        return Money(value.quantize(self.amount), self.currency)

    def is_positive(self) -> bool:
        return self.amount > 0

    def is_zero(self) -> bool:
        return self.amount == 0

    def is_non_negative(self) -> bool:
        return self.amount >= 0

    def is_negative(self) -> bool:
        return self.amount < 0

    def sign(self) -> int:
        return 1 if self.amount >= 0 else -1

    def copy_sign(self, other: Self) -> Self:
        return Money(self.amount.copy_sign(other.amount), self.currency)

    def quantize(self, exp: Self, rounding=None, context=None):
        return Money(self.amount.quantize(exp.amount, rounding, context), self.currency)
