from dataclasses import dataclass
from datetime import date

from money import Money


@dataclass
class Forex:
    tradeId: str
    date: date
    activity: str
    amount: Money
    amount_orig: Money
