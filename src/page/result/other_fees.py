import streamlit as st

from i18n import format_currency, COLUMN_NAME_EXPORT
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe
from report import Result


@st.fragment
def export_buttons():
    result: Result = st.session_state["report_result"]
    st.download_button("Download als CSV-Datei", st.session_state["csv_export"],
                       file_name=f"fees_{result.year}.csv",
                       mime="text/csv")
    st.download_button("Download als Excel-Datei", st.session_state["excel_export"],
                       file_name=f"fees_{result.year}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


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
    export_buttons()


def prepare_exports(result: Result):
    columns = {col: COLUMN_NAME_EXPORT[col] for col in result.df.columns}
    st.session_state["csv_export"] = result.to_csv(columns)
    st.session_state["excel_export"] = result.to_excel(f"Sonstige Gebühren {result.year}", columns,
                                                       ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_other_fees(selected_year)
st.session_state["report_result"] = report_result
prepare_exports(report_result)
display_other_fees(report_result)
