import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_dividends(result: Result):
    st.title(f"Dividenden ({result.year})")
    st.write("""Die folgenden Zahlen stammen aus der Kapitalflussrechnung.
         Sie enthalten die Auszahlungen, die Quellensteuern, und die Korrekturbuchungen zur Quellensteuer.
         Allerdings wird nicht unterschieden zwischen Dividenden, Kapitalzuwachs und Return of Capital.
         Daher sollten diese Zahlen nur als Anhaltspunkt interpretiert werden.""")
    st.write("""Der Dividendenbericht von Interactive Brokers schlüsselt alle Dividenden korrekt auf.
         Er ist in der Kontoverwaltung bei den Steuerdokumenten zu finden.""")
    st.write("""Dividendenbericht und Steuerkorrekturen werden in den ersten Monaten des Folgejahres bereitgestellt.""")
    dividends = result.total("amount")
    taxes = result.total("tax")
    st.write(f"Dividenden: {format_currency(dividends)}")
    st.write(f"Quellensteuern: {format_currency(abs(taxes))}")
    with st.expander("Kapitalflussrechnung (nur Dividenden)", True):
        display_dataframe(result.df, ["date", "report_date",], {"amount": "EUR", "tax": "EUR"})
    display_export_buttons(result, f"dividends_{result.year}", f"Dividenden {result.year}", ["amount", "tax"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_dividends(selected_year)
display_dividends(report_result)
