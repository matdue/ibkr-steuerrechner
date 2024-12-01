import pandas as pd
import streamlit as st

from ibkr_steuerrechner.i18n import format_currency
from ibkr_steuerrechner.page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_dividends(df: pd.DataFrame):
    st.header("Dividenden")
    st.write("""Die folgenden Zahlen stammen aus der Kapitalflussrechnung.
         Sie enthalten die Auszahlungen, die Quellensteuern, und die Korrekturbuchungen zur Quellensteuer.
         Allerdings wird nicht unterschieden zwischen Dividenden, Kapitalzuwachs und Return of Capital.
         Daher sollten diese Zahlen nur als Anhaltspunkt interpretiert werden.""")
    st.write("""Der Dividendenbericht von Interactive Brokers schlüsselt alle Dividenden korrekt auf.
         Er ist in der Kontoverwaltung bei den Steuerdokumenten zu finden.""")
    st.write("""Dividendenbericht und Steuerkorrekturen werden in den ersten Monaten des Folgejahres bereitgestellt.""")
    dividends = df["amount"].sum()
    taxes = df["tax"].sum()
    st.write(f"Dividenden: {format_currency(dividends)}")
    st.write(f"Quellensteuern: {format_currency(abs(taxes))}")
    with st.expander("Kapitalflussrechnung (nur Dividenden)", True):
        display_dataframe(df, ["date", "report_date",], ["amount", "tax"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_dividends(report.get_dividends(selected_year))
