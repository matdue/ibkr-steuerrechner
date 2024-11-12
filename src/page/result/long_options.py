import pandas as pd
import streamlit as st

from i18n import format_currency
from options import OptionType
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_termingeschaefte(df: pd.DataFrame):
    st.header("Termingeschäfte")
    st.write("""Gewinne und Verluste aus Termingeschäften werden nach der FIFO-Methode berechnet und hier ausgewiesen.
        Termingeschäfte werden erst mit Schließung der Position steuerlich relevant.
        Der Sonderfall Barausgleich wird nicht berücksichtigt.""")
    st.write("""Verluste aus Termingeschäfte können bei Privatpersonen nur beschränkt mit Gewinnen aus
        Stillhaltergeschäften ausgeglichen werden. Alles über 20.000 € wird ins Folgejahr vorgetragen.""")
    profitable_trades = df.query("profit >= 0")["profit"].sum()
    lossy_trades = df.query("profit < 0")["profit"].sum()
    sum_trades = profitable_trades + lossy_trades
    st.write(f"Prämieneinkünfte: {format_currency(profitable_trades)}")
    st.write(f"Glattstellungen: {format_currency(abs(lossy_trades))}")
    st.write(f"Saldo: {format_currency(sum_trades)}")
    with st.expander("Kapitalflussrechnung (nur Termingeschäfte)", True):
        display_dataframe(df,
                          ["expiry", "date"],
                          ["profit", "amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_termingeschaefte(report.get_options(selected_year, OptionType.TERMINGESCHAEFT, {}))
