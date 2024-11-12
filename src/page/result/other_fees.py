import pandas as pd
import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_other_fees(df: pd.DataFrame):
    st.header("Sonstige Gebühren")
    st.write("""Gebühren, die nicht in Zusammenhang mit Handelsgeschäften stehen. Privatleute können diese Gebühren
        i.d.R. nicht absetzen.""")
    fee_expenses = df.query("amount < 0")["amount"].sum()
    fee_refunds = df.query("amount >= 0")["amount"].sum()
    st.write(f"Ausgaben: {format_currency(abs(fee_expenses))}")
    st.write(f"Erstattungen: {format_currency(fee_refunds)}")
    st.write(f"Saldo: {format_currency(fee_expenses + fee_refunds)}")
    with st.expander("Kapitalflussrechnung (nur sonstige Gebühren)", True):
        df["sequence"] = range(len(df))
        display_dataframe(df, ["date"], ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_other_fees(report.get_other_fees(selected_year))
