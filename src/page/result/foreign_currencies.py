from dataclasses import dataclass

import pandas as pd
import streamlit as st

from i18n import format_currency
from page.utils import ensure_report_is_available, ensure_selected_year, display_dataframe


def display_foreign_currencies(buckets: dict[str, pd.DataFrame]):
    if len(buckets) == 0:
        st.write("Keine Daten für das gewählte Jahr vorhanden")
        return

    for currency, df in buckets.items():
        st.header(currency)
        currency_profits = df.query("profit >= 0")["profit"].sum()
        currency_losses = df.query("profit < 0")["profit"].sum()
        st.write(f"Gewinne: {format_currency(currency_profits)}")
        st.write(f"Verluste: {format_currency(currency_losses)}")
        st.write(f"Saldo: {format_currency(currency_profits + currency_losses)}")
        with st.expander("Berechnung"):
            display_dataframe(df, ["date"], ["profit"])


report = ensure_report_is_available()
selected_year = ensure_selected_year()

st.title(f"Fremdwährungsgewinne ({selected_year})")
st.write("""Fremdwährungsgewinne können auf zwei Arten versteuert werden, abhängig vom Kontotyp: Auf verzinslichen 
    Fremdwährungskonten werden Gewinne und Verluste wie Kapitaleinkünfte versteuert, sie gehören in die Anlage KAP. 
    Die Konten von IBKR dürften dazu zählen. Auf unverzinslichen Fremdwährungskonten oder Zahlungsverkehrskonten werden 
    Fremdwährungsgewinne dagegen mit dem persönlichen Steuersatz besteuert und gehören in die Anlage SO. Hier sind 
    nur einzelne Transaktionstypen steuerrelevant, und Fremdwährungen sind nach einem Jahr Haltezeit steuerfrei. 
    Je nach Art des Handelns kann die eine oder andere Versteuerung vorteilhafter sein.""")
st.write("""Das [BMF-Schreiben vom 19. Mai 2022](https://esth.bundesfinanzministerium.de/esth/2022/C-Anhaenge/Anhang-19/II/inhalt.html) 
    beschreibt in Randziffer 131, wie die Finanzämter die Regeln anwenden sollen. Hier sind die drei Kontotypen 
    genannt. Es ist davon auszugehen, dass das Schreiben ab 2025 angewendet wird.""")
st.write("""Fremdwährungsgewinne können alternativ dem Forexbericht entnommen werden, der allerdings nicht an die 
    deutsche Gesetzgebung angepasst ist und zu hoch oder zu niedrig ausfallen kann.""")

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
    st.write("""Bei verzinslichen Fremdwährungskonten wird jede Transaktion betrachtet, jede einzelne ist
        ergebnisrelevant.""")
    st.write("""Bei den anderen Kontotypen unterscheidet das Gesetz dagegen zwischen echten und unechten 
        Anschaffungen bzw. Veräußerungen.
        Ein Anschaffungsvorgang löst eine echte Anschaffung aus, z.B. der Verkauf einer Aktie, und ein
        Veräußerungsvorgang löst eine echte Veräußerung aus, z.B. dem Kauf einer Aktie. Alle anderen Vorgänge sind
        unechte Anschaffungen bzw. Veräußerungen, z.B. der Empfang einer Dividende. Nur echte Anschaffungen und 
        Veräußerungen sind ergebnisrelevant.""")
    st.write("""In der folgenden Tabelle stellt jeder Block ein Abgang von Fremdwährung dar, der sich aus einem
        oder mehreren Zugängen in der gleichen Fremdwährung finanziert. Die Zugänge haben immer positive Beträge,
        die Abgänge immer negative. Aus der Summe ergibt sich das Ergebnis. Zugangstransaktionen werden ggf. 
        aufgeteilt, damit sie zu einem Abgang passen. Ein Zugang kann daher mehrfach aufgeführt sein, wenn nur ein 
        Teil des Betrages verwendet wird.""")
    st.write("""Transaktionen, die nicht als ergebnisrelevant markiert sind, sind neutral, sie haben keinen Einfluss
        auf das Ergebnis (sie gehören zu den unechten Anschaffungen oder Veräußerungen, s.o.). Dazu wird der 
        Devisenkurs des Abgangs auf den Zugang angewendet. Durch Rundungsfehler können Blöcke, die nur aus 
        nicht-ergebnisrelevanten Transaktionen bestehen (und damit neutral sind), trotzdem ein positives oder 
        negatives Ergebnis haben. Der Betrag dürfte im Cent-Bereich liegen und sich über die Blöcke mehr oder 
        weniger ausgleichen.""")


@dataclass
class AccountType:
    code: int
    title: str
    caption: str


account_options = [
    AccountType(1, "Verzinsliches Fremdwährungskonto", "Kapitalerträge, vgl. §20 Abs. 2 S. 1 Nr. 7 EStG"),
    AccountType(2, "Unverzinsliches Fremdwährungskonto", "Private Veräußerungsgeschäfte, vgl. §23 Abs. 1 Nr. 2 EStG"),
    AccountType(3, "Zahlungsverkehrskonto", "Private Veräußerungsgeschäfte, vgl. §23 Abs. 1 Nr. 2 EStG")
]
account_type: AccountType = st.radio(
    "Welcher Kontotyp soll für die Gewinnermittlung angenommen werden?",
    account_options,
    format_func=lambda acc_type: acc_type.title,
    captions=[acc_type.caption for acc_type in account_options],
    key="account_type"
)
interest_bearing_account = account_type.code == account_options[0].code

display_foreign_currencies(report.get_foreign_currencies2(selected_year, interest_bearing_account))
