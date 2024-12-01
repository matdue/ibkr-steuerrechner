import io
from datetime import date

import pandas as pd
import streamlit as st

from ibkr_steuerrechner.flex_query import read_report, DataError, REQUIRED_COLUMNS
from ibkr_steuerrechner.report import Report


def create_report(data_files: list):
    data_dfs = [read_report(data_file.name, io.TextIOWrapper(data_file, "utf-8")) for data_file in data_files]

    # Skip empty reports
    data_dfs = [data_df for data_df in data_dfs if not data_df.empty]

    # Ensure chronological order of reports and keep order within each report as is
    data_dfs.sort(key=lambda data_df: data_df["ReportDate"].iloc[0])

    if len(data_dfs) != 0:
        # German law requires FIFO, i.e. we have to process line by line
        report = Report()
        pd.concat(data_dfs).apply(lambda row: report.process(row), axis=1)
        report.finish(date.today())
        return report


st.set_page_config("IBKR Steuerrechner", layout="wide")
st.title("Daten hochladen")

# Do not use the whole width to display the introduction, use a smaller part to make it better readable
intro, _ = st.columns([2, 1])
intro.write("### Kontoauszug zur Auswertung übertragen")
intro.write("""Für die Auswertung können Sie mehrere Dateien hochladen und anschließend das Auswertungsjahr 
    auswählen. Auf diese Weise kann die Historie der vergangenen Jahre berücksichtigt werden, z.B. für Positionen,
    die über den Jahreswechsel gehaltenen werden.""")
intro.write("""Alle hochgeladenen Daten werden auf einem Server in den USA verarbeitet. Sie werden nur im 
    Hauptspeicher des Servers abgelegt, sie werden weder dauerhaft noch zeitweise gespeichert. Sobald Sie das 
    Browserfenster schließen, werden die Daten aus dem Speicher entfernt.""")

try:
    data_files = intro.file_uploader("Kapitalflussrechnung (CSV-Format)", type="csv", accept_multiple_files=True)
    report = create_report(data_files)
    st.session_state["report"] = report
except DataError as error:
    intro.error(f"""Datei {error} scheint keine CSV-Datei mit der Kapitalflussrechnung aus der Flex-Query zu sein.
    Es wird eine CSV-Datei mit mindestens diesen Spalten erwartet: {", ".join(sorted(REQUIRED_COLUMNS))}""")


left, right = st.columns([2, 1])
left.page_link("page/start/create_statement.py", label="Zurück", icon=":material/arrow_back:")
if st.session_state.get("report", None) is not None:
    right.page_link("page/start/tax_report_dates.py", label="Weiter", icon=":material/arrow_forward:")
