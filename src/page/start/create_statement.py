import streamlit as st

from page.utils import render_footer

st.title("Kontoauszüge erstellen und herunterladen")

# Do not use the whole width to display the introduction, use a smaller part to make it better readable
intro, _ = st.columns([2, 1])
intro.write("""Loggen Sie sich in der Weboberfläche von Interactive Brokers ein und laden Sie eine Flex-Query, die  
    Kapitalflussrechnung und Trades enthält, herunter und speichern Sie diese auf ihrem eigenen Rechner ab.""")
intro.write("""Wenn Sie noch keine passende Flex-Query erstellt haben, klappen Sie den nachfolgenden Block durch einen 
    Klick auf und folgen den Anweisungen.""")
with intro.expander("Flex-Query erstellen"):
    st.write("""
        1. Loggen Sie sich in der Weboberfläche von Interactive Brokers ein
        2. Wählen Sie den Menüpunkt *Performance & Berichte / Flex-Queries*""")
    st.image("resources/page/start/fq_0.png")
    st.write("""
        3. Erstellen Sie eine neue Flex-Query""")
    st.image("resources/page/start/fq_create_03.png")
    st.write("""
        4. Geben Sie der Flex-Query einen passenden Namen""")
    st.image("resources/page/start/fq_create_04.png")
    st.write("""
        5. Scrollen Sie anschließend herunter und wählen Kapitalflussrechnung (Statement of Funds) aus""")
    st.image("resources/page/start/fq_create_05.png")
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
    st.image("resources/page/start/fq_create_06.png")
    st.write("""
        7. Nach Bestätigung durch Speichern wählen Sie Trades aus (damit erweitern Sie die Auswahl)""")
    st.image("resources/page/start/fq_create_07.png")
    st.write("""
        8. Beim Umfang genügt die Option _Ausführung_. Bei den Feldern wählen Sie ebenfalls alle aus. Wenn Sie 
        personenbezogene Felder ausschließen möchten, wählen Sie _Account ID_ und _Account Alias_ ab. Alternativ können 
        Sie die Auswahl auf das absolute Minimum reduzieren, das dieses Werkzeug erfordert:
          - Asset Class
          - Symbol
          - Trade ID
          - Open/Close Indicator
          - Buy/Sell
          - Quantity
          - Trade Date""")
    st.image("resources/page/start/fq_create_08.png")
    st.write("""
        9. Nach Bestätigung durch Speichern scrollen Sie weiter herunter und stellen Sie in der Zustellkonfiguration 
        das Format auf CSV um. Einbeziehung des Abschnittscodes und der Zeilenbeschriftung muss eingeschaltet werden""")
    st.image("resources/page/start/fq_create_09.png")
    st.write("""
        10. Abschließend ist die Allgemeine Konfiguration zu prüfen und ggf. zu korrigieren""")
    st.image("resources/page/start/fq_create_10.png")
    st.write("""
        11. Geschafft! Mit einem Klick auf _Weiter_ kommen Sie zur Bestätigungsseite, die sie mit einem weiteren Klick
        auf _Erstellen_ abschließen.""")
    st.write("""Mit der soeben erstellte Flex-Query kann nun der gewünschten Kontoauszug heruntergeladen werden. Das 
        gilt für diese und alle zukünftigen Auswertungen.""")
    st.write("""Übrigens: In der IBKR Kontoverwaltung gibt es unter _Performance & Berichte_ auch den Menüpunkt
        _Kontoauszüge_, wo ebenfalls individuelle Kontoauszüge heruntergeladen werden können, u.a. auch einen mit
        der Kapitalflussrechnung. Allerdings enthält dieser weniger Details, was eine Auswertung erschwert oder unmöglich
        macht. Daher verwenden wir hier die Flex-Query.""")
    st.write("""Die Flex-Queries enthalten sowohl die Kapitalflussrechnung als auch die Trades. Das vereinfacht die
        Handhabung, denn Sie benötigen nur eine Datei je Kalenderjahr, allerdings erschwert es die Verarbeitung mit
        anderen Programmen, z.B. Excel. Statt nur einer Flex-Query können Sie auch zwei Flex-Queries erstellen (eine
        mit der Kapitalflussrechnung und eine mit Trades). Für die Auswertung laden Sie beide Dateien hoch; dieses Tool
        benötigt nicht zwingend alle Daten in einer Datei, sie können auch auf mehrere Dateien verteilt werden.""")

intro.write("""Eine detaillierte Beschreibung zum Herunterladen können Sie im nachfolgenden Block nachlesen. Klappen 
    Sie ihn dazu mit einem Klick auf.""")
with intro.expander("Flex-Query herunterladen"):
    st.write("""
        1. Loggen Sie sich in der Weboberfläche von Interactive Brokers ein
        2. Wählen Sie den Menüpunkt *Performance & Berichte / Flex-Queries*""")
    st.image("resources/page/start/fq_0.png")
    st.write("""
        3. Führen Sie die Flex-Query mit Kapitalflussrechnung und Trades durch einen Klick auf den Pfeil aus""")
    st.image("resources/page/start/fq_execute_1.png")
    st.write("""
        4. Stellen Sie den gewünschten Zeitraum ein. Typischerweise umfasst er ein komplettes, vergangenes Jahr, oder
        _Seit Jahresbeginn_ für das aktuelle Jahr. Ein Auszug umfasst maximal ein Jahr. Feiertage und Wochenenden können
        nicht ausgewählt werden, denn an diesen Tagen gibt ohnehin keine Buchungen.""")
    st.image("resources/page/start/fq_execute_2.png")
    st.write("""
        5. Manchmal startet der Download nicht, sondern es kommt ein Hinweis, dass die Erstellung in eine Warteschlange
        gestellt wurde. Warten Sie hier einen Augenblick und laden Sie anschließend die Webseite neu (F5), da die
        automatische Aktualisierung nicht immer erfolgt.""")
    st.image("resources/page/start/fq_execute_3.png")
    st.write("""
        6. Wenn die Warteschlange im Spiel war, können Sie den Kontoauszug manuell herunterladen""")
    st.image("resources/page/start/fq_execute_4.png")
    st.write("""
        7. Speichern Sie den Kontoauszug an einem sicheren Ort. Sie werden ihn im nächsten Jahr wieder benötigen, denn nur
        mit den Kontoauszügen aus allen Jahren liegt die komplette Historie vor.""")


render_footer("page/start/introduction.py", "page/start/upload_data.py")
