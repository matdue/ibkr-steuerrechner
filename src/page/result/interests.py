import pandas as pd
import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_interests(df: pd.DataFrame):
    st.header("Zinsen")
    st.write("""Zinseinnahmen müssen versteuert werden (Abgeltungssteuer). Zinsausgaben können von Privatpersonen i.d.R.
        nicht angerechnet werden.""")
    earned_interests = df.query("amount >= 0")["amount"].sum()
    payed_interests = df.query("amount < 0")["amount"].sum()
    st.write(f"Einnahmen: {format_currency(earned_interests)}")
    st.write(f"Ausgaben: {format_currency(abs(payed_interests))}")
    st.write(f"Saldo: {format_currency(earned_interests + payed_interests)}")
    with st.expander("Kapitalflussrechnung (nur Zinsen)", True):
        df["sequence"] = range(len(df))
        display_dataframe(df, ["date"], ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_interests(report.get_interests(selected_year))
