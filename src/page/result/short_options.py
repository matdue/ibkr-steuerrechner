import streamlit as st

from depot_position import DepotPositionType
from i18n import format_currency, COLUMN_NAME_EXPORT
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe
from report import Result


@st.fragment
def export_buttons():
    result: Result = st.session_state["report_result"]
    st.download_button("Download als CSV-Datei", st.session_state["csv_export"],
                       file_name=f"short_options_{result.year}.csv",
                       mime="text/csv")
    st.download_button("Download als Excel-Datei", st.session_state["excel_export"],
                       file_name=f"short_options_{result.year}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def display_short_options(result: Result):
    st.title(f"Stillhaltergeschäfte ({result.year})")
    st.write("""Gewinne und Verluste aus Stillhaltergeschäften werden nach der FIFO-Methode berechnet und hier 
        ausgewiesen. Stillhaltergeschäfte sind sofort steuerlich relevant (vgl. §20 Abs. 1 Nr. 11 EStG). 
        Der Sonderfall Barausgleich wird nicht berücksichtigt.""")
    profitable_trades = result.total_positive("profit")
    lossy_trades = result.total_negative("profit")
    sum_trades = profitable_trades + lossy_trades
    st.write(f"Prämieneinkünfte: {format_currency(profitable_trades)}")
    st.write(f"Glattstellungen: {format_currency(abs(lossy_trades))}")
    st.write(f"Saldo: {format_currency(sum_trades)}")
    with st.expander("Kapitalflussrechnung (nur Stillhaltergeschäfte)", True):
        display_dataframe(result.df,
                          ["expiry", "date"],
                          {"profit": "EUR", "amount": "EUR"})
    export_buttons()


def prepare_exports(result: Result):
    columns = {col: COLUMN_NAME_EXPORT[col] for col in result.df.columns}
    st.session_state["csv_export"] = result.to_csv(columns)
    st.session_state["excel_export"] = result.to_excel(f"Stillhaltergeschäfte {result.year}", columns,
                                                       ["quantity", "amount", "profit"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_options(selected_year, DepotPositionType.SHORT)
st.session_state["report_result"] = report_result
prepare_exports(report_result)
display_short_options(report_result)
