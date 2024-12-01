from dataclasses import dataclass
from datetime import date

from money import Money


@dataclass
class OtherFee:
    date: date
    amount: Money
    activity: str
