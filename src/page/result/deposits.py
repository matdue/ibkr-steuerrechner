import streamlit as st

from i18n import format_currency, COLUMN_NAME_EXPORT
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe
from report import Result


@st.fragment
def export_buttons():
    result: Result = st.session_state["report_result"]
    st.download_button("Download als CSV-Datei", st.session_state["csv_export"],
                       file_name=f"deposits_{result.year}.csv",
                       mime="text/csv")
    st.download_button("Download als Excel-Datei", st.session_state["excel_export"],
                       file_name=f"deposits_{result.year}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


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
    export_buttons()


def prepare_exports(result: Result):
    columns = {col: COLUMN_NAME_EXPORT[col] for col in result.df.columns}
    st.session_state["csv_export"] = result.to_csv(columns)
    st.session_state["excel_export"] = result.to_excel(f"Ein- und Auszahlungen {result.year}", columns,
                                                       ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_deposits(selected_year)
st.session_state["report_result"] = report_result
prepare_exports(report_result)
display_deposits(report_result)
