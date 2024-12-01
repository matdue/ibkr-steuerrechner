import streamlit as st

st.set_page_config("IBKR Steuerrechner", layout="wide")
st.title("Kontoauszüge erstellen und herunterladen")

# Do not use the whole width to display the introduction, use a smaller part to make it better readable
intro, _ = st.columns([2, 1])
intro.write("""Loggen Sie sich in der Weboberfläche von Interactive Brokers ein und laden Sie eine Flex-Query, die die 
    Kapitalflussrechnung enthält, herunter und speichern Sie sie auf ihrem eigenen Rechner ab. Wenn Sie noch keine
    passende Flex-Query erstellt haben, klappen Sie den nachfolgenden Block auf und folgen den Anweisungen.""")
with intro.expander("Flex-Query erstellen"):
    st.write("""
        1. Loggen Sie sich in der Weboberfläche von Interactive Brokers ein
        2. Wählen Sie den Menüpunkt *Performance & Berichte / Flex-Queries*""")
    st.image("resources/page/start/fq_0.png")
    st.write("""
        3. Erstellen Sie eine neue Flex-Query""")
    st.image("resources/page/start/fq_create_3.png")
    st.write("""
        4. Geben Sie der Flex-Query einen passenden Namen""")
    st.image("resources/page/start/fq_create_4.png")
    st.write("""
        5. Scrollen Sie anschließend herunter und wählen Kapitalflussrechnung (Statement of Funds) aus""")
    st.image("resources/page/start/fq_create_5.png")
    st.write("""
        6. Nun wählen Sie den Umfang aus: Zwingend notwendige Optionen sind _Basiswährungsübersicht_ und
        _Währungsaufschlüsslung_. Bei den Feldern wählen Sie der Einfachheit halber alle aus. Wenn Sie personenbezogene
        Felder ausschließen möchten, wählen Sie _Balance_, _Account ID_ und _Account Alias_ ab. Alternativ können Sie
        die Auswahl auf das absolute Minimum reduzieren, das dieses Werkzeug erfordert:
          - Currency
          - FXRateToBase
          - Asset Class
          - Symbol
          - Buy/Sell
          - Description
          - Strike
          - Expiry
          - Put/Call
          - Report Date
          - Date
          - Activity Code
          - Activity Description
          - Trade ID
          - Order ID
          - Trade Quantity
          - Trade Price
          - Trade Gross
          - Trade Commission
          - Trade Tax
          - Amount
          - Level of Detail
          - Transaction ID
          - Action ID""")
    st.image("resources/page/start/fq_create_6.png")
    st.write("""
        7. Scrollen Sie weiter herunter und stellen Sie in der Zustellkonfiguration das Format auf CSV um""")
    st.image("resources/page/start/fq_create_7.png")
    st.write("""
        8. Abschließend ist die Allgemeine Konfiguration zu prüfen und ggf. zu korrigieren""")
    st.image("resources/page/start/fq_create_8.png")
    st.write("""
        9. Geschafft! Mit einem Klick auf _Weiter_ kommen Sie zur Bestätigungsseite, die sie mit einem weiteren Klick
        auf _Erstellen_ abschließen.""")
    st.write("""Mit der soeben erstellte Flex-Query kann nun der gewünschten Kontoauszug heruntergeladen werden. Das 
        gilt für diese und alle zukünftigen Auswertungen.""")
    st.write("""Übrigens: In der IBKR Kontoverwaltung gibt es unter _Performance & Berichte_ auch den Menüpunkt
        _Kontoauszüge_, wo ebenfalls individuelle Kontoauszüge heruntergeladen werden können, u.a. auch einen mit
        der Kapitalflussrechnung. Allerdings enthält dieser weniger Details, was eine Auswertung erschwert oder unmöglich
        macht. Daher verwenden wir hier die Flex-Query.""")
    st.write("Nachfolgend ist beschrieben, wie ein Kontoauszug erstellt und heruntergeladen werden kann:")

intro.write("""
    1. Loggen Sie sich in der Weboberfläche von Interactive Brokers ein
    2. Wählen Sie den Menüpunkt *Performance & Berichte / Flex-Queries*""")
intro.image("resources/page/start/fq_0.png")
intro.write("""
    3. Führen Sie die Flex-Query mit der Kapitalflussrechnung durch einen Klick auf den Pfeil aus""")
intro.image("resources/page/start/fq_execute_1.png")
intro.write("""
    4. Stellen Sie den gewünschten Zeitraum ein. Typischerweise umfasst er ein komplettes, vergangenes Jahr, oder
    _Seit Jahresbeginn_ für das aktuelle Jahr. Ein Auszug umfasst maximal ein Jahr. Feiertage und Wochenenden können
    nicht ausgewählt werden. An diesen Tagen gibt ohnehin keine Buchungen.""")
intro.image("resources/page/start/fq_execute_2.png")
intro.write("""
    5. Manchmal startet der Download nicht, sondern es kommt ein Hinweis, dass die Erstellung in eine Warteschlange
    gestellt wurde. Warten Sie hier einen Augenblick und laden Sie anschließend die Webseite neu (F5), da die
    automatische Aktualisierung nicht immer erfolgt.""")
intro.image("resources/page/start/fq_execute_3.png")
intro.write("""
    6. Wenn die Warteschlange im Spiel war, können Sie den Kontoauszug manuell herunterladen""")
intro.image("resources/page/start/fq_execute_4.png")
intro.write("""
    7. Speichern Sie den Kontoauszug an einem sicheren Ort. Sie werden ihn im nächsten Jahr wieder benötigen, denn nur
    mit den Kontoauszügen aus allen Jahren liegt die komplette Historie vor.""")

left, right = st.columns([2, 1])
left.page_link("page/start/introduction.py", label="Zurück", icon=":material/arrow_back:")
right.page_link("page/start/upload_data.py", label="Weiter", icon=":material/arrow_forward:")
