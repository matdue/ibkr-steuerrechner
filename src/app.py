import io

import pandas as pd
import streamlit as st

def read_statement_file(file: io.TextIOBase):
    # Load relevant lines only
    # A CSV may contain more than one report, but we are interested in Statement of Funds only
    # TODO: Auch deutsche Reports unterstützen
    statement_of_funds_lines = io.StringIO()
    statement_of_funds_lines.writelines(line for line in file if line.startswith("Statement of Funds,"))
    statement_of_funds_lines.seek(0)
    df = pd.read_csv(statement_of_funds_lines, parse_dates=["Report Date", "Activity Date"])
    df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")
    df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")
    df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")
    df["Year"] = df["Report Date"].dt.year
    return df


def main():
    st.title("Steuerrechner für Interactive Brokers")
    st.caption("Zur Berechnung der Steuerschuld von Optionen und Aktiengeschäften")

    # Statement of Funds (Kapitalflussrechnung)
    st.write("Laden Sie zunächst die Kapitalflussrechnung (WO?) herunter und speichern Sie sie ab. Anschließend laden Sie sie zur Auswertung hier hoch. Sie können mehrere Dateien auswählen, damit die Historie aus den vergangenenen Jahren berücksichtigt werden kann.")
    sof_files = st.file_uploader("Kapitalflussrechnung (CSV-Format)", type="csv", accept_multiple_files=True)
    sof_dfs = [read_statement_file(io.TextIOWrapper(sof_file, "utf-8"))
               for sof_file in sof_files]
    if len(sof_dfs) == 0:
        return

    df = pd.concat(sof_dfs).sort_values(["Report Date"])
    years = df["Year"].unique()
    years_options = ["Bitte wählen"] + list(map(str, years))[::-1]
    selected_year = st.selectbox("Für welches Kalenderjahr sollen die Steuern berechnet werden?", years_options)
    st.write(f"Gewählt: {selected_year}")


if __name__ == "__main__":
    main()
