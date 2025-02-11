from dataclasses import dataclass, field

from transaction import Transaction, BuySell, OpenCloseIndicator
from transaction_collection import to_opening_closing_pairs, TransactionPair


@dataclass
class ForeignCurrencyAccount:
    currency: str
    transactions: list[Transaction] = field(default_factory=list)

    def add_transaction(self, txn: Transaction):
        if txn.amount_orig is None:
            raise ValueError("Transaction amount was not provided")
        if txn.amount_orig.currency != self.currency:
            raise ValueError(f"Transaction currency {txn.amount_orig.currency} does not match this account's currency {self.currency}")
        if txn.quantity != txn.amount_orig.amount:
            raise ValueError("Quantity must match original amount")
        if txn.amount.sign() != txn.amount_orig.sign():
            raise ValueError("Both amounts must have the same sign")
        if txn.amount_orig.is_positive() and txn.buy_sell != BuySell.BUY:
            raise ValueError("Positive amounts must be of type BuySell.BUY")
        elif txn.amount_orig.is_negative() and txn.buy_sell != BuySell.SELL:
            raise ValueError("Negative amounts must be of type BuySell.SELL")
        if not ((txn.buy_sell == BuySell.BUY and txn.open_close == OpenCloseIndicator.OPEN) or
                (txn.buy_sell == BuySell.SELL and txn.open_close == OpenCloseIndicator.CLOSE)):
            raise ValueError("Buy must match open, sell must match close")
        self.transactions.append(txn)

    def transaction_pairs(self, year: int) -> list[TransactionPair]:
        return to_opening_closing_pairs(self.transactions, year)
