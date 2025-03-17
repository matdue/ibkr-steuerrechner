import pandas as pd
import streamlit as st

from i18n import format_currency, COLUMN_NAME_EXPORT
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe
from report import Result


@st.fragment
def export_buttons():
    result: Result = st.session_state["report_result"]
    st.download_button("Download als CSV-Datei", st.session_state["csv_export"],
                       file_name=f"bonds_{result.year}.csv",
                       mime="text/csv")
    st.download_button("Download als Excel-Datei", st.session_state["excel_export"],
                       file_name=f"bonds_{result.year}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def display_bonds(result: Result, df_all: pd.DataFrame):
    st.title(f"Anleihen ({result.year})")
    st.write("""Gewinne und Verluste aus Käufen, Verkäufen und Ausbuchungen von Anleihen werden nach der
        FIFO-Methode berechnet und hier ausgewiesen. Käufe werden steuerlich erst dann relevant, wenn die
        Position durch Verkauf oder Ausbuchung geschlossen wird. Erfolgt die Schließung im Folgejahr, wird erst dann ein
        Gewinn oder Verlust berechnet.""")
    profitable_trades = result.total_positive("profit")
    lossy_trades = result.total_negative("profit")
    sum_trades = profitable_trades + lossy_trades
    st.write(f"Gewinne aus Anleihenveräußerungen: {format_currency(profitable_trades)}")
    st.write(f"Verluste aus Anleihenveräußerungen: {format_currency(abs(lossy_trades))}")
    st.write(f"Saldo: {format_currency(sum_trades)}")
    with st.expander(f"Kapitalflussrechnung (nur abgeschlossene Anleihengeschäfte)", True):
        display_dataframe(result.df,
                          ["date"],
                          {"amount": "EUR", "profit": "EUR"})
    with st.expander("Kapitalflussrechnung (nur Anleihengeschäfte)"):
        display_dataframe(df_all,
                          ["date"],
                          {"amount": "EUR"})
    export_buttons()


def prepare_exports(result: Result):
    columns = {col: COLUMN_NAME_EXPORT[col] for col in result.df.columns}
    st.session_state["csv_export"] = result.to_csv(columns)
    st.session_state["excel_export"] = result.to_excel(f"Anleihen {result.year}", columns,
                                                       ["quantity", "amount", "profit"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_treasury_bills(selected_year)
st.session_state["report_result"] = report_result
prepare_exports(report_result)
display_bonds(report_result, report.get_all_stocks(selected_year))
