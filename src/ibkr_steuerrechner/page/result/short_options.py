import pandas as pd
import streamlit as st

from ibkr_steuerrechner.i18n import format_currency
from ibkr_steuerrechner.options import OptionType
from ibkr_steuerrechner.page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_stillhalter(df: pd.DataFrame):
    st.header("Stillhaltergeschäfte")
    st.write("""Gewinne und Verluste aus Stillhaltergeschäften werden nach der FIFO-Methode berechnet und hier 
        ausgewiesen. Stillhaltergeschäfte sind sofort steuerlich relevant, da der Zufluss von Kapital sofort erfolgt. 
        Der Sonderfall Barausgleich wird nicht berücksichtigt.""")
    profitable_trades = df.query("profit >= 0")["profit"].sum()
    lossy_trades = df.query("profit < 0")["profit"].sum()
    sum_trades = profitable_trades + lossy_trades
    st.write(f"Prämieneinkünfte: {format_currency(profitable_trades)}")
    st.write(f"Glattstellungen: {format_currency(abs(lossy_trades))}")
    st.write(f"Saldo: {format_currency(sum_trades)}")
    with st.expander("Kapitalflussrechnung (nur Stillhaltergeschäfte)", True):
        display_dataframe(df,
                          ["expiry", "date"],
                          ["profit", "amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
cut_off_dates = {int(year): date
                 for year, date in st.session_state.get("cut_off_dates", {}).items()}
display_stillhalter(report.get_options(selected_year, OptionType.STILLHALTERGESCHAEFT, cut_off_dates))
