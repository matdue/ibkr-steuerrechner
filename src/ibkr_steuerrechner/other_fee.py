from dataclasses import dataclass
from datetime import date

from ibkr_steuerrechner.money import Money


@dataclass
class OtherFee:
    date: date
    amount: Money
    activity: str
