import pandas as pd
import streamlit as st

from depot_position import DepotPositionType
from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_short_stocks(result: Result, df_all: pd.DataFrame):
    st.title(f"Aktienleerverkäufe ({result.year})")
    st.write("""Gewinne und Verluste aus Aktienleerverkäufen sowie Aktienandienungen und -ausbuchungen (in der 
        Reihenfolge Ausbuchung mit anschließender Andienung) werden nach der FIFO-Methode berechnet und hier 
        ausgewiesen.""")
    st.write("""An dieser Stelle werden auch ETFs aufgelistet, obwohl sie keine Aktien sind, sondern Sammelanlagen.
        Allerdings haben Sammelanlagen einen anderen Verlusttopf. Eine manuelle Aufteilung ist ggf. notwendig.""")
    profitable_trades = result.total_positive("profit")
    lossy_trades = result.total_negative("profit")
    sum_trades = profitable_trades + lossy_trades
    st.write(f"Gewinne aus Aktienleerverkäufen: {format_currency(profitable_trades)}")
    st.write(f"Verluste aus Aktienleerverkäufen: {format_currency(abs(lossy_trades))}")
    st.write(f"Saldo: {format_currency(sum_trades)}")
    with st.expander(f"Kapitalflussrechnung (nur abgeschlossene Aktienleerverkäufe)", True):
        display_dataframe(result.df,
                          ["date"],
                          {"amount": "EUR", "profit": "EUR"})
    with st.expander("Kapitalflussrechnung (nur Aktiengeschäfte)"):
        display_dataframe(df_all,
                          ["date"],
                          {"amount": "EUR"})
    display_export_buttons(result, f"short_stocks_{result.year}", f"Aktienleerverkäufe {result.year}",
                           ["quantity", "amount", "profit"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_stocks(selected_year, DepotPositionType.SHORT)
display_short_stocks(report_result, report.get_all_stocks(selected_year))
