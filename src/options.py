import dataclasses
import operator
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum, auto
from functools import reduce

from money import Money


class OptionType(Enum):
    STILLHALTERGESCHAEFT = auto()
    TERMINGESCHAEFT = auto()


@dataclass
class OptionTransaction:
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
class OptionTrade:
    symbol: str
    description: str
    expiry: date
    transactions: list[OptionTransaction] = field(default_factory=list)
    closed: bool = False

    @dataclass
    class Profit:
        total: Money = None
        total_orig: Money = None
        transactions: list[OptionTransaction] = field(default_factory=list)

        def calculate_profit(self):
            if len(self.transactions) == 0:
                return
            self.total = reduce(operator.add, (trade.amount for trade in self.transactions))
            self.total_orig = reduce(operator.add, (trade.amount_orig for trade in self.transactions))

    def option_type(self):
        match self.transactions[0].buy_or_sell:
            case "SELL":
                return OptionType.STILLHALTERGESCHAEFT
            case "BUY":
                return OptionType.TERMINGESCHAEFT

    def close(self):
        self.closed = True

    def calculate_profit_per_year(self, cut_off_dates: dict[int, date]):
        profit_per_year: dict[int, OptionTrade.Profit] = {}
        for transaction in self.transactions:
            profit = profit_per_year.get(transaction.date.year)
            if profit is None:
                profit = OptionTrade.Profit()
                profit_per_year[transaction.date.year] = profit

            if self.option_type() == OptionType.TERMINGESCHAEFT:
                # Common case: Assign Termingeschäft trade to the year when it happens
                profit.transactions.append(transaction)
            elif self.option_type() == OptionType.STILLHALTERGESCHAEFT:
                if transaction.buy_or_sell == "SELL":
                    # Common case: Assign Stillhalter trade to the year when it happens
                    profit.transactions.append(transaction)
                elif transaction.buy_or_sell == "BUY":
                    # Glattstellungsgeschäft can be moved back to the year when income was generated
                    # (in order to reduce taxes on that income as it gets reduced)
                    for year, profit_in_year in profit_per_year.items():
                        cut_off_date = cut_off_dates.get(year, date(year, 12, 31))
                        if transaction.date > cut_off_date:
                            continue
                        open_quantity = reduce(operator.add, (t.quantity
                                                              for y in profit_per_year.keys()
                                                              if y <= year
                                                              for t in profit_per_year[y].transactions))
                        quantity_to_close = (min(abs(open_quantity), abs(transaction.quantity))
                                             .copy_sign(transaction.quantity))
                        fraction_to_close = quantity_to_close / transaction.quantity
                        closing_transaction = dataclasses.replace(
                            transaction,
                            quantity=quantity_to_close,
                            amount=transaction.amount * fraction_to_close,
                            amount_orig=transaction.amount_orig * fraction_to_close
                        )
                        profit_in_year.transactions.append(closing_transaction)
                        if transaction.quantity - closing_transaction.quantity == 0:
                            break

                        # Create transaction with remaining quantity
                        transaction = dataclasses.replace(
                            transaction,
                            quantity=transaction.quantity - closing_transaction.quantity,
                            amount=transaction.amount - closing_transaction.amount,
                            amount_orig=transaction.amount_orig - closing_transaction.amount_orig
                        )

        for profit in profit_per_year.values():
            profit.calculate_profit()
        return profit_per_year

    def add_transaction(self, transaction: OptionTransaction):
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
