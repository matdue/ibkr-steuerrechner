import pandas as pd
import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_bonds(year: int, df: pd.DataFrame, df_all: pd.DataFrame):
    st.title(f"Anleihen ({year})")
    st.write("""Gewinne und Verluste aus Käufen, Verkäufen und Ausbuchungen von Anleihen werden nach der
        FIFO-Methode berechnet und hier ausgewiesen. Käufe werden steuerlich erst dann relevant, wenn die
        Position durch Verkauf oder Ausbuchung geschlossen wird. Erfolgt die Schließung im Folgejahr, wird erst dann ein
        Gewinn oder Verlust berechnet.""")
    profitable_trades = df.query("profit >= 0")["profit"].sum()
    lossy_trades = df.query("profit < 0")["profit"].sum()
    sum_trades = profitable_trades + lossy_trades
    st.write(f"Gewinne aus Anleihenveräußerungen: {format_currency(profitable_trades)}")
    st.write(f"Verluste aus Anleihenveräußerungen: {format_currency(abs(lossy_trades))}")
    st.write(f"Saldo: {format_currency(sum_trades)}")
    with st.expander(f"Kapitalflussrechnung (nur abgeschlossene Anleihengeschäfte)", True):
        display_dataframe(df,
                          ["date"],
                          ["amount", "profit"])
    with st.expander("Kapitalflussrechnung (nur Anleihengeschäfte)"):
        display_dataframe(df_all,
                          ["date"],
                          ["amount"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_bonds(selected_year, report.get_treasury_bills(selected_year), report.get_all_treasury_bills(selected_year))
