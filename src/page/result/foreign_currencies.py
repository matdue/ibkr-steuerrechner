import pandas as pd
import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_foreign_currencies(buckets: dict[str, pd.DataFrame]):
    st.header("Fremdwährungsgewinne")
    st.write("""Fremdwährungsgewinne gehören in die Anlage KAP (und nicht in SO), da die Fremdwährungskonten bei IBKR
        verzinst sind. Sie gehören zu den ausländischen Kapitalerträgen.""")
    st.write("""Alternativ können sie dem Forexbericht entnommen werden, der allerdings nicht an die deutsche
        Gesetzgebung angepasst ist und zu hoch oder zu niedrig ausfallen kann.""")

    with st.expander(f"Erläuterungen"):
        st.write("""Eine Transaktion in Fremdwährung setzt sich, steuerlich betrachtet, aus zwei Transaktionen
            zusammen: Einer Transaktion, die EUR von/nach der Fremdwährung tauscht, und der Transaktion, die das 
            Geschäft darstellt. Zum Beispiel setzt sich der Kauf einer Aktie in USD zusammen aus dem Tausch von USD
            in EUR und dem Kauf der Aktie mit diesen Mitteln. Zum besseren Verständnis kann man sich den USD-Topf als
            ein eigenständiges Wirtschaftsgut vorstellen. Die USD haben einen Wert in EUR, und die Aktie hat einen Wert
            in EUR. Das ist die Währung, in der das Finanzamt rechnet.""")
        st.write("""Fremdwährungsgewinne oder -verluste entstehen, wenn zum Zeitpunkt der Entnahme der Wert der USD
            gestiegen bzw. gefallen sind. Der Wert der USD (in EUR) bei Entnahme wird mit dem Wert der USD bei Zufuhr
            verglichen. Es wird das FIFO-Prinzip angewendet, d.h. zuerst erworbene Fremdwährungsbeträge werden zuerst
            wieder veräußert.""")
        st.write("""Das Gesetz unterscheidet zwischen echten und unechten Anschaffungen bzw. Veräußerungen.
            Ein Anschaffungsvorgang löst eine echte Anschaffung aus, z.B. der Verkauf einer Aktie, und ein
            Veräußerungsvorgang löst eine echte Veräußerung aus, z.B. dem Kauf einer Aktie. Alle anderen Vorgänge sind
            unechte Anschaffungen bzw. Veräußerungen, z.B. der Empfang einer Dividende. Für die Ermittlung von
            Fremdwährungsgewinnen werden nur echte Anschaffungen und Veräußerungen betrachtet.""")
        st.write("""In der folgenden Tabelle stellt jeder Block ein Abgang von Fremdwährung dar, der sich aus einem
            oder mehreren Zugängen in der gleichen Fremdwährung finanziert. Abgänge und Zugänge, die zu einer echten
            Anschaffung oder Veräußerung gehören, sind steuerpflichtig, während die unechten nicht ergebnisrelevant 
            sind. Der Abgang ist immer negativ, die Zugänge positiv. Die Summe ergibt den Fremdwährungsgewinn 
            bzw. -verlust.""")
        st.write("""Zugangstransaktionen werden ggf. aufgeteilt, damit sie zu einem Abgang passen. Wird z.B. ein Abgang
            von 100 USD durch einen Zugang von 300 USD finanziert, wird das wie folgt in den einzelnen Spalten
            dargestellt:""")
        st.write("""- USD (gesamt): 300 (_Transaktion, die diesen Block finanziert, stammt z.B. aus einem Währungstausch 
            in der Vergangenheit, in dem EUR in 300 USD getauscht wurden_)""")
        st.write("""- USD (verbraucht): 100 (_die übrigen 200 USD werden hier nicht dargestellt und werden in einem 
            späteren Block verbraucht)_)""")
        st.write("""- USD (ergebnisrelevant): entspricht 'USD (verbraucht)', wenn die Position zu einer echten 
            Veräußerung/Anschaffung gehört, oder 0 bei unechten Veräußerungen/Anschaffungen""")
        st.write("""- EUR (ergebnisrelevant): entspricht 'USD (ergebnisrelevant)' in EUR, umgerechnet mit dem 
            angegebenen Devisenkurs""")

    if len(buckets) == 0:
        st.write("Keine Daten für das gewählte Jahr vorhanden")
        return

    for currency, df in buckets.items():
        st.subheader(currency)
        currency_profits = df.query("profit >= 0")["profit"].sum()
        currency_losses = df.query("profit < 0")["profit"].sum()
        st.write(f"Gewinne: {format_currency(currency_profits)}")
        st.write(f"Verluste: {format_currency(currency_losses)}")
        st.write(f"Saldo: {format_currency(currency_profits + currency_losses)}")
        with st.expander("Berechnung"):
            display_dataframe(df, ["date"], ["profit"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()
display_foreign_currencies(report.get_foreign_currencies(selected_year))
