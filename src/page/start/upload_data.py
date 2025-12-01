import io

import pandas as pd
import streamlit as st

from flex_query import DataError, read_statement_of_funds, read_trades, STATEMENT_OF_FUNDS_COLUMNS, TRADES_COLUMNS, \
    read_corporate_actions
from page.utils import render_footer
from report import Report


def create_report(data_files: list):
    df_all_trades = []
    df_all_statement_of_funds = []
    df_all_corporate_actions = []
    for data_file in data_files:
        data_file_content = data_file.getvalue().decode("utf-8")
        df_trades = read_trades(data_file.name, io.StringIO(data_file_content))
        df_statement_of_funds = read_statement_of_funds(data_file.name, io.StringIO(data_file_content))
        df_corporate_actions = read_corporate_actions(data_file.name, io.StringIO(data_file_content))


        # Mix trade data into statement data and vice versa
        df_trades = df_trades.merge(df_statement_of_funds.filter(["TradeID", "AssetClass", "Symbol", "Buy/Sell",
                                                                  "Date", "ActivityDescription", "TradeQuantity",
                                                                  "Amount", "CurrencyPrimary", "Amount_orig",
                                                                  "CurrencyPrimary_orig", "FXRateToBase_orig"]),
                                    how="left",
                                    on=["TradeID", "AssetClass", "Symbol", "Buy/Sell"])
        if not df_trades.empty:
            df_all_trades.append(df_trades)
        df_statement_of_funds = df_statement_of_funds.merge(df_trades.filter(["TradeID", "Open/CloseIndicator"]),
                                                            how="left",
                                                            on="TradeID")
        if not df_statement_of_funds.empty:
            df_all_statement_of_funds.append(df_statement_of_funds)

        if not df_corporate_actions.empty:
            df_all_corporate_actions.append(df_corporate_actions)

    # Ensure chronological order of reports and keep order within each report as is
    df_all_trades.sort(key=lambda data_df: data_df["TradeDate"].iloc[0])
    df_all_statement_of_funds.sort(key=lambda data_df: data_df["Date"].iloc[0])
    df_all_corporate_actions.sort(key=lambda data_df: data_df["Date/Time"].iloc[0])

    result = Report()
    if df_all_trades:
        pd.concat(df_all_trades).apply(lambda row: result.process_trade(row), axis=1)
    if df_all_statement_of_funds:
        pd.concat(df_all_statement_of_funds).apply(lambda row: result.process_statement(row), axis=1)
    return result


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

uploads = intro.file_uploader("Kapitalflussrechnung+Trades (CSV-Format)", type="csv", accept_multiple_files=True)
if uploads:
    intro.write("Daten wurden hochgeladen, durch einen Klick können Sie die Auswertung starten.")
    if intro.button("Auswertung starten", type="primary"):
        try:
            report = create_report(uploads)
            st.session_state["report"] = report
            if report.has_data():
                st.switch_page("page/result/deposits.py")
            else:
                intro.write("Die Dateien enthalten keine Daten. Haben Sie die richtigen Dateien hochgeladen?")
        except DataError as error:
            intro.error(f"""Datei {error} scheint keine CSV-Datei mit der Kapitalflussrechnung und den Trades aus der Flex-Query
            zu sein. Es wird eine CSV-Datei mit mindestens diesen Spalten erwartet: 
            {", ".join(sorted(set(STATEMENT_OF_FUNDS_COLUMNS+TRADES_COLUMNS)))}""")

render_footer("page/start/create_statement.py", None)
