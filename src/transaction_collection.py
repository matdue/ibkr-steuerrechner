import dataclasses
import operator
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from functools import reduce
from typing import Iterable, Self

from dateutil import relativedelta

from money import Money
from transaction import Transaction, OpenCloseIndicator, AcquisitionType


class TaxRelevance(Enum):
    TAX_RELEVANT = auto()
    TAX_IRRELEVANT = auto()


@dataclass
class TaxableTransaction(Transaction):
    tax_relevance: TaxRelevance = TaxRelevance.TAX_RELEVANT

    @classmethod
    def from_transaction(cls, transaction: Transaction, tax_relevance: TaxRelevance) -> Self:
        return cls(
            trade_id=transaction.trade_id,
            date=transaction.date,
            activity=transaction.activity,
            buy_sell=transaction.buy_sell,
            open_close=transaction.open_close,
            quantity=transaction.quantity,
            amount=transaction.amount,
            amount_orig=transaction.amount_orig,
            fx_rate=transaction.fx_rate,
            acquisition=transaction.acquisition,
            tax_relevance=tax_relevance
        )


class TransactionCollection(ABC):
    @abstractmethod
    def profit(self) -> Money:
        pass

    @abstractmethod
    def is_closed(self) -> bool:
        pass

    @abstractmethod
    def get_closing_transaction(self) -> TaxableTransaction:
        pass

    @abstractmethod
    def get_opening_transactions(self) -> list[TaxableTransaction]:
        pass


@dataclass
class SingleTransaction(TransactionCollection):
    transaction: TaxableTransaction

    def profit(self) -> Money:
        return self.transaction.amount

    def is_closed(self) -> bool:
        return True

    def get_closing_transaction(self) -> TaxableTransaction:
        return self.transaction

    def get_opening_transactions(self) -> list[TaxableTransaction]:
        return []


@dataclass
class TransactionPair(TransactionCollection):
    closing_transaction: TaxableTransaction
    opening_transactions: list[TaxableTransaction] = dataclasses.field(default_factory=list)

    def profit(self) -> Money:
        opening_amount = reduce(operator.add, (txn.amount for txn in self.opening_transactions))
        if self.closing_transaction.amount is None:
            return opening_amount
        return opening_amount + self.closing_transaction.amount

    def is_closed(self) -> bool:
        opening_quantity = reduce(operator.add, (txn.quantity for txn in self.opening_transactions), Decimal(0))
        total_quantity = self.closing_transaction.quantity + opening_quantity
        return total_quantity.is_zero()

    def get_closing_transaction(self) -> TaxableTransaction:
        return self.closing_transaction

    def get_opening_transactions(self) -> list[TaxableTransaction]:
        return self.opening_transactions


def to_single_transactions(transactions: Iterable[Transaction], year: int) -> list[SingleTransaction]:
    return [SingleTransaction(TaxableTransaction.from_transaction(transaction, TaxRelevance.TAX_RELEVANT))
            for transaction in transactions
            if transaction.date.year == year and transaction.amount is not None]


def to_opening_closing_pairs(transactions: Iterable[Transaction], year: int) -> list[TransactionPair]:
    # Build pairs of one (or more) opening transactions and a closing transaction.
    # A closing transaction can have multiple opening transaction if the quantity does not
    # match. An opening transaction might get split up into multiple parts to fit into the closing transaction.
    # The given transactions are processed one by one. If they are sorted by date, they will be processed first-in
    # first-out (FIFO).
    transaction_pairs = list[TransactionPair]()

    opening_transactions = deque[Transaction]()
    closing_transactions = list[Transaction]()
    for transaction in transactions:
        match transaction.open_close:
            case OpenCloseIndicator.OPEN:
                opening_transactions.append(transaction)
            case OpenCloseIndicator.CLOSE:
                closing_transactions.append(transaction)

    for closing_transaction in closing_transactions:
        transaction_pair = TransactionPair(
            closing_transaction=TaxableTransaction.from_transaction(closing_transaction, TaxRelevance.TAX_RELEVANT),
            opening_transactions=[]
        )
        quantity_to_close = closing_transaction.quantity
        while quantity_to_close != 0 and opening_transactions:
            opening_transaction = opening_transactions.popleft()
            if abs(opening_transaction.quantity) <= abs(quantity_to_close):
                transaction_pair.opening_transactions.append(
                    TaxableTransaction.from_transaction(opening_transaction, TaxRelevance.TAX_RELEVANT)
                )
                quantity_to_close += opening_transaction.quantity
            else:
                # Opening transaction is too big and cannot match taxable transaction => split it
                partial_amount_factor = (quantity_to_close / opening_transaction.quantity).copy_abs()
                amount_orig_to_close = ((opening_transaction.amount_orig * partial_amount_factor)
                                        .quantize(Decimal("1.00")))
                amount_to_close = (opening_transaction.amount
                                   .with_value(amount_orig_to_close.amount * opening_transaction.fx_rate)
                                   .quantize(Decimal("1.00")))
                opening_transaction_to_close = dataclasses.replace(
                    opening_transaction,
                    quantity=-quantity_to_close,
                    amount=amount_to_close,
                    amount_orig=amount_orig_to_close
                )
                transaction_pair.opening_transactions.append(
                    TaxableTransaction.from_transaction(opening_transaction_to_close, TaxRelevance.TAX_RELEVANT)
                )
                remaining_opening_transaction = dataclasses.replace(
                    opening_transaction,
                    quantity=opening_transaction.quantity + quantity_to_close,
                    amount=opening_transaction.amount - amount_to_close,
                    amount_orig=opening_transaction.amount_orig - amount_orig_to_close
                )
                opening_transactions.appendleft(remaining_opening_transaction)
                quantity_to_close = 0
        transaction_pairs.append(transaction_pair)

    return [transaction_pair
            for transaction_pair in transaction_pairs
            if transaction_pair.closing_transaction.date.year == year]


def apply_estg_23(transaction_pairs: list[TransactionPair]) -> list[TransactionPair]:

    def apply_to_opening(opening_transaction: TaxableTransaction, closing_transaction: TaxableTransaction):
        if (closing_transaction.tax_relevance == TaxRelevance.TAX_IRRELEVANT or
                opening_transaction.acquisition == AcquisitionType.NON_GENUINE or
                opening_transaction.date + relativedelta.relativedelta(years=+1) < closing_transaction.date):
            override_fx_rate = closing_transaction.fx_rate
            override_amount = (opening_transaction.amount
                               .with_value(opening_transaction.amount_orig.amount * override_fx_rate)
                               .quantize(Decimal("1.00")))
            return dataclasses.replace(opening_transaction,
                                       amount=override_amount,
                                       fx_rate=override_fx_rate,
                                       tax_relevance=TaxRelevance.TAX_IRRELEVANT)
        return dataclasses.replace(opening_transaction)


    def apply(transaction_pair: TransactionPair) -> TransactionPair:
        result_pair = dataclasses.replace(transaction_pair)
        match transaction_pair.closing_transaction.acquisition:
            case AcquisitionType.GENUINE:
                result_pair.closing_transaction.tax_relevance = TaxRelevance.TAX_RELEVANT
            case AcquisitionType.NON_GENUINE:
                result_pair.closing_transaction.tax_relevance = TaxRelevance.TAX_IRRELEVANT

        result_pair.opening_transactions = [apply_to_opening(opening_transaction, result_pair.closing_transaction)
                                            for opening_transaction in result_pair.opening_transactions]
        return result_pair

    return [apply(transaction_pair) for transaction_pair in transaction_pairs]
