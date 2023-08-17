import io
import locale
from typing import Optional

import pandas as pd
import streamlit as st

from iterable_text_io import IterableTextIO


def categorize_statement_record(record: pd.Series) -> tuple[str, Optional[str]]:
    if record["Description"] in ["Opening Balance", "Closing Balance"]:
        return "balance", None

    if record["Description"] == "Electronic Fund Transfer":
        return "transfer", None

    if "Cash Dividend" in record["Description"]:
        if record["Description"].endswith(" (Ordinary Dividend)"):
            return "dividend", "ordinary"
        if record["Description"].endswith(" Tax"):
            return "dividend", "tax"
        return "dividend", "other"

    return "other", None


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
    statement_of_funds_lines = (line for line in file if line.startswith("Statement of Funds,"))
    with IterableTextIO(statement_of_funds_lines) as s:
        df = pd.read_csv(s, parse_dates=["Report Date", "Activity Date"])
    df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")
    df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")
    df["Sum"] = df[["Debit", "Credit"]].sum(axis=1)
    df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")
    df["Report_Year"] = df["Report Date"].dt.year.astype("str")
    df["Activity_Year"] = df["Activity Date"].apply(lambda d: None if pd.isnull(d) else str(d.year))

    # Skip all records which are not in base currency
    df = df.query("Currency == 'Base Currency Summary'").drop(columns=["Statement of Funds", "Header", "Currency"])

    return df


def display_fund_transfer(df_year: pd.DataFrame):
    st.header("Ein- und Auszahlungen")
    df_transfer = df_year.query("Category == 'transfer'")
    deposited_funds = df_transfer["Credit"].sum()
    withdrawn_funds = df_transfer["Debit"].sum()
    st.write(f"Einzahlungen: {locale.currency(deposited_funds, grouping=True)}")
    st.write(f"Auszahlungen: {locale.currency(withdrawn_funds, grouping=True)}")
    with st.expander("Auszug"):
        st.dataframe(df_transfer)


def display_dividends(df_year: pd.DataFrame, df_year_corrections: pd.DataFrame, selected_year: str):
    st.header("Dividenden")
    df_dividend = df_year.query("Category == 'dividend'")
    df_dividend_corrections = df_year_corrections.query("Category == 'dividend'")
    ordinary_dividends = df_dividend.query("Subcategory == 'ordinary'")
    ordinary_dividends_corrections = df_dividend_corrections.query("Subcategory == 'ordinary'")
    earned_dividends = ordinary_dividends["Sum"].sum()
    earned_dividends_corrections = ordinary_dividends_corrections["Sum"].sum()

    taxes = df_dividend.query("Subcategory == 'tax'")
    taxes_corrections = df_dividend_corrections.query("Subcategory == 'tax'")
    withheld_taxes = taxes["Sum"].sum()
    withheld_taxes_corrections = taxes_corrections["Sum"].sum()

    others = df_dividend.query("Subcategory == 'other'")
    others_corrections = df_dividend_corrections.query("Subcategory == 'other'")
    other_dividends = others["Sum"].sum()
    other_dividends_corrections = others_corrections["Sum"].sum()

    st.subheader("Gewöhnliche Dividenden")
    if earned_dividends_corrections:
        st.write(f"Summe {selected_year}: {locale.currency(earned_dividends, grouping=True)}")
        st.write(f"Korrektur: {locale.currency(earned_dividends_corrections, grouping=True)}")
    st.write(f"Summe: {locale.currency(earned_dividends+earned_dividends_corrections, grouping=True)}")

    st.subheader("Quellensteuer")
    if withheld_taxes_corrections:
        st.write(f"Summe {selected_year}: {locale.currency(withheld_taxes * (-1), grouping=True)}")
        st.write(f"Korrektur: {locale.currency(withheld_taxes_corrections * (-1), grouping=True)}")
    st.write(f"Summe: {locale.currency((withheld_taxes+withheld_taxes_corrections) * (-1), grouping=True)}")

    if other_dividends or other_dividends_corrections:
        st.subheader("Andere Zahlungen")
        st.write(f"Summe {selected_year}: {locale.currency(other_dividends, grouping=True)}")
        st.write(f"Korrektur: {locale.currency(other_dividends_corrections, grouping=True)}")
        st.write(f"Summe: {locale.currency(other_dividends+other_dividends_corrections, grouping=True)}")

    with st.expander("Auszug"):
        st.dataframe(pd.concat([df_dividend, df_dividend_corrections]))


def main():
    locale.setlocale(locale.LC_ALL, "de_DE.utf8")

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

    st.header(f"Ergebnis für das Jahr {selected_year}")
    df[["Category", "Subcategory"]] = df.apply(categorize_statement_record, axis=1, result_type="expand")
    df_year = df.query("Report_Year == @selected_year and Activity_Year == @selected_year")
    df_year_corrections = df.query("Report_Year > @selected_year and Activity_Year == @selected_year")
    with st.expander("Kompletter Kontoauszug"):
        st.dataframe(df)

    display_fund_transfer(df_year)
    display_dividends(df_year, df_year_corrections, selected_year)


if __name__ == "__main__":
    main()
