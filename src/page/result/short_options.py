import streamlit as st

from depot_position import DepotPositionType
from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


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
    display_export_buttons(result, f"short_options_{result.year}", f"Stillhaltergeschäfte {result.year}",
                           ["quantity", "amount", "profit"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_options(selected_year, DepotPositionType.SHORT)
display_short_options(report_result)
