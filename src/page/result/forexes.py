import streamlit as st

from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_forexes(result: Result):
    st.title(f"Forex-Trades ({result.year})")
    with st.expander("Kapitalflussrechnung (nur Forex)", True):
        display_dataframe(result.df, ["date"], {"amount": "EUR"})
    display_export_buttons(result, f"forex_{result.year}", f"Forex {result.year}", ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_forexes(selected_year)
st.session_state["report_result"] = report_result
display_forexes(report_result)
