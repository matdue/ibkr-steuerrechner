import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_deposits(result: Result):
    st.title(f"Ein- und Auszahlungen ({result.year})")
    st.write("""Alle Ein- und Auszahlen werden aufsummiert. Beide Summen dienen nur der Information und sind steuerlich
        nicht relevant.""")
    deposited_funds = result.total_positive("amount")
    withdrawn_funds = result.total_negative("amount")
    st.write(f"Einzahlungen: {format_currency(deposited_funds)}")
    st.write(f"Auszahlungen: {format_currency(withdrawn_funds)}")
    with st.expander("Kapitalflussrechnung (nur Ein- und Auszahlungen)", True):
        display_dataframe(result.df, ["date"], {"amount": "EUR"})
    display_export_buttons(result, f"deposits_{result.year}", f"Ein- und Auszahlungen {result.year}", ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_deposits(selected_year)
display_deposits(report_result)
