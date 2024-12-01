from dataclasses import dataclass
from datetime import date

from money import Money


@dataclass
class Deposit:
    date: date
    amount: Money
    activity: str
