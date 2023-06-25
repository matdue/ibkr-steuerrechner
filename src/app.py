import io
import locale

import pandas as pd
import streamlit as st


def categorize_statement_record(record: pd.Series):
    if record["Description"] in ["Opening Balance", "Closing Balance"]:
        return "balance"

    if record["Description"] == "Electronic Fund Transfer":
        return "transfer"

    if "Cash Dividend" in record["Description"]:
        return "dividend"

    return "other"

def read_statement_file(file: io.TextIOBase):
    """
    Reads and parses the input field and returns a dataframe with the following columns:

    Report Date: Date of record
    Activity Date: Date of activity
    Description: Type of activity in human-readable text
    Debit: Debit amount of activity (negative or none)
    Credit: Credit amount of activity (positive or none)
    Balance: Balance after activity
    Year: Year of report date (duplicated for convenience)

    :param file: Input file
    :return: Pandas Dataframe
    """
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
    df["Report_Year"] = df["Report Date"].dt.year.astype("str")
    df["Activity_Year"] = df["Activity Date"].dt.year.astype("str")

    # Skip all records which are not in base currency
    df = df.query("Currency == 'Base Currency Summary'").drop(columns=["Statement of Funds", "Header", "Currency"])

    return df


def main():
    # TODO: Im Dockerfile: RUN locale-gen en_US.UTF-8
    try:
        locale.setlocale(locale.LC_ALL, "de_DE.utf8")
    except locale.Error:
        st.write("locale de_DE.utf8 unavailable")
        try:
            locale.setlocale(locale.LC_ALL, "de_DE")
        except locale.Error:
            st.write("locale de_DE unavailable")

    st.title("Steuerrechner für Interactive Brokers")
    st.caption("Zur Berechnung der Steuerschuld von Optionen und Aktiengeschäften")

    # Statement of Funds (Kapitalflussrechnung)
    # TODO: Erklärung ergänzen, wo und wie man das herunterlädt
    st.write("Laden Sie zunächst die Kapitalflussrechnung (WO?) herunter und speichern Sie sie ab. Anschließend laden Sie sie zur Auswertung hier hoch. Sie können mehrere Dateien auswählen, damit die Historie aus den vergangenenen Jahren berücksichtigt werden kann.")
    sof_files = st.file_uploader("Kapitalflussrechnung (CSV-Format)", type="csv", accept_multiple_files=True)
    sof_dfs = [read_statement_file(io.TextIOWrapper(sof_file, "utf-8"))
               for sof_file in sof_files]
    if len(sof_dfs) == 0:
        return

    df = pd.concat(sof_dfs).sort_values(["Report Date"])
    years = df["Report_Year"].unique()
    years_options = ["Bitte wählen"] + list(years)[::-1]
    selected_year = st.selectbox("Für welches Kalenderjahr sollen die Steuern berechnet werden?", years_options)
    if selected_year == years_options[0]:
        return

    st.write(f"Berechnung läuft für das Jahr {selected_year}...")
    df["Category"] = df.apply(categorize_statement_record, axis=1).astype("category")
    df_year = df.query("Report_Year == @selected_year")
    st.dataframe(df_year)

    st.header("Ein- und Auszahlungen")
    df_transfer = df_year.query("Category == 'transfer'")
    deposited_funds = df_transfer.filter(["Credit"]).sum()[0]
    withdrawn_funds = df_transfer.filter(["Debit"]).sum()[0]
    st.write(f"Einzahlungen: {locale.currency(deposited_funds, grouping=True)}")
    st.write(f"Auszahlungen: {locale.currency(withdrawn_funds, grouping=True)}")
    st.dataframe(df_transfer)

    st.header("Dividenden")
    # FIXME: Was ist mit Steuerkorrekturen aus dem letzten Jahr?
    df_dividend = df_year.query("Category == 'dividend'")
    earned_dividends = df_dividend.filter(["Credit"]).sum()[0]
    withheld_taxes = abs(df_dividend.filter(["Debit"]).sum()[0])
    st.write(f"Dividendenzahlungen: {locale.currency(earned_dividends, grouping=True)}")
    st.write(f"Quellensteuer: {locale.currency(withheld_taxes, grouping=True)}")
    st.dataframe(df_dividend)


if __name__ == "__main__":
    main()
