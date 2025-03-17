import streamlit as st

from i18n import format_currency, COLUMN_NAME_EXPORT
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe
from report import Result


@st.fragment
def export_buttons():
    result: Result = st.session_state["report_result"]
    st.download_button("Download als CSV-Datei", st.session_state["csv_export"],
                       file_name=f"dividends_{result.year}.csv",
                       mime="text/csv")
    st.download_button("Download als Excel-Datei", st.session_state["excel_export"],
                       file_name=f"dividends_{result.year}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def display_dividends(result: Result):
    st.title(f"Dividenden ({result.year})")
    st.write("""Die folgenden Zahlen stammen aus der Kapitalflussrechnung.
         Sie enthalten die Auszahlungen, die Quellensteuern, und die Korrekturbuchungen zur Quellensteuer.
         Allerdings wird nicht unterschieden zwischen Dividenden, Kapitalzuwachs und Return of Capital.
         Daher sollten diese Zahlen nur als Anhaltspunkt interpretiert werden.""")
    st.write("""Der Dividendenbericht von Interactive Brokers schlüsselt alle Dividenden korrekt auf.
         Er ist in der Kontoverwaltung bei den Steuerdokumenten zu finden.""")
    st.write("""Dividendenbericht und Steuerkorrekturen werden in den ersten Monaten des Folgejahres bereitgestellt.""")
    dividends = result.total("amount")
    taxes = result.total("tax")
    st.write(f"Dividenden: {format_currency(dividends)}")
    st.write(f"Quellensteuern: {format_currency(abs(taxes))}")
    with st.expander("Kapitalflussrechnung (nur Dividenden)", True):
        display_dataframe(result.df, ["date", "report_date",], {"amount": "EUR", "tax": "EUR"})
    export_buttons()


def prepare_exports(result: Result):
    columns = {col: COLUMN_NAME_EXPORT[col] for col in result.df.columns}
    st.session_state["csv_export"] = result.to_csv(columns)
    st.session_state["excel_export"] = result.to_excel(f"Dividenden {result.year}", columns,
                                                       ["amount", "tax"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_dividends(selected_year)
st.session_state["report_result"] = report_result
prepare_exports(report_result)
display_dividends(report_result)
