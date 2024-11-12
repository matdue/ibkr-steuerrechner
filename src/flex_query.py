from decimal import Decimal

import pandas as pd

REQUIRED_COLUMNS = ["CurrencyPrimary", "FXRateToBase", "AssetClass", "Symbol", "Buy/Sell",
                    "Description", "Strike", "Expiry", "Put/Call", "ReportDate", "Date", "ActivityCode",
                    "ActivityDescription", "TradeID", "OrderID", "TradeQuantity", "TradePrice", "TradeGross",
                    "TradeCommission", "TradeTax", "Amount", "LevelOfDetail", "TransactionID", "ActionID"]

class DataError(Exception):
    pass


def decimal_from_value(value: str):
    trimmed_value = value.strip()
    if not trimmed_value:
        return None
    return Decimal(trimmed_value)


def read_report(filename: str, filebuf = None):
    try:
        df = pd.read_csv(filebuf if filebuf is not None else filename,
                         usecols=REQUIRED_COLUMNS,
                         parse_dates=["Expiry", "ReportDate", "Date"],
                         converters={
                             "FXRateToBase": decimal_from_value,
                             "Strike": decimal_from_value,
                             "TradeQuantity": decimal_from_value,
                             "TradePrice": decimal_from_value,
                             "TradeGross": decimal_from_value,
                             "TradeCommission": decimal_from_value,
                             "TradeTax": decimal_from_value,
                             "Amount": decimal_from_value
                         },
                         dtype={
                             "CurrencyPrimary": "category",
                             "AssetClass": "category",
                             "Put/Call": "category",
                             "ActivityCode": "category",
                             "TradeID": "str",
                             "OrderID": "str",
                             "LevelOfDetail": "category",
                             "TransactionID": "str",
                             "ActionID": "str"
                         })
        df["Expiry"] = df["Expiry"].apply(lambda x: x.to_pydatetime().date() if pd.notna(x) else None)
        df["ReportDate"] = df["ReportDate"].apply(lambda x: x.to_pydatetime().date() if pd.notna(x) else None)
        df["Date"] = df["Date"].apply(lambda x: x.to_pydatetime().date() if pd.notna(x) else None)
        df["TradeID"] = df["TradeID"].apply(lambda x: x if pd.notna(x) else None)
        df["Buy/Sell"] = df["Buy/Sell"].apply(lambda x: x if pd.notna(x) else None)

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

        return df
    except Exception:
        raise DataError(filename)
