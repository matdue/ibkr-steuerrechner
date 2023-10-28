# IBKR Steuerrechner
Zur Berechnung der Steuerschuld von Optionen- und Aktiengeschäften

Mit diesem Programm kann der Kontoauszug, d.h. die Kapitalflussrechnung, von Interactive Brokers ausgewertet werden. Die folgenden Einträge werden erkannt und aufsummiert oder detaillierter analysiert:
- Dividenden
- Zinsen
- Aktiengeschäfte
- Optionsgeschäfte (inkl. Aufteilung in die einzelnen Trades)
- Ein- und Auszahlungen
- Währungstausch
- Marktdatenabonnements

## Anwendung

Dieses Programm steht online zur Verfügung: https://ibkr-steuerrechner.streamlit.app/

Das Hosting erfolgt in der [Streamlit Community Cloud](https://streamlit.io/cloud). Falls das Programm nicht aktiv ist, starten Sie es über den Button, der in diesem Fall dargestellt wird.

Alternativ können Sie das Programm auf ihren eigenen Rechner herunterladen und dort starten. Grundkenntnisse in Python sind erforderlich, alle Abhängigkeiten sind in `requirements.txt` aufgelistet. Der Start erfolgt über `streamlit run src/app.py`

## Weiterentwicklung

Dieses Programm ist Open Source. Sie sind eingeladen, selbst Änderungen vorzunehmen oder Erweiterungen zu programmieren und sie anschließend per Pull-Request bereitzustellen.

Lokal können die Unit Tests mit `PYTHONPATH=$PWD/src python -m unittest` ausgeführt werden.
