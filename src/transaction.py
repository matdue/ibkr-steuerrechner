from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum, auto

from money import Money


class BuySell(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OpenCloseIndicator(Enum):
    OPEN = "O"
    CLOSE = "C"


class AcquisitionType(Enum):
    GENUINE = auto()
    NON_GENUINE = auto()


@dataclass
class Transaction:
    trade_id: str | None
    date: date
    activity: str | None
    buy_sell: BuySell | None
    open_close: OpenCloseIndicator
    quantity: Decimal
    amount: Money | None
    amount_orig: Money | None
    fx_rate: Decimal | None  # amount_orig * fx_rate = amount
    acquisition: AcquisitionType = AcquisitionType.GENUINE
