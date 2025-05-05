import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_other_fees(result: Result):
    st.title(f"Sonstige Gebühren ({result.year})")
    st.write("""Gebühren, die nicht in Zusammenhang mit Handelsgeschäften stehen. Privatleute können diese Gebühren
        i.d.R. nicht absetzen.""")
    fee_expenses = result.total_negative("amount")
    fee_refunds = result.total_positive("amount")
    st.write(f"Ausgaben: {format_currency(abs(fee_expenses))}")
    st.write(f"Erstattungen: {format_currency(fee_refunds)}")
    st.write(f"Saldo: {format_currency(fee_expenses + fee_refunds)}")
    with st.expander("Kapitalflussrechnung (nur sonstige Gebühren)", True):
        display_dataframe(result.df, ["date"], {"amount": "EUR"})
    display_export_buttons(result, f"fees_{result.year}", f"Sonstige Gebühren {result.year}", ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_other_fees(selected_year)
display_other_fees(report_result)
