import pandas as pd
import streamlit as st

from ibkr_steuerrechner.page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_unknown_lines(df: pd.DataFrame):
    st.header("Sonstiges")
    st.write("""Im Kontoauszug gibt es einige Zeilen, die nicht zugeordnet werden können. Sie werden hier aufgelistet
        und haben keinen Einfluss auf die Berechnungen.""")
    with st.expander("Kapitalflussrechnung (nur Sonstiges)", True):
        df["sequence"] = range(len(df))
        display_dataframe(df, ["date"], ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_unknown_lines(report.get_unknown_lines(selected_year))
