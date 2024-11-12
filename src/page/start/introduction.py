import streamlit as st

st.set_page_config("IBKR Steuerrechner", layout="wide")
st.title("Steuerrechner für Interactive Brokers")

# Do not use the whole width to display the introduction, use a smaller part to make it better readable
intro, _ = st.columns([2, 1])
intro.write("""Dieses Werkzeug wertet die Kontoauszüge von Interactive Brokers aus und berechnet die Gewinne und
    Verluste für einzelne Arten von Kapitalgeschäften. Diese bilden die Grundlage für die eigene Steuererklärung.
    Das deutsche Einkommensteuergesetz (EStG) definiert für diese Arten teilweise unterschiedliche Regeln, wie diese 
    steuerlich betrachtet werden und wie sie untereinander verrechnet werden dürfen. Finanztransaktionen können sogar 
    in zweierlei Hinsicht steuerlich relevant werden, z.B. löst der Kauf oder Verkauf von Aktien in einer Fremdwährung 
    ein Aktiengeschäft und ein Fremdwährungsgeschäft aus.""")
intro.write("""Im Ergebnis werden nur Gewinne und Verlust ausgewiesen, und es wird dargestellt, wie sie berechnet
    wurden. Es erfolgt _keine_ Anleitung, in welche Zeile der Steuererklärung welche Zahl eingetragen werden soll.""")
intro.write("""Diese Auswertung ersetzt keine Steuerberatung! Alle Angaben sind ohne Gewähr und dienen nur der 
    Inspiration.""")

intro.write("### Umfang")
intro.write("""
    Diese Kapitalgeschäfte werden ausgewertet:
    - Ein- und Auszahlungen
    - Aktien-Trades (nur long)
    - Anleihen-Trades (nur T-Bills)
    - Dividenausschüttungen
    - Zinseinnahmen und -ausgaben
    - Optionen (Stillhalter- und Termingeschäfte)
    - Fremdwährungsgeschäfte""")

intro.write("### Bemerkungen")
intro.write("""Alle Daten werden auf einem Server in den USA verarbeitet. Sie werden nur im 
    Hauptspeicher des Servers abgelegt und weder dauerhaft noch zeitweise gespeichert.""")
intro.write("""Dieses Werkzeug ist Open Source, der Programmcode ist auf 
    [GitHub](https://github.com/matdue/ibkr-steuerrechner) zu finden.""")

_, right = st.columns([2, 1])
right.page_link("page/start/create_statement.py", label="Weiter", icon=":material/arrow_forward:")
