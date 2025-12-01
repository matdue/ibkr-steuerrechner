from decimal import Decimal
from typing import Iterator

import pandas as pd
from pandas.errors import EmptyDataError

from iterable_text_io import IterableTextIO


class DataError(Exception):
    pass


DATE_COLUMNS = ["Expiry", "ReportDate", "Date", "TradeDate"]
STATEMENT_OF_FUNDS_SECTION_CODE = "STFU"
STATEMENT_OF_FUNDS_COLUMNS = \
    ["CurrencyPrimary", "FXRateToBase", "AssetClass", "Symbol", "Conid", "Buy/Sell",
     "Description", "Strike", "Expiry", "Put/Call", "ReportDate", "Date", "ActivityCode",
     "ActivityDescription", "TradeID", "OrderID", "TradeQuantity", "TradePrice", "TradeGross",
     "TradeCommission", "TradeTax", "Amount", "LevelOfDetail", "TransactionID", "ActionID"]
TRADES_COLUMNS_SECTION_CODE = "TRNT"
TRADES_COLUMNS = \
    ["AssetClass", "Symbol", "Conid", "TradeID", "Open/CloseIndicator", "Buy/Sell", "Quantity", "TradeDate"]
CORPORATE_ACTIONS_SECTION_CODE = "CORP"
CORPORATE_ACTIONS_COLUMNS = ["AssetClass","Symbol","Description","Conid","Date/Time","Quantity","Type"]


def decimal_from_value(value: str):
    trimmed_value = value.strip()
    if not trimmed_value:
        return None
    return Decimal(trimmed_value)


def date_from_datetime(value: str):
    date_value, _, _ = value.strip().partition(";")
    return pd.to_datetime(date_value).date()


def csv_part(all_lines: Iterator[str], section_code: str):
    header_line = f"\"HEADER\",\"{section_code}\","
    data_line = f"\"DATA\",\"{section_code}\","
    for line in all_lines:
        if line.startswith(data_line) or line.startswith(header_line):
            yield line


def read_csv_part(filebuf, section_code: str, required_columns: list[str]):
    df = pd.read_csv(IterableTextIO(csv_part(filebuf, section_code)),
                     usecols=required_columns,
                     parse_dates=[col
                                  for col in DATE_COLUMNS
                                  if col in required_columns],
                     converters={
                         "FXRateToBase": decimal_from_value,
                         "Quantity": decimal_from_value,
                         "Strike": decimal_from_value,
                         "TradeQuantity": decimal_from_value,
                         "TradePrice": decimal_from_value,
                         "TradeGross": decimal_from_value,
                         "TradeCommission": decimal_from_value,
                         "TradeTax": decimal_from_value,
                         "Amount": decimal_from_value,
                         "Date/Time": date_from_datetime
                     },
                     dtype={
                         "CurrencyPrimary": "category",
                         "AssetClass": "category",
                         "Buy/Sell": "category",
                         "Put/Call": "category",
                         "Open/CloseIndicator": "category",
                         "ActivityCode": "category",
                         "Conid": "str",
                         "TradeID": "str",
                         "OrderID": "str",
                         "LevelOfDetail": "category",
                         "TransactionID": "str",
                         "ActionID": "str"
                     })
    return df


def convert_dates(df: pd.DataFrame):
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.to_pydatetime().date() if pd.notna(x) else None)


def read_statement_of_funds(filename: str, filebuf):
    try:
        df = read_csv_part(filebuf, STATEMENT_OF_FUNDS_SECTION_CODE, STATEMENT_OF_FUNDS_COLUMNS)
        convert_dates(df)

        # Base currency must be EUR because we are going to calculate German taxes which must be in EUR
        df_base_currency = df.query("LevelOfDetail == 'BaseCurrency'")
        base_currency = ", ".join(df_base_currency["CurrencyPrimary"].unique())
        if base_currency != "EUR":
            print(f"Die Basiswährung des Kontos muss EUR sein. In diesem FlexQuery-Report wurden dagegen die folgende Basiswährung gefunden: {base_currency}")
            return

        # Fees of forex transactions
        df_forex_fees = (df
                         .query(f"ActivityCode == 'FOREX' and LevelOfDetail == 'Currency' and CurrencyPrimary == '{base_currency}'")
                         .groupby("TradeID", as_index=False)[["Amount"]]
                         .sum())
        df_base_currency = df_base_currency.merge(df_forex_fees, how="left", on="TradeID", suffixes=(None, "_forex_fee"))
        df_base_currency["Amount_forex_fee"] = df_base_currency["Amount_forex_fee"].fillna(Decimal(0))
        df_base_currency["Amount"] += df_base_currency["Amount_forex_fee"]
        df_base_currency.drop(columns=["Amount_forex_fee"], inplace=True)

        df_orig_currency = df.query(f"LevelOfDetail == 'Currency' and CurrencyPrimary != '{base_currency}'")
        df = df_base_currency.merge(df_orig_currency, how="left", on="TransactionID", suffixes=(None, "_orig"))

        # Fix FX rate because the current FX rate does not include trade commissions
        df["FXRateToBase_orig"] = df.apply(
            lambda row: abs(round(row["Amount"] / row["Amount_orig"], 5)) if row["ActivityCode"] == "FOREX"
            else row["FXRateToBase_orig"], axis=1)

        return df
    except Exception:
        raise DataError(filename)


def read_trades(filename: str, filebuf):
    try:
        df = read_csv_part(filebuf, TRADES_COLUMNS_SECTION_CODE, TRADES_COLUMNS)
        convert_dates(df)
        df.sort_values(by="TradeDate", kind="stable", inplace=True)
        return df
    except EmptyDataError:
        return pd.DataFrame(columns=TRADES_COLUMNS)
    except Exception:
        raise DataError(filename)

def read_corporate_actions(filename: str, filebuf):
    try:
        df = read_csv_part(filebuf, CORPORATE_ACTIONS_SECTION_CODE, CORPORATE_ACTIONS_COLUMNS)
        convert_dates(df)
        df.sort_values(by="Date/Time", kind="stable", inplace=True)
        return df
    except EmptyDataError:
        return pd.DataFrame(columns=CORPORATE_ACTIONS_COLUMNS)
    except Exception:
        raise DataError(filename)
