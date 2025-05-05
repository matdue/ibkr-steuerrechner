import streamlit as st

from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_unknown_lines(result: Result):
    st.title(f"Sonstiges ({result.year})")
    st.write("""Im Kontoauszug gibt es einige Zeilen, die nicht zugeordnet werden können. Sie werden hier aufgelistet
        und haben keinen Einfluss auf die Berechnungen.""")
    with st.expander("Kapitalflussrechnung (nur Sonstiges)", True):
        display_dataframe(result.df, ["date"], {"amount": "EUR"})
    display_export_buttons(result, f"unknown_lines_{result.year}", f"Sonstiges {result.year}", ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_unknown_lines(selected_year)
display_unknown_lines(report_result)
