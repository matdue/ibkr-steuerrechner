import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_interests(result: Result):
    st.title(f"Zinsen ({result.year})")
    st.write("""Zinseinnahmen müssen versteuert werden (Abgeltungssteuer). Zinsausgaben können von Privatpersonen i.d.R.
        nicht angerechnet werden.""")
    earned_interests = result.total_positive("amount")
    payed_interests = result.total_negative("amount")
    st.write(f"Einnahmen: {format_currency(earned_interests)}")
    st.write(f"Ausgaben: {format_currency(abs(payed_interests))}")
    st.write(f"Saldo: {format_currency(earned_interests + payed_interests)}")
    with st.expander("Kapitalflussrechnung (nur Zinsen)", True):
        display_dataframe(result.df, ["date"], {"amount": "EUR"})
    display_export_buttons(result, f"interests_{result.year}", f"Zinsen {result.year}", ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_interests(selected_year)
st.session_state["report_result"] = report_result
display_interests(report_result)
