import pandas as pd
import streamlit as st

from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_forexes(df: pd.DataFrame):
    st.header("Forex-Trades")
    with st.expander("Kapitalflussrechnung (nur Forex)", True):
        df["sequence"] = range(len(df))
        display_dataframe(df, ["date"], ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_forexes(report.get_forexes(selected_year))