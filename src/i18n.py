from typing import Optional

import babel
import babel.dates
import babel.numbers
import pandas as pd


COLUMN_NAMES = {
    "Report Date": "Berichtsdatum",
    "Activity Date": "Datum der Aktivität",
    "Description": "Beschreibung",
    "Debit": "Soll",
    "Credit": "Haben",
    "Total": "Betrag",
    "Category": "Kategorie",
    "Count": "Anzahl",
    "Name": "Aktie/Option",
    "Profit": "Gewinn/Verlust",
    "Trade": "Trade-Nr.",
    "Action": "Aktion"
}

current_locale = babel.Locale("de_DE")


def format_currency(x) -> Optional[str]:
    if pd.isnull(x):
        return None
    return babel.numbers.format_currency(x, "EUR", locale=current_locale)


def format_date(x) -> Optional[str]:
    if pd.isnull(x):
        return None
    return babel.dates.format_date(x, locale=current_locale)


def get_column_name(column: str) -> str:
    return COLUMN_NAMES[column]
