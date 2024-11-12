from typing import Optional

import babel
import babel.dates
import babel.numbers
import pandas as pd

COLUMN_NAME = {
    "date": "Datum",
    "report_date": "Datum (Kontoauszug)",
    "amount": "Betrag",
    "tax": "Steuern",
    "activity": "Aktivität",
    "no": "Lfd. Nr.",
    "symbol": "Symbol",
    "description": "Beschreibung",
    "expiry": "Fällig am",
    "closed": "Geschlossen",
    "profit": "Gewinn/Verlust",
    "trade_id": "Trade-ID",
    "activity_code": "Code",
    "quantity": "Anzahl",
    "correction": "Korrektur"
}

current_locale = babel.Locale("de_DE")


def format_currency(x, currency: str = "EUR") -> Optional[str]:
    if pd.isnull(x):
        return None
    return babel.numbers.format_currency(x, currency, locale=current_locale)


def format_date(x) -> Optional[str]:
    if pd.isnull(x):
        return None
    return babel.dates.format_date(x, locale=current_locale)
