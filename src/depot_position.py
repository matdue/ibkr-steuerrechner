import operator
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import reduce

from transaction import Transaction, OpenCloseIndicator, BuySell
from transaction_collection import TransactionCollection, to_single_transactions, to_opening_closing_pairs


class DepotPositionType(Enum):
    LONG = auto()
    SHORT = auto()


@dataclass
class DepotPosition:
    symbol: str
    asset_class: str
    transactions: list[Transaction] = field(default_factory=list)
    closed: bool = False

    def add_transaction(self, txn: Transaction):
        self.transactions.append(txn)

        remaining_quantity = reduce(operator.add, (transaction.quantity for transaction in self.transactions))
        if remaining_quantity == 0:
            self.closed = True

    def position_type(self) -> DepotPositionType | None:
        if not self.transactions:
            return None
        first_txn = self.transactions[0]
        if ((first_txn.open_close == OpenCloseIndicator.OPEN and first_txn.buy_sell == BuySell.BUY) or
                (first_txn.open_close == OpenCloseIndicator.CLOSE and first_txn.buy_sell == BuySell.SELL)):
            return DepotPositionType.LONG
        else:
            return DepotPositionType.SHORT

    def transaction_collections(self, year: int) -> list[TransactionCollection]:
        match self.asset_class:
            case "STK" | "BILL":
                return to_opening_closing_pairs(self.transactions, year)
            case "OPT":
                if self.position_type() == DepotPositionType.SHORT:
                    return to_single_transactions(self.transactions, year)
                elif self.position_type() == DepotPositionType.LONG:
                    return to_opening_closing_pairs(self.transactions, year)
        return []
