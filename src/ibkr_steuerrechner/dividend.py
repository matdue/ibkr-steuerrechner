from dataclasses import dataclass
from datetime import date

from ibkr_steuerrechner.money import Money


@dataclass
class Dividend:
    date: date
    report_date: date
    amount: Money
    activity: str
    action_id: str
    is_tax: bool
    is_correction: bool
