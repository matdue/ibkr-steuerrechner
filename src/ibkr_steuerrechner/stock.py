import dataclasses
import operator
from collections import deque
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum, auto
from functools import reduce
from typing import Self, Deque

from ibkr_steuerrechner.money import Money


class StockType(Enum):
    LONG = auto()
    SHORT = auto()


@dataclass
class StockTransaction:
    tradeId: str
    date: date
    activity: str
    buy_or_sell: str
    quantity: Decimal
    amount: Money
    amount_orig: Money

    def __post_init__(self):
        if self.buy_or_sell not in ["BUY", "SELL"]:
            raise ValueError("buy_or_sell must be either BUY or SELL")


@dataclass
class AccrualTransaction:
    transaction: StockTransaction
    consumed_quantity: Decimal = Decimal(0)

    def consumed(self) -> Decimal:
        return self.consumed_quantity

    def unconsumed(self) -> Decimal:
        return self.transaction.quantity - self.consumed()

    def is_consumed(self) -> bool:
        return self.transaction.quantity == self.consumed()

    def consume(self, quantity: Decimal) -> Self:
        self.consumed_quantity += quantity
        return self

    def consumed_amount(self):
        return self.transaction.amount * (self.consumed_quantity / self.transaction.quantity)


@dataclass
class ReturnTransaction:
    transaction: StockTransaction
    consumed_from: list[AccrualTransaction] = field(default_factory=list)

    def consumed(self) -> Decimal:
        sum_accruals = reduce(operator.add,
                              (accrual.consumed() for accrual in self.consumed_from),
                              Decimal(0))
        return sum_accruals

    def unconsumed(self) -> Decimal:
        return self.transaction.quantity + self.consumed()

    def is_consumed(self) -> bool:
        return self.transaction.quantity + self.consumed() == Decimal(0)

    def consume(self, accrual: StockTransaction, quantity: Decimal):
        accrual_transaction = AccrualTransaction(accrual, quantity)
        self.consumed_from.append(accrual_transaction)

    @dataclass
    class Profit:
        profit_base: Money
        accruals: list[AccrualTransaction]

    def calculate_profit(self):
        accruals_amount = (accrual.consumed_amount() for accrual in self.consumed_from)
        sum_accruals = reduce(operator.add, accruals_amount, self.transaction.amount.as_zero())
        return ReturnTransaction.Profit(self.transaction.amount + sum_accruals, self.consumed_from)


@dataclass
class StockTrade:
    symbol: str
    description: str
    transactions: list[StockTransaction] = field(default_factory=list)
    closed: bool = False

    def stock_type(self):
        match self.transactions[0].buy_or_sell:
            case "SELL":
                return StockType.SHORT
            case "BUY":
                return StockType.LONG

    def close(self):
        self.closed = True

    def add_transaction(self, transaction: StockTransaction):
        if self.closed:
            raise ValueError("Cannot modify a closed trade")
        quantity_sum = reduce(operator.add, (t.quantity for t in self.transactions), Decimal(0))
        quantity_sum_plus_transaction = quantity_sum + transaction.quantity
        if quantity_sum_plus_transaction == 0 or quantity_sum.is_signed() == quantity_sum_plus_transaction.is_signed():
            # Given transaction closes this trade, increases its total quantity, or decreases its total quantity
            # without surpassing zero (i.e. positive total quantity would become negative)
            self.transactions.append(transaction)
            quantity_sum = reduce(operator.add, (t.quantity for t in self.transactions), Decimal(0))
            if quantity_sum == 0:
                self.close()
            return None
        else:
            # Given transaction closes the trade, and there is some quantity left
            # Example: This trade has a quantity of 1, and transaction has a quantity of -3
            # I.e. this trade will be closed, and there is a quantity of -2 left which would open another trade
            quantity_to_close = min(abs(quantity_sum), abs(transaction.quantity)).copy_sign(transaction.quantity)
            fraction_to_close = quantity_to_close / transaction.quantity
            closing_transaction = dataclasses.replace(
                transaction,
                quantity=quantity_to_close,
                amount=transaction.amount * fraction_to_close,
                amount_orig=transaction.amount_orig * fraction_to_close
            )
            self.transactions.append(closing_transaction)
            self.close()

            remaining_transaction = dataclasses.replace(
                transaction,
                quantity=transaction.quantity - closing_transaction.quantity,
                amount=transaction.amount - closing_transaction.amount,
                amount_orig=transaction.amount_orig - closing_transaction.amount_orig
            )
            return remaining_transaction

    def calculate_returns(self):
        if self.stock_type() == StockType.SHORT:
            raise NotImplementedError("Leerverkäufe werden noch nicht unterstützt oder Kauftransaktion fehlt")

        unconsumed_accruals: Deque[AccrualTransaction] = deque()
        unconsumed_returns: Deque[ReturnTransaction] = deque()
        returns: list[ReturnTransaction] = list()

        for transaction in self.transactions:
            if transaction.buy_or_sell == "BUY":
                unconsumed_accruals.append(AccrualTransaction(transaction))
            else:
                unconsumed_returns.append(ReturnTransaction(transaction))

            if len(unconsumed_returns) == 0 or len(unconsumed_accruals) == 0:
                # Nothing to do if there are no pending returns, or no accruals to net the return
                continue

            return_transaction = unconsumed_returns[0]
            while not return_transaction.is_consumed() and len(unconsumed_accruals) != 0:
                accrual = unconsumed_accruals[0]
                quantity_to_consume = min(abs(return_transaction.unconsumed()), abs(accrual.unconsumed()))

                accrual.consume(quantity_to_consume)
                return_transaction.consume(accrual.transaction, quantity_to_consume)

                if accrual.is_consumed():
                    unconsumed_accruals.popleft()
                if return_transaction.is_consumed():
                    returns.append(unconsumed_returns.popleft())

        return returns, list(unconsumed_returns), list(unconsumed_accruals)
