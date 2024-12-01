from dataclasses import dataclass
from datetime import date

from money import Money


@dataclass
class Interest:
    date: date
    amount: Money
    activity: str
