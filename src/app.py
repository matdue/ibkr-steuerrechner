import io
import re
from dataclasses import dataclass, asdict
from decimal import Decimal
from enum import Enum, auto

import pandas as pd
import streamlit as st

from i18n import format_date, format_currency, get_column_name
from iterable_text_io import IterableTextIO
from utils import calc_profits_fifo

RECORD_FUND_TRANSFER = re.compile(r"(Electronic Fund Transfer)|(Disbursement .*)")
RECORD_DIVIDEND = re.compile(r"Cash Dividend|Payment in Lieu of Dividend")
RECORD_INTEREST = re.compile(r"Credit|Debit Interest")
RECORD_OPTION = re.compile(r"(Buy|Sell) (-?[0-9,]+) (.{1,5} [0-9]{2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[0-9]{2} [0-9]+(\.[0-9]+)? ([PC])) (\(\w+\))?")
RECORD_SHARES = re.compile(r"(Buy|Sell) (-?[0-9,]+) (.*?)\s*(\(\w+\))?$")
RECORD_FOREX = re.compile(r"Forex Trade")
RECORD_MARKET_DATA_SUBSCRIPTION = re.compile(r"[A-Za-z]\*{6}[0-9]{2}:")


class Category(Enum):
    BALANCE = auto()
    TRANSFER = auto()
    DIVIDEND = auto()
    INTEREST = auto()
    OPTION = auto()
    SHARES = auto()
    FOREX = auto()
    MARKET_DATA_SUBSCRIPTION = auto()
    OTHER = auto()


def categorize_statement_record(record: pd.Series) -> str:
    description = record["Description"]
    if description in ["Opening Balance", "Closing Balance"]:
        return Category.BALANCE.name
    if RECORD_FUND_TRANSFER.fullmatch(description):
        return Category.TRANSFER.name
    if RECORD_DIVIDEND.search(description):
        return Category.DIVIDEND.name
    if RECORD_INTEREST.search(description):
        return Category.INTEREST.name
    if RECORD_OPTION.match(description):
        return Category.OPTION.name
    if RECORD_SHARES.match(description):
        return Category.SHARES.name
    if RECORD_FOREX.search(description):
        return Category.FOREX.name
    if RECORD_MARKET_DATA_SUBSCRIPTION.search(description):
        return Category.MARKET_DATA_SUBSCRIPTION.name

    return Category.OTHER.name


@dataclass
class FinancialAction:
    action: str
    count: int
    name: str


def parse_option_share_record(record: pd.Series) -> dict:
    description = record["Description"]
    match = RECORD_OPTION.match(description)
    if match is not None:
        # Cleansing: Remove ending .0 from strike price as some options have this precision specification and some not
        name = re.sub(r"(.*?)(\.0)( [CP])", r"\1\3", match.group(3))
        return asdict(FinancialAction(match.group(1), int(match.group(2).replace(",", "")), name))

    match = RECORD_SHARES.match(description)
    if match is not None:
        return asdict(FinancialAction(match.group(1), int(match.group(2).replace(",", "")), match.group(3)))


class DividendType(Enum):
    ORDINARY = auto()
    TAX = auto()
    OTHER = auto()


def parse_dividend_record(record: pd.Series) -> str:
    description = record["Description"]
    if type(description) is not str:
        return DividendType.OTHER.name
    if description.endswith(" (Ordinary Dividend)"):
        return DividendType.ORDINARY.name
    if description.endswith(" Tax"):
        return DividendType.TAX.name

    return DividendType.OTHER.name


class DataError(Exception):
    pass


def read_statement_file(file: io.TextIOBase, filename: str) -> pd.DataFrame:
    """
    Reads and parses the input field and returns a dataframe with the following columns:

    Report Date: Date of record
    Activity Date: Date of activity
    Description: Type of activity in human-readable text
    Debit: Debit amount of activity (negative or none)
    Credit: Credit amount of activity (positive or none)
    Year: Year of report date (duplicated for convenience)

    :param file: Input file
    :param filename: Input file name
    :return: Pandas Dataframe
    """

    def decimal_from_value(value: str):
        trimmed_value = value.strip()
        if not trimmed_value:
            return None
        return Decimal(trimmed_value)

    try:
        # Load relevant lines only
        # A CSV may contain more than one report, but we are interested in Statement of Funds only
        statement_of_funds_lines = (line for line in file if line.startswith("Statement of Funds,"))
        with IterableTextIO(statement_of_funds_lines) as s:
            # noinspection PyTypeChecker
            df = pd.read_csv(s,
                             usecols=["Currency", "Report Date", "Activity Date", "Description", "Debit", "Credit"],
                             parse_dates=["Report Date", "Activity Date"],
                             converters={"Debit": decimal_from_value, "Credit": decimal_from_value})
        df["Total"] = df[["Debit", "Credit"]].sum(axis=1)
        df["Report_Year"] = df["Report Date"].dt.year.astype("str")
        df["Activity_Year"] = df["Activity Date"].apply(lambda d: None if pd.isnull(d) else str(d.year))

        # Skip all records which are not in base currency
        df = df.query("Currency == 'Base Currency Summary'").drop(columns=["Currency"])

        return df
    except Exception:
        raise DataError(filename)


def display_dataframe(df: pd.DataFrame, date_columns: list[str], number_columns: list[str]):
    background_color = ["background-color: White", "background-color: GhostWhite"]

    def alternate_background(row):
        return [background_color[row["TradeSequence"] % 2]] * len(row)

    # Convert decimals to floats as the dataframe view is unable to handle decimals properly
    for number_column in number_columns:
        df[number_column] = df[number_column].apply(lambda x: None if pd.isnull(x) else float(round(x, 2)))
    
    column_config = {date_column: st.column_config.DateColumn(get_column_name(date_column))
                     for date_column in date_columns}
    column_config |= {number_column: st.column_config.NumberColumn(get_column_name(number_column))
                      for number_column in number_columns}
    date_format = {date_column: lambda x: format_date(x) for date_column in date_columns}
    number_format = {number_column: lambda x: format_currency(x) for number_column in number_columns}
    formats = date_format | number_format

    # Rename remaining columns
    column_config |= {col: get_column_name(col)
                      for col in df.columns
                      if col not in date_columns and col not in number_columns}

    if "Trade" in df.columns:
        # Transform column Trade into a sequence, so we can switch the background whenever a different trade is
        # displayed.
        # Example:
        # Trade  Action
        # 0      Buy
        # 0      Sell
        # 2      Buy
        # 5      Buy
        # Goal:
        # TradeSequence  Action
        # 0              Buy
        # 0              Sell
        # 1              Buy
        # 2              Buy
        # This way we are able to use an alternating background for each different trade by calculating
        # TradeSequence % 2
        df["TradeSequence"] = df.groupby("Trade", as_index=False, group_keys=True, sort=False).ngroup()
        column_config["TradeSequence"] = None
        st.dataframe(df.style.apply(alternate_background, axis=1).format(formats),
                     hide_index=True, column_config=column_config)
    else:
        st.dataframe(df.style.format(formats),
                     hide_index=True, column_config=column_config)


def display_fund_transfer(df_year: pd.DataFrame):
    st.header("Ein- und Auszahlungen")
    st.write("""Alle Ein- und Auszahlen werden aufsummiert. Beide Summen dienen nur der Information und sind steuerlich
    nicht relevant.""")
    df_transfer = df_year.query(f"Category == '{Category.TRANSFER.name}'")
    deposited_funds = df_transfer["Credit"].sum()
    withdrawn_funds = df_transfer["Debit"].sum()
    st.write(f"Einzahlungen: {format_currency(deposited_funds)}")
    st.write(f"Auszahlungen: {format_currency(-withdrawn_funds)}")
    with st.expander("Kapitalflussrechnung (nur Ein- und Auszahlungen)"):
        display_dataframe(df_transfer.filter(["Report Date", "Activity Date", "Description", "Total"]),
                          ["Report Date", "Activity Date"], ["Total"])


def display_dividends(df_year: pd.DataFrame, df_year_corrections: pd.DataFrame, selected_year: str):
    st.header("Dividenden")
    st.write("""Alle Dividenden werden aufsummiert, die Quellensteuern werden gesondert ausgewiesen. 
    Manchmal werden Zahlungen und/oder Steuern im Folgejahr korrigiert; 
    die Korrektur wird, wenn vorhanden, hier gesondert ausgewiesen.""")
    df_dividend = df_year.query(f"Category == '{Category.DIVIDEND.name}'")
    df_dividend["DividendType"] = df_dividend.apply(parse_dividend_record, axis=1).astype("category")
    df_dividend_corrections = df_year_corrections.query(f"Category == '{Category.DIVIDEND.name}'")
    df_dividend_corrections["DividendType"] = (df_dividend_corrections.apply(parse_dividend_record, axis=1)
                                               .astype("category"))

    ordinary_dividends = df_dividend.query(f"DividendType == '{DividendType.ORDINARY.name}'")
    ordinary_dividends_corrections = df_dividend_corrections.query(f"DividendType == '{DividendType.ORDINARY.name}'")
    earned_dividends = ordinary_dividends["Total"].sum()
    earned_dividends_corrections = ordinary_dividends_corrections["Total"].sum()

    taxes = df_dividend.query(f"DividendType == '{DividendType.TAX.name}'")
    taxes_corrections = df_dividend_corrections.query(f"DividendType == '{DividendType.TAX.name}'")
    withheld_taxes = taxes["Total"].sum()
    withheld_taxes_corrections = taxes_corrections["Total"].sum()

    others = df_dividend.query(f"DividendType == '{DividendType.OTHER.name}'")
    others_corrections = df_dividend_corrections.query(f"DividendType == '{DividendType.OTHER.name}'")
    other_dividends = others["Total"].sum()
    other_dividends_corrections = others_corrections["Total"].sum()

    st.subheader("Gewöhnliche Dividenden")
    if earned_dividends_corrections:
        st.write(f"Summe {selected_year}: {format_currency(earned_dividends)}")
        st.write(f"Korrektur: {format_currency(earned_dividends_corrections)}")
    st.write(f"Summe: {format_currency(earned_dividends + earned_dividends_corrections)}")

    st.subheader("Quellensteuer")
    if withheld_taxes_corrections:
        st.write(f"Summe {selected_year}: {format_currency(withheld_taxes * (-1))}")
        st.write(f"Korrektur: {format_currency(withheld_taxes_corrections * (-1))}")
    st.write(f"Summe: {format_currency((withheld_taxes + withheld_taxes_corrections) * (-1))}")

    if other_dividends or other_dividends_corrections:
        st.subheader("Andere Zahlungen")
        st.write(f"Summe {selected_year}: {format_currency(other_dividends)}")
        st.write(f"Korrektur: {format_currency(other_dividends_corrections)}")
        st.write(f"Summe: {format_currency(other_dividends + other_dividends_corrections)}")

    with st.expander("Kapitalflussrechnung (nur Dividenden)"):
        display_dataframe((pd.concat([df_dividend, df_dividend_corrections])
                           .filter(["Report Date", "Activity Date", "Description", "Total"])),
                          ["Report Date", "Activity Date"], ["Total"])


def display_interests(df_year: pd.DataFrame):
    st.header("Zinsen")
    st.write("Alle Zinseinnahmen und -ausgaben werden aufsummiert.")
    df_interests = df_year.query(f"Category == '{Category.INTEREST.name}'")
    earned_interests = df_interests["Credit"].sum()
    payed_interests = abs(df_interests["Debit"].sum())
    st.write(f"Einnahmen: {format_currency(earned_interests)}")
    st.write(f"Ausgaben: {format_currency(payed_interests)}")
    st.write(f"Summe: {format_currency(earned_interests - payed_interests)}")
    with st.expander("Kapitalflussrechnung (nur Zinsen)"):
        display_dataframe(df_interests.filter(["Report Date", "Activity Date", "Description", "Total"]),
                          ["Report Date", "Activity Date"], ["Total"])


def _add_profits(df_group, trade_counter: dict):
    df_profit = calc_profits_fifo(df_group.filter(["Count", "Credit", "Debit"]),
                                  "Count", "Debit", "Credit")
    df_profit["trade"] = df_profit["start_of_trade"].cumsum() + trade_counter["trade"]
    trade_counter["trade"] = df_profit["trade"].max()

    df_group[["Profit", "Trade"]] = df_profit[["profit", "trade"]]
    return df_group


def display_shares(df: pd.DataFrame, selected_year: str):
    df_shares = (df.query(f"Category == '{Category.SHARES.name}'")
                 .filter(["Report Date", "Activity Date", "Description", "Debit", "Credit", "Total", "Report_Year",
                          "Activity_Year"]))
    if not df_shares.empty:
        df_shares[["Action", "Count", "Name"]] = df_shares.apply(parse_option_share_record, axis=1,
                                                                 result_type="expand")
        df_shares_by_name = df_shares.groupby("Name", as_index=False, group_keys=True, sort=False)
        df_shares = df_shares_by_name.apply(_add_profits, {"trade": 0}, include_groups=True)
        df_shares_selected_year = df_shares.query("Activity_Year == @selected_year")
        shares_profits = df_shares_selected_year.query("Profit > 0").get("Profit").sum()
        shares_losses = abs(df_shares_selected_year.query("Profit < 0").get("Profit")).sum()
        shares_total = shares_profits - shares_losses
    else:
        shares_profits = 0
        shares_losses = 0
        shares_total = shares_profits - shares_losses
        df_shares_selected_year = pd.DataFrame(columns=["Profit", "Trade"])

    st.header("Aktien")
    st.write("""Gewinne und Verluste aus Aktienkäufe, -verkäufe, -andienungen und -ausbuchungen werden nach der
    FIFO-Methode berechnet und hier ausgewiesen. Käufe und Andienungen werden steuerlich erst dann relevant, wenn die
    Position durch Verkauf oder Ausbuchung geschlossen wird. Erfolgt die Schließung erst im Folgejahr, wird erst dann
    ein Gewinn oder Verlust berechnet.""")
    st.write(f"Gewinne: {format_currency(shares_profits)}")
    st.write(f"Verluste: {format_currency(shares_losses)}")
    st.write(f"Summe: {format_currency(shares_total)}")
    st.write(f"Verlusttopf: {format_currency(abs(min(shares_total, 0)))}")
    with st.expander(f"Kapitalflussrechnung (nur in {selected_year} abgeschlossene Aktiengeschäfte)"):
        closed_trades = df_shares_selected_year.query("Profit != 0").get("Trade").unique()
        display_dataframe(df_shares_selected_year.query("Trade in @closed_trades")
                          .reindex(columns=["Trade", "Report Date", "Activity Date", "Description", "Count", "Name",
                                            "Total", "Profit"])
                          .sort_values(["Trade", "Report Date"]),
                          ["Report Date", "Activity Date"], ["Total", "Profit"])

    with st.expander("Kapitalflussrechnung (nur Aktiengeschäfte)"):
        display_dataframe(df_shares
                          .reindex(columns=["Trade", "Report Date", "Activity Date", "Description", "Count", "Name",
                                            "Total", "Profit"])
                          .sort_values(["Trade", "Report Date"]),
                          ["Report Date", "Activity Date"], ["Total", "Profit"])


def display_options(df: pd.DataFrame, selected_year: str):
    df_options = (df.query(f"Category == '{Category.OPTION.name}'")
                  .filter(["Report Date", "Activity Date", "Description", "Debit", "Credit", "Total", "Report_Year",
                           "Activity_Year"]))
    if not df_options.empty:
        df_options[["Action", "Count", "Name"]] = df_options.apply(parse_option_share_record, axis=1,
                                                                   result_type="expand")
        df_options_by_name = df_options.groupby("Name", as_index=False, group_keys=True, sort=False)
        df_options = df_options_by_name.apply(_add_profits, {"trade": 0}, include_groups=True)
        df_options_by_trade = (df_options.filter(["Trade", "Name", "Debit", "Credit", "Count", "Profit",
                                                  "Activity_Year", "Action"])
                               .groupby("Trade", sort=False)
                               .agg(Credit=("Credit", "sum"),
                                    Debit=("Debit", "sum"),
                                    Count=("Count", "sum"),
                                    Profit=("Profit", "sum"),
                                    Action=("Action", "first"),
                                    Open=("Activity_Year", "first"),
                                    Close=("Activity_Year", "last"),
                                    Trade=("Trade", "first"),
                                    Name=("Name", "first"))
                               .query("Open == @selected_year"))
    else:
        df_options_by_trade = pd.DataFrame(columns=["Action", "Credit", "Debit", "Profit", "Trade"])
        df_options["Trade"] = None

    df_stillhalter = df_options_by_trade.query("Action=='Sell'")
    df_stillhalter_totals = df_stillhalter.filter(["Credit", "Debit", "Profit"]).sum()
    stillhalter_einkuenfte = df_stillhalter_totals["Credit"]
    stillhalter_glattstellungen = abs(df_stillhalter_totals["Debit"])
    stillhalter_total = stillhalter_einkuenfte - stillhalter_glattstellungen

    df_termingeschaefte = df_options_by_trade.query("Action=='Buy'")
    df_termingeschaefte_totals = df_termingeschaefte.filter(["Credit", "Debit", "Profit"]).sum()
    termingeschaefte_einkuenfte = df_termingeschaefte_totals["Credit"]
    termingeschaefte_glattstellungen = abs(df_termingeschaefte_totals["Debit"])
    termingeschaefte_total = termingeschaefte_einkuenfte - termingeschaefte_glattstellungen
    termingeschaefte_verlusttopf = 0
    if termingeschaefte_total < 0:
        termingeschaefte_verlusttopf = abs(termingeschaefte_total)
        if stillhalter_total > 0:
            # Stillhalter profits can even Termingeschäfte losses up to 20,000 €
            termingeschaefte_verlusttopf -= min([stillhalter_total, 20000, termingeschaefte_verlusttopf])

    st.header("Optionen")
    st.write("""Gewinne und Verluste aus Optionsgeschäften werden nach der FIFO-Methode berechnet und hier ausgewiesen.
    Stillhaltergeschäfte sind sofort steuerlich relevant, Termingeschäfte erst mit Schließung der Position.
    Der Sonderfall Barausgleich wird nicht berücksichtigt.""")
    st.write("""Verluste aus Termingeschäfte können bei Privatpersonen nur beschränkt mit Gewinnen aus
    Stillhaltergeschäften ausgeglichen werden. Alles über 20.000 € wird in den Verlusttopf gelegt.""")
    st.subheader("Stillhaltergeschäfte")
    st.write(f"Einkünfte: {format_currency(stillhalter_einkuenfte)}")
    st.write(f"Glattstellungen: {format_currency(stillhalter_glattstellungen)}")
    st.write(f"Summe: {format_currency(stillhalter_einkuenfte - stillhalter_glattstellungen)}")
    with st.expander("Kapitalflussrechnung (nur Stillhaltergeschäfte)"):
        stillhalter_trades = df_stillhalter.get("Trade").unique()
        df_options_display = (df_options
                              .query("Trade in @stillhalter_trades")
                              .reindex(columns=["Trade", "Report Date", "Activity Date", "Description", "Count", "Name",
                                                "Action", "Total", "Profit"])
                              .sort_values(["Trade", "Activity Date"]))
        display_dataframe(df_options_display,
                          ["Report Date", "Activity Date"], ["Total", "Profit"])

    st.subheader("Termingeschäfte")
    st.write(f"Einkünfte: {format_currency(termingeschaefte_einkuenfte)}")
    st.write(f"Glattstellungen: {format_currency(termingeschaefte_glattstellungen)}")
    st.write(f"Summe: {format_currency(termingeschaefte_einkuenfte - termingeschaefte_glattstellungen)}")
    st.write(f"Verlusttopf: {format_currency(termingeschaefte_verlusttopf)}")
    with st.expander("Kapitalflussrechnung (nur Termingeschäfte)"):
        termingeschaefte_trades = df_termingeschaefte.get("Trade").unique()
        df_options_display = (df_options
                              .query("Trade in @termingeschaefte_trades")
                              .reindex(columns=["Trade", "Report Date", "Activity Date", "Description", "Count", "Name",
                                                "Action", "Total", "Profit"])
                              .sort_values(["Trade", "Activity Date"]))
        display_dataframe(df_options_display,
                          ["Report Date", "Activity Date"], ["Total", "Profit"])


def display_forex(df_year: pd.DataFrame):
    st.header("Währungsumrechnungen")
    st.write("""Fremdwährungskäufe und -verkäufe werden hier nur aufgelistet, aber nicht weiter ausgewertet. Gewinne,
    die durch Fremdwährungsgeschäfte erwirtschaftet werden, sind steuerlich relevant!""")
    df_forex = df_year.query(f"Category == '{Category.FOREX.name}'")
    with st.expander("Kapitalflussrechnung (nur Währungsumrechnungen)"):
        display_dataframe(df_forex.filter(["Report Date", "Activity Date", "Description", "Total"]),
                          ["Report Date", "Activity Date"], ["Total"])


def display_market_data_subscriptions(df_year: pd.DataFrame):
    st.header("Marktdatenabonnements")
    st.write("""Gebühren von Marktdatenabonnements werden aufsummiert. Privatleute können diese Gebühren i.d.R. nicht 
    absetzen.""")
    df_mds = df_year.query(f"Category == '{Category.MARKET_DATA_SUBSCRIPTION.name}'")
    mds_income = df_mds["Credit"].sum()
    mds_expense = abs(df_mds["Debit"].sum())
    st.write(f"Einnahmen: {format_currency(mds_income)}")
    st.write(f"Ausgaben: {format_currency(mds_expense)}")
    st.write(f"Summe: {format_currency(mds_income - mds_expense)}")
    with st.expander("Kapitalflussrechnung (nur Marktdatenabonnements)"):
        display_dataframe(df_mds.filter(["Report Date", "Activity Date", "Description", "Total"]),
                          ["Report Date", "Activity Date"], ["Total"])


def display_other(df_year: pd.DataFrame):
    st.header("Rest")
    st.write("Diese Posten konnten keiner Kategorie zugeordnet werden und wurden daher nicht berücksichtigt.")
    df_other = df_year.query(f"Category == '{Category.OTHER.name}'")
    with st.expander("Kapitalflussrechnung (restliche Posten)"):
        display_dataframe(df_other.filter(["Report Date", "Activity Date", "Description", "Total"]),
                          ["Report Date", "Activity Date"], ["Total"])


def main():
    pd.options.mode.copy_on_write = True

    st.set_page_config("IBKR Steuerrechner", layout="wide")
    st.title("Steuerrechner für Interactive Brokers")
    st.caption("Zur Berechnung der Steuerschuld von Optionen- und Aktiengeschäften")

    # Do not use the whole width to display the introduction, use a smaller part to make it better readable
    intro, _ = st.columns([2, 1])
    intro.write("""Die Auswertung ersetzt keine Steuerberatung! Alle Angaben sind ohne Gewähr und dienen nur der 
    Inspiration.""")
    intro.write("""Dieses Programm ist Open Source, der Programmcode ist auf 
    [GitHub](https://github.com/matdue/ibkr-steuerrechner) zu finden.""")

    # Statement of Funds (Kapitalflussrechnung)
    intro.write("#### Kontoauszug erstellen")
    intro.write("""Laden Sie zunächst in der Weboberfläche von Interactive Brokers einen Kontoauszug, der die 
    Kapitalflussrechnung enthält, herunter und speichern Sie sie auf ihrem eigenen Rechner ab. Wenn Sie noch keinen so 
    genannten *Benutzerdefinierten Kontoauszug* erstellt haben, klappen Sie den nachfolgenden Block auf und folgen
    den Anweisungen.""")
    with intro.expander("Benutzerdefinierten Kontoauszug erstellen"):
        st.write("""
        1. Loggen Sie sich in der Weboberfläche von Interactive Brokers ein
        1. Wählen Sie den Menüpunkt *Performance & Berichte / Kontoauszüge*
        1. Klicken Sie auf das Plus-Symbol unten im Abschnitt *Benutzerdefinierte Kontoauszüge*
        1. Vergeben Sie einen Namen (z.B. Kapitalflussrechnung)
        1. Wählen Sie als einzigen Abschnitt *Kapitalflussrechnung (Statement of Funds)* aus
        1. Setzen Sie alle Abschnittseinstellungen auf *Nein* bzw. *Keine*
        1. Speichern Sie den benutzerdefinierten Kontoauszug durch einen Klick auf *Weiter* und anschließend *Erstellen*
           ab
        
        Anschließend kann der Kontoauszug durch einen Klick auf den Start-Pfeil generiert werden. Wählen Sie den
        gewünschten Zeitraum, stellen Sie die Sprache auf Englisch um, und klicken Sie auf *Download* bei CSV-Format.
        
        Der Zeitraum ist typischerweise ein komplettes, vergangenes Jahr oder *Jahresbeginn bis heute* für das aktuelle 
        Jahr. Ein Auszug umfasst maximal ein Jahr. Es ist empfehlenswert, den Download im PDF-Format zu wiederholen, er 
        kann als Beleg für das Finanzamt dienen. Sichern Sie beide Dateien, dann können sie bei zukünftigen Auswertungen 
        darauf zurückgreifen.
        
        Die Kapitalflussrechnung enthält keine personenbezogenen Daten, d.h. keinen Namen, keine Depotnummer
        usw. Sollten Sie weitere Abschnitte in den Kontoauszug aufnehmen, werden diese bei der Auswertung ignoriert.
        Dennoch werden diese Daten zum Server übertragen, da sie in der CSV-Datei enthalten sind. Prüfen Sie daher ggf.,
        ob Sie wirklich nur die Kapitalflussrechnung ausgewählt haben.""")

    # Data upload
    intro.write("#### Kontoauszug zur Auswertung übertragen")
    intro.write("""Für die Auswertung können Sie mehrere Dateien hochladen und anschließend das Auswertungsjahr 
    auswählen. Auf diese Weise kann die Historie aus den vergangenenen Jahren berücksichtigt werden, z.B. für über den
    Jahreswechsel gehaltene Positionen.""")
    intro.write("""Alle hochgeladenen Daten werden auf einem Server in den USA verarbeitet. Sie werden nur im 
    Hauptspeicher des Servers abgelegt, sie werden weder dauerhaft noch zeitweise gespeichert. Sobald Sie das 
    Browserfenster schließen, werden die Daten aus dem Speicher entfernt.""")
    try:
        sof_files = intro.file_uploader("Kapitalflussrechnung (CSV-Format)", type="csv", accept_multiple_files=True)
        sof_dfs = [read_statement_file(io.TextIOWrapper(sof_file, "utf-8"), sof_file.name)
                   for sof_file in sof_files]
        if len(sof_dfs) == 0:
            return
    except DataError as error:
        intro.error(f"""In Datei {error} fehlt die Spalte 'Report Date'; bitte laden Sie den Kontoauszug in englischer
        Sprache herunter.""")
        return

    intro.write("#### Auswertung starten")
    intro.write("""Wählen Sie nun das Kalenderjahr aus, für das die Kontoauszüge ausgewertet werden sollen. Sie können
    beliebig oft zwischen den Kalenderjahren wechseln, ohne die Kontoauszügen neu hochladen zu müssen.""")
    # Skip empty reports
    sof_dfs = [sof_df for sof_df in sof_dfs if not sof_df.empty]
    # Ensure chronological order of reports and keep order within each report as is
    sof_dfs.sort(key=lambda sof_df: sof_df["Report Date"].iloc[0])
    df = pd.concat(sof_dfs, ignore_index=True)
    years = df["Report_Year"].unique()
    years_options = ["Bitte wählen"] + list(years)[::-1]
    selected_year = intro.selectbox("Für welches Kalenderjahr sollen die Steuern berechnet werden?", years_options)
    if selected_year == years_options[0]:
        return

    st.header(f"Ergebnis für das Jahr {selected_year}")
    st.write("""Durch Anklicken des unten stehenden Blocks kann dieser aufgeklappt werden.
             Er enthält alle Posten aus der Kapitalflussrechnung. Jeder Posten wurde einer Kategorie zugeordnet.  
             Weiter unten werden für jede Kategorie die Posten ausgewertet und aufsummiert.""")
    df["Category"] = df.apply(categorize_statement_record, axis=1).astype("category")
    df_year = df.query("Report_Year == @selected_year and Activity_Year == @selected_year")
    df_year_corrections = df.query("Report_Year > @selected_year and Activity_Year == @selected_year")
    with st.expander("Komplette Kapitalflussrechnung"):
        display_dataframe(df.filter(["Report Date", "Activity Date", "Description", "Debit", "Credit", "Total",
                                     "Category"]),
                          ["Report Date", "Activity Date"], ["Debit", "Credit", "Total"])
        st.write("Legende:")
        st.write(f""" 
        | Kategorie | Beschreibung |
        | --------- | ------------ |
        | {Category.BALANCE.name} | Anfangs- und Schlusssaldo |
        | {Category.TRANSFER.name} | Ein- und Auszahlungen |
        | {Category.INTEREST.name} | Zinsen |
        | {Category.DIVIDEND.name} | Dividenden |
        | {Category.SHARES.name} | Aktien |
        | {Category.OPTION.name} | Optionen |
        | {Category.FOREX.name} | Währungsumrechnungen |
        | {Category.MARKET_DATA_SUBSCRIPTION.name} | Marktdatenabonnements |
        | {Category.OTHER.name} | Nicht zuordenbar |""")

    display_fund_transfer(df_year)
    display_dividends(df_year, df_year_corrections, selected_year)
    display_interests(df_year)
    display_shares(df, selected_year)
    display_options(df, selected_year)
    display_forex(df_year)
    display_market_data_subscriptions(df_year)
    display_other(df_year)


if __name__ == "__main__":
    main()
