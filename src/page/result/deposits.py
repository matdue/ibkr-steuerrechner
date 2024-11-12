import pandas as pd
import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_deposits(df: pd.DataFrame):
    st.header("Ein- und Auszahlungen")
    st.write("""Alle Ein- und Auszahlen werden aufsummiert. Beide Summen dienen nur der Information und sind steuerlich
        nicht relevant.""")
    deposited_funds = df.query("amount >= 0")["amount"].sum()
    withdrawn_funds = df.query("amount < 0")["amount"].sum()
    st.write(f"Einzahlungen: {format_currency(deposited_funds)}")
    st.write(f"Auszahlungen: {format_currency(withdrawn_funds)}")
    with st.expander("Kapitalflussrechnung (nur Ein- und Auszahlungen)", True):
        df["sequence"] = range(len(df))
        display_dataframe(df, ["date"], ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_deposits(report.get_deposits(selected_year))
