import io

import pandas as pd

from flex_query import read_statement_of_funds, read_trades, read_corporate_actions
from report import Report


def read_report(filename: str) -> Report:
    with open(filename, encoding="utf-8") as csv_file:
        data_file_content = csv_file.read()
        df_statement_of_funds = read_statement_of_funds(filename, io.StringIO(data_file_content))
        df_trades = read_trades(filename, io.StringIO(data_file_content))
        df_corporate_actions = read_corporate_actions(filename, io.StringIO(data_file_content))

        # Mix trade data into statement data and vice versa
        df_trades = df_trades.merge(df_statement_of_funds.filter(["TradeID", "AssetClass", "Conid", "Buy/Sell",
                                                                  "Date", "ActivityDescription", "TradeQuantity",
                                                                  "Amount", "CurrencyPrimary", "Amount_orig",
                                                                  "CurrencyPrimary_orig", "FXRateToBase_orig"]),
                                    how="left",
                                    on=["TradeID", "AssetClass", "Conid", "Buy/Sell"])
        df_statement_of_funds = df_statement_of_funds.merge(df_trades.filter(["TradeID", "Open/CloseIndicator"]),
                                                            how="left",
                                                            on="TradeID")

        result = Report()
        df_trades.apply(lambda row: result.process_trade(row), axis=1)
        df_statement_of_funds.apply(lambda row: result.process_statement(row), axis=1)
        df_corporate_actions.apply(lambda row: result.process_corporate_action(row), axis=1)

        return result


def read_report2(filename: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    with open(filename, encoding="utf-8") as csv_file:
        data_file_content = csv_file.read()
        df_statement_of_funds = read_statement_of_funds(filename, io.StringIO(data_file_content))
        df_trades = read_trades(filename, io.StringIO(data_file_content))
        return df_statement_of_funds, df_trades
