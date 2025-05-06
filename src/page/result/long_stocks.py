import pandas as pd
import streamlit as st

from depot_position import DepotPositionType
from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe, display_export_buttons
from report import Result


def display_long_stocks(result: Result, df_all: pd.DataFrame):
    st.title(f"Aktiengeschäfte ({result.year})")
    st.write("""Gewinne und Verluste aus Aktienkäufen, -verkäufen, -andienungen und -ausbuchungen werden nach der
        FIFO-Methode berechnet und hier ausgewiesen. Käufe und Andienungen werden steuerlich erst dann relevant, wenn die
        Position durch Verkauf oder Ausbuchung geschlossen wird. Erfolgt die Schließung im Folgejahr, wird erst dann ein
        Gewinn oder Verlust berechnet.""")
    st.write("""An dieser Stelle werden auch ETFs aufgelistet, obwohl sie keine Aktien sind, sondern Sammelanlagen.
        Allerdings haben Sammelanlagen einen anderen Verlusttopf. Eine manuelle Aufteilung ist ggf. notwendig.""")
    profitable_trades = result.total_positive("profit")
    lossy_trades = result.total_negative("profit")
    sum_trades = profitable_trades + lossy_trades
    st.write(f"Gewinne aus Aktienveräußerungen: {format_currency(profitable_trades)}")
    st.write(f"Verluste aus Aktienveräußerungen: {format_currency(abs(lossy_trades))}")
    st.write(f"Saldo: {format_currency(sum_trades)}")
    if abs(lossy_trades) > profitable_trades:
        st.write(f"""Die Verluste aus Aktienveräußerungen übersteigen die Gewinne. Das Finanzamt wird die übersteigenden
            Verluste in Höhe von {format_currency(abs(sum_trades))} ins nächste Jahr vortragen. Sie können nicht mit
            Gewinnen aus anderen Kapitalgeschäften verrechnet werden.""")
    with st.expander(f"Kapitalflussrechnung (nur abgeschlossene Aktiengeschäfte)", True):
        display_dataframe(result.df,
                          ["date"],
                          {"amount": "EUR", "profit": "EUR"})
    with st.expander("Kapitalflussrechnung (nur Aktiengeschäfte)"):
        display_dataframe(df_all,
                          ["date"],
                          {"amount": "EUR"})
    display_export_buttons(result, f"long_stocks_{result.year}", f"Aktiengeschäfte {result.year}",
                           ["quantity", "amount", "profit"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
report_result = report.get_stocks(selected_year, DepotPositionType.LONG)
display_long_stocks(report_result, report.get_all_stocks(selected_year))
