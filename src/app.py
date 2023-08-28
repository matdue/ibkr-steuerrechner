import io
import locale
import re
from dataclasses import dataclass, asdict
from typing import Optional

import pandas as pd
import streamlit as st

from iterable_text_io import IterableTextIO
from utils import calc_share_trade_profits

RECORD_INTEREST = re.compile(r"Credit|Debit Interest")
RECORD_OPTION = re.compile(r"(Buy|Sell) (-?[0-9]+) (.{1,5} [0-9]{2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[0-9]{2} [0-9]+(\.[0-9]+)? ([PC])) (\(\w+\))?")
RECORD_SHARES = re.compile(r"(Buy|Sell) (-?[0-9]+) (.*?)( \(\w+\))?$")


def categorize_statement_record(record: pd.Series) -> tuple[str, Optional[str]]:
    description = record["Description"]
    if description in ["Opening Balance", "Closing Balance"]:
        return "balance", None

    if description == "Electronic Fund Transfer":
        return "transfer", None

    if "Cash Dividend" in description:
        if description.endswith(" (Ordinary Dividend)"):
            return "dividend", "ordinary"
        if description.endswith(" Tax"):
            return "dividend", "tax"
        return "dividend", "other"

    if RECORD_INTEREST.search(description):
        return "interest", None
    if RECORD_OPTION.match(description):
        return "option", None
    if RECORD_SHARES.match(description):
        return "shares", None

    return "other", None


@dataclass
class OptionShare:
    is_option: bool
    action: str
    count: int
    underlying: str


def parse_option_share_record(record: pd.Series) -> dict:
    description = record["Description"]
    match = RECORD_OPTION.match(description)
    if match is not None:
        # Cleansing: Remove ending .0 from strike price as some options have this precision specification and some not
        underlying = re.sub(r"(.*?)(\.0)( [CP])", r"\1\3", match.group(3))
        return asdict(OptionShare(True, match.group(1), int(match.group(2)), underlying))
        #return {"Action": match.group(1), "Count": int(match.group(2)), "Underlying": underlying, "Option": True}

    match = RECORD_SHARES.match(description)
    if match is not None:
        return asdict(OptionShare(False, match.group(1), int(match.group(2)), match.group(3)))
        #return {"Action": match.group(1), "Count": int(match.group(2)), "Underlying": match.group(3), "Option": False}

    #return {"Action": None, "Count": None, "Underlying": None, "Option": False}



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


def display_interests(df_year: pd.DataFrame):
    st.header("Zinsen")
    df_interests = df_year.query("Category == 'interest'")
    earned_interests = df_interests["Credit"].sum()
    payed_interests = abs(df_interests["Debit"].sum())
    st.write(f"Einnahmen: {locale.currency(earned_interests, grouping=True)}")
    st.write(f"Ausgaben: {locale.currency(payed_interests, grouping=True)}")
    st.write(f"Summe: {locale.currency(earned_interests - payed_interests, grouping=True)}")
    with st.expander("Auszug"):
        st.dataframe(df_interests)


def display_options_shares(df: pd.DataFrame, selected_year: str):
    df_shares = df.query("Category == 'shares'").copy()
    df_shares[["is_option", "action", "count", "underlying"]] = df_shares.apply(parse_option_share_record, axis=1,
                                                                                result_type="expand")
    def add_profits(df_group):
        df_group_for_calc = (df_group
                             .filter(["count", "Credit", "Debit"])
                             .rename(columns={"Credit": "credit", "Debit": "debit"}))
        df_group["profit"] = calc_share_trade_profits(df_group_for_calc)
        return df_group

    df_shares = df_shares.groupby("underlying", as_index=False).apply(add_profits)
    df_shares_selected_year = df_shares.query("Activity_Year == @selected_year").filter(["profit"])
    shares_profits = df_shares_selected_year.query("profit > 0").sum()[0]
    shares_losses = abs(df_shares_selected_year.query("profit < 0")).sum()[0]

    st.header("Aktien")
    st.write(f"Gewinne: {locale.currency(shares_profits, grouping=True)}")
    st.write(f"Verluste: {locale.currency(shares_losses, grouping=True)}")
    with st.expander("Auszug"):
        st.dataframe(df_shares)


    df_options = df.query("Category == 'option'").copy()
    df_options[["is_option", "action", "count", "underlying"]] = df_options.apply(parse_option_share_record, axis=1,
                                                                                  result_type="expand")
    df_options_by_underlying = df_options.filter(["underlying", "Debit", "Credit", "count", "Report Date", "Report_Year", "action"]).groupby("underlying").agg(
        Credit=("Credit", "sum"),
        Debit=("Debit", "sum"),
        Count=("count", "sum"),
        Action=("action", "first"),
        Open=("Report Date", "first"),
        Close=("Report Date", "last"),
        OpenYear=("Report_Year", "first"),
        CloseYear=("Report_Year", "last")).query("Open.dt.year==2022")
    df_stillhalter = df_options_by_underlying.query("Action=='Sell'")
    df_stillhalter_totals = df_stillhalter.filter(["Credit", "Debit"]).sum()
    df_termingeschaefte = df_options_by_underlying.query("Action=='Buy'")
    df_termingeschaefte_totals = df_termingeschaefte.filter(["Credit", "Debit"]).sum()

    stillhalter_einkuenfte = df_stillhalter_totals["Credit"]
    stillhalter_glattstellungen = abs(df_stillhalter_totals["Debit"])
    termingeschaefte_einkuenfte = df_termingeschaefte_totals["Credit"]
    termingeschaefte_glattstellungen = abs(df_termingeschaefte_totals["Debit"])

    st.header("Optionen")
    st.subheader("Stillhaltergeschäfte")
    st.write(f"Einkünfte: {locale.currency(stillhalter_einkuenfte, grouping=True)}")
    st.write(f"Glattstellungen: {locale.currency(stillhalter_glattstellungen, grouping=True)}")
    st.subheader("Termingeschäfte")
    st.write(f"Einkünfte: {locale.currency(termingeschaefte_einkuenfte, grouping=True)}")
    st.write(f"Glattstellungen: {locale.currency(termingeschaefte_glattstellungen, grouping=True)}")
    with st.expander("Auszug"):
        st.dataframe(df_options)


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
    display_interests(df_year)
    display_options_shares(df_year, selected_year)


if __name__ == "__main__":
    main()
