from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from io import BytesIO
from itertools import groupby
from typing import Iterable

import pandas as pd

from deposit import Deposit
from depot_position import DepotPosition, DepotPositionType
from dividend import Dividend
from foreign_currency_account import ForeignCurrencyAccount
from forex import Forex
from interest import Interest
from money import Money
from option import Option
from other_fee import OtherFee
from stock import Stock
from transaction import Transaction, BuySell, OpenCloseIndicator, AcquisitionType
from transaction_collection import apply_estg_23, TransactionCollection
from treasury_bill import TreasuryBill
from unknown_line import UnknownLine


@dataclass
class Result:
    year: int
    df: pd.DataFrame

    def total(self, column: str) -> float:
        data = self.df[column]
        return data.sum()

    def total_positive(self, column: str) -> float:
        data = self.df[column]
        return data[data >= 0].sum()

    def total_negative(self, column: str) -> float:
        data = self.df[column]
        return data[data < 0].sum()

    def to_csv(self, columns: dict[str, str]) -> str:
        df_export = self.df.filter(columns.keys()).rename(columns=columns)
        csv = df_export.to_csv(index=False)
        return csv

    def to_excel(self, name: str, columns: dict[str, str], decimal_columns: list[str] = None) -> BytesIO:
        df_export = self.df.filter(columns.keys())
        if decimal_columns:
            for decimal_column in decimal_columns:
                # Convert decimals to float as to_excel of Pandas 2.2 exports decimals as strings
                df_export[decimal_column] = df_export[decimal_column].astype(float)
        df_export = df_export.rename(columns=columns)
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file) as writer:
            df_export.to_excel(writer, index=False, sheet_name=name)
        excel_file.seek(0)
        return excel_file


class Report:
    def __init__(self):
        self._years: set[str] = set()
        self._deposits: list[Deposit] = []
        self._interests: list[Interest] = []
        self._other_fees: list[OtherFee] = []
        self._dividends: list[Dividend] = []
        self._stocks: list[Stock] = []
        self._options: list[Option] = []
        self._treasury_bills: list[TreasuryBill] = []
        self._forexes: list[Forex] = []
        self._foreign_currency_accounts: dict[str, ForeignCurrencyAccount] = {}
        self._unknown_lines: list[UnknownLine] = []

    def register_year(self, row_date: date):
        self._years.add(str(row_date.year))

    def add_deposit(self, row: pd.Series):
        deposit = Deposit(row["Date"],
                          Money(row["Amount"], row["CurrencyPrimary"]),
                          row["ActivityDescription"])
        self._deposits.append(deposit)

    def add_interest(self, row: pd.Series):
        interest = Interest(row["Date"],
                            Money(row["Amount"], row["CurrencyPrimary"]),
                            row["ActivityDescription"])
        self._interests.append(interest)
        self.add_foreign_currency_flow(row, False)

    def add_other_fee(self, row: pd.Series):
        other_fee = OtherFee(row["Date"],
                             Money(row["Amount"], row["CurrencyPrimary"]),
                             row["ActivityDescription"])
        self._other_fees.append(other_fee)

    def add_dividend(self, row: pd.Series):
        dividend = Dividend(row["Date"],
                            row["ReportDate"],
                            Money(row["Amount"], row["CurrencyPrimary"]),
                            row["ActivityDescription"],
                            row["ActionID"],
                            row["ActivityCode"] == "FRTAX",
                            row["Date"].year != row["ReportDate"].year)
        self._dividends.append(dividend)
        self.add_foreign_currency_flow(row, False)

    def _process_treasury_bill(self, row: pd.Series):
        symbol = row["Symbol"]
        depot_position = next((p for p in self._treasury_bills if p.symbol == symbol and not p.closed), None)
        if depot_position is None:
            return
        # Maturity record does not include quantity, so we copy it from amount with 1 quantity = 1 USD
        maturity_transaction = Transaction(
            None,
            row["Date"],
            row["ActivityDescription"],
            None,
            OpenCloseIndicator.CLOSE,
            -row["Amount_orig"],
            Money(row["Amount"], row["CurrencyPrimary"]),
            Money(row["Amount_orig"], row["CurrencyPrimary_orig"]),
            row["FXRateToBase_orig"]
        )
        depot_position.add_transaction(maturity_transaction)
        self.add_foreign_currency_flow(row, True)

    def add_foreign_currency_flow(self, row: pd.Series, taxable: bool):
        foreign_currency_code = row["CurrencyPrimary_orig"]
        if not foreign_currency_code or pd.isna(foreign_currency_code):
            return

        foreign_currency_account = self._foreign_currency_accounts.get(foreign_currency_code, None)
        if foreign_currency_account is None:
            foreign_currency_account = ForeignCurrencyAccount(foreign_currency_code)
            self._foreign_currency_accounts[foreign_currency_code] = foreign_currency_account

        amount_orig = Money(row["Amount_orig"].quantize(Decimal("1.00")), row["CurrencyPrimary_orig"])
        foreign_currency_account.add_transaction(Transaction(
            row["TradeID"],
            row["Date"],
            row["ActivityDescription"],
            BuySell.BUY if amount_orig.amount >= 0 else BuySell.SELL,
            OpenCloseIndicator.OPEN if amount_orig.amount >= 0 else OpenCloseIndicator.CLOSE,
            amount_orig.amount,
            Money(row["Amount"].quantize(Decimal("1.00")), row["CurrencyPrimary"]).copy_sign(amount_orig),
            amount_orig,
            row["FXRateToBase_orig"],
            AcquisitionType.GENUINE if taxable else AcquisitionType.NON_GENUINE
        ))

    def add_forex(self, row: pd.Series):
        forex = Forex(row["TradeID"],
                      row["Date"],
                      row["ActivityDescription"],
                      Money(row["Amount"], row["CurrencyPrimary"]),
                      Money(row["Amount_orig"].quantize(Decimal("1.00")), row["CurrencyPrimary_orig"]))
        self._forexes.append(forex)
        self.add_foreign_currency_flow(row, True)

    def add_unknown_line(self, row: pd.Series):
        unknown_line = UnknownLine(row["Date"],
                                   Money(row["Amount"], row["CurrencyPrimary"]),
                                   row["ActivityDescription"])
        self._unknown_lines.append(unknown_line)

    def get_years(self) -> list[str]:
        years = sorted(self._years, reverse=True)
        return years

    def has_data(self) -> bool:
        return bool(self._years)

    def get_deposits(self, year: int) -> Result:
        df = pd.DataFrame(columns=["date", "activity", "amount"],
                          data=((x.date, x.activity, round(x.amount.amount, 2))
                                for x in self._deposits
                                if x.date.year == year))
        df.insert(0, "sequence", pd.Series(range(1, len(df)+1)))
        result = Result(year, df)
        return result

    def get_other_fees(self, year: int) -> Result:
        df = pd.DataFrame(columns=["date", "activity", "amount"],
                          data=((x.date, x.activity, round(x.amount.amount, 2))
                                for x in self._other_fees
                                if x.date.year == year))
        df.insert(0, "sequence", pd.Series(range(1, len(df)+1)))
        result = Result(year, df)
        return result

    def get_interests(self, year: int) -> Result:
        df = pd.DataFrame(columns=["date", "activity", "amount"],
                          data=((x.date, x.activity, round(x.amount.amount, 2))
                                for x in self._interests
                                if x.date.year == year))
        df.insert(0, "sequence", pd.Series(range(1, len(df)+1)))
        result = Result(year, df)
        return result

    def get_options(self, year: int, depot_position_type: DepotPositionType) -> Result:

        def amount_or_zero(amount: Money | None):
            return amount.amount if amount else Decimal("0.00")

        def option_line(transactions: Iterable[TransactionCollection]):
            for transaction_no, transaction in enumerate(transactions, 1):
                for opening_transaction in transaction.get_opening_transactions():
                    yield (transaction_no,
                           opening_transaction.date,
                           opening_transaction.activity,
                           opening_transaction.trade_id,
                           opening_transaction.quantity,
                           round(opening_transaction.amount.amount, 2),
                           None)
                closing_transaction = transaction.get_closing_transaction()
                yield (transaction_no,
                       closing_transaction.date,
                       closing_transaction.activity,
                       closing_transaction.trade_id,
                       closing_transaction.quantity,
                       round(amount_or_zero(closing_transaction.amount), 2),
                       round(transaction.profit().amount, 2))

        transaction_collections = (collection
                                   for option in self._options
                                   if option.position_type() == depot_position_type
                                   for collection in option.transaction_collections(year))
        df = pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount", "profit"],
                          data=option_line(transaction_collections))
        result = Result(year, df)
        return result

    def get_all_stocks(self, year: int):

        def stock_line(transactions: Iterable[Transaction]):
            for transaction_no, transaction in enumerate(transactions, 1):
                yield (transaction_no,
                       transaction.date,
                       transaction.activity,
                       transaction.trade_id,
                       transaction.quantity,
                       round(transaction.amount.amount, 2))

        transactions = (transaction
                        for stock in self._stocks
                        for transaction in stock.transactions
                        if transaction.date.year == year)
        return pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount"],
                            data=stock_line(transactions))

    def get_stocks(self, year: int, depot_position_type: DepotPositionType) -> Result:

        def stock_line(transactions: Iterable[TransactionCollection]):
            for transaction_no, transaction in enumerate(transactions, 1):
                for opening_transaction in transaction.get_opening_transactions():
                    yield (transaction_no,
                           opening_transaction.date,
                           opening_transaction.activity,
                           opening_transaction.trade_id,
                           opening_transaction.quantity,
                           round(opening_transaction.amount.amount, 2),
                           None)
                closing_transaction = transaction.get_closing_transaction()
                yield (transaction_no,
                       closing_transaction.date,
                       closing_transaction.activity,
                       closing_transaction.trade_id,
                       closing_transaction.quantity,
                       round(closing_transaction.amount.amount, 2),
                       round(transaction.profit().amount, 2))

        transaction_collections = (collection
                                   for stock in self._stocks
                                   if stock.position_type() == depot_position_type
                                   for collection in stock.transaction_collections(year))
        df = pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount", "profit"],
                          data=stock_line(transaction_collections))
        result = Result(year, df)
        return result

    def get_all_treasury_bills(self, year: int):

        def tbill_line(transactions: Iterable[Transaction]):
            for transaction_no, transaction in enumerate(transactions, 1):
                yield (transaction_no,
                       transaction.date,
                       transaction.activity,
                       transaction.trade_id,
                       transaction.quantity,
                       round(transaction.amount.amount, 2))

        transactions = (transaction
                        for t_bill in self._treasury_bills
                        for transaction in t_bill.transactions
                        if transaction.date.year == year)
        return pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount"],
                            data=tbill_line(transactions))

    def get_treasury_bills(self, year: int) -> Result:

        def tbill_line(transactions: Iterable[TransactionCollection]):
            for transaction_no, transaction in enumerate(transactions, 1):
                for opening_transaction in transaction.get_opening_transactions():
                    yield (transaction_no,
                           opening_transaction.date,
                           opening_transaction.activity,
                           opening_transaction.trade_id,
                           opening_transaction.quantity,
                           round(opening_transaction.amount.amount, 2),
                           None)
                closing_transaction = transaction.get_closing_transaction()
                yield (transaction_no,
                       closing_transaction.date,
                       closing_transaction.activity,
                       closing_transaction.trade_id,
                       closing_transaction.quantity,
                       round(closing_transaction.amount.amount, 2),
                       round(transaction.profit().amount, 2))

        transaction_collections = (collection
                                   for t_bill in self._treasury_bills
                                   for collection in t_bill.transaction_collections(year))
        df = pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount", "profit"],
                          data=tbill_line(transaction_collections))
        result = Result(year, df)
        return result

    def get_dividends(self, year: int) -> Result:

        def dividend_line(all_dividends: Iterable[Dividend]):
            all_dividends_by_date_action_id = sorted(all_dividends, key=lambda d: f'{d.date.isoformat()}/{d.action_id}')
            for sequence, (action_id, dividends) in enumerate(groupby(all_dividends_by_date_action_id,
                                                                      lambda d: d.action_id), 1):
                for dividend in dividends:
                    yield (sequence,
                           dividend.date,
                           dividend.report_date,
                           dividend.activity,
                           round(dividend.amount.amount, 2) if not dividend.is_tax else None,
                           round(dividend.amount.amount, 2) if dividend.is_tax else None,
                           dividend.is_correction)

        dividends_in_year = (x
                             for x in self._dividends
                             if x.date.year == year)
        df = pd.DataFrame(columns=["sequence", "date", "report_date", "activity", "amount", "tax", "correction"],
                          data=dividend_line(dividends_in_year))
        result = Result(year, df)
        return result

    def get_forexes(self, year: int) -> Result:
        df = pd.DataFrame(columns=["date", "activity", "amount"],
                          data=((x.date, x.activity, round(x.amount.amount, 2))
                                for x in self._forexes
                                if x.date.year == year))
        df.insert(0, "sequence", pd.Series(range(1, len(df)+1)))
        result = Result(year, df)
        return result

    def get_foreign_currencies(self, year: int, interest_bearing_account: bool):

        def currency_line(transactions: Iterable[TransactionCollection]):
            for transaction_no, transaction in enumerate(transactions, 1):
                profit = -transaction.profit()
                for opening_txn_no, opening_transaction in enumerate(transaction.get_opening_transactions()):
                    if opening_txn_no == 0:
                        title = "Zugang" if len(transaction.get_opening_transactions()) == 1 else "Zugänge"
                    else:
                        title = ""
                    yield (transaction_no,
                           title,
                           opening_transaction.date,
                           opening_transaction.activity,
                           opening_transaction.trade_id,
                           opening_transaction.acquisition == AcquisitionType.GENUINE or interest_bearing_account,
                           round(opening_transaction.amount_orig.amount, 2),
                           opening_transaction.fx_rate,
                           round(opening_transaction.amount.amount, 2),
                           None)
                closing_transaction = transaction.get_closing_transaction()
                yield (transaction_no,
                       "Abgang",
                       closing_transaction.date,
                       closing_transaction.activity,
                       closing_transaction.trade_id,
                       closing_transaction.acquisition == AcquisitionType.GENUINE or interest_bearing_account,
                       round(closing_transaction.amount_orig.amount, 2),
                       closing_transaction.fx_rate,
                       round(closing_transaction.amount.amount, 2),
                       round(profit.amount, 2))

        result: dict[str, Result] = {}
        for currency in sorted(self._foreign_currency_accounts.keys()):
            account = self._foreign_currency_accounts[currency]
            transaction_pairs = account.transaction_pairs(year)
            if not interest_bearing_account:
                transaction_pairs = apply_estg_23(transaction_pairs)
            df = pd.DataFrame(columns=["sequence",
                                       "foreign_currency",
                                       "date",
                                       "activity",
                                       "trade_id",
                                       "tax_relevant",
                                       currency,
                                       "fx_rate",
                                       "EUR",
                                       "profit"],
                              data=currency_line(transaction_pairs))

            if not df.empty:
                result[currency] = Result(year, df)

        return result

    def get_unknown_lines(self, year: int) -> Result:
        df = pd.DataFrame(columns=["date", "activity", "amount"],
                          data=((x.date, x.activity, round(x.amount.amount, 2))
                                for x in self._unknown_lines
                                if x.date.year == year))
        df.insert(0, "sequence", pd.Series(range(1, len(df)+1)))
        result = Result(year, df)
        return result

    def process_statement(self, row: pd.Series):
        self.register_year(row["Date"])
        match row["ActivityCode"]:
            case "DEP" | "WITH":
                self.add_deposit(row)

            case "SELL" | "BUY" | "ASSIGN" | "EXE":
                # Processed in process_trade(), registering the foreign currency only
                match row["AssetClass"]:
                    case "BILL":
                        self.add_foreign_currency_flow(row, True)
                    case "OPT":
                        self.add_foreign_currency_flow(row, False)
                    case "STK":
                        self.add_foreign_currency_flow(row, True)

            case "DIV" | "PIL" | "FRTAX":
                self.add_dividend(row)

            case "FOREX":
                self.add_forex(row)

            case "OFEE" | "STAX":
                self.add_other_fee(row)

            case "CINT" | "DINT":
                self.add_interest(row)

            case "CORP":
                self._process_treasury_bill(row)

            case _:
                self.add_unknown_line(row)

    def _find_stock_position(self, symbol: str, asset_class: str) -> Stock | None:
        depot_position = next((stock
                               for stock in self._stocks
                               if stock.symbol == symbol and not stock.closed),
                              None)
        if depot_position is None:
            new_stock = Stock(symbol, asset_class)
            self._stocks.append(new_stock)
            depot_position = new_stock

        return depot_position

    def _find_option_position(self, symbol: str, asset_class: str) -> Option | None:
        depot_position = next((option
                               for option in self._options
                               if option.symbol == symbol and not option.closed),
                              None)
        if depot_position is None:
            new_option = Option(symbol, asset_class)
            self._options.append(new_option)
            depot_position = new_option

        return depot_position

    def _find_treasury_bill_position(self, symbol: str, asset_class: str) -> TreasuryBill | None:
        depot_position = next((t_bill
                               for t_bill in self._treasury_bills
                               if t_bill.symbol == symbol and not t_bill.closed),
                              None)
        if depot_position is None:
            new_t_bill = TreasuryBill(symbol, asset_class)
            self._treasury_bills.append(new_t_bill)
            depot_position = new_t_bill

        return depot_position

    def process_trade(self, row: pd.Series):
        self.register_year(row["TradeDate"])
        asset_class = row["AssetClass"]
        if asset_class not in ["STK", "OPT", "BILL", "CASH"]:
            raise NotImplementedError()
        symbol = row["Symbol"]
        trade_id = row["TradeID"]
        buy_sell = row["Buy/Sell"]

        depot_position: DepotPosition | None = None
        match asset_class:
            case "STK":
                depot_position = self._find_stock_position(symbol, asset_class)

            case "OPT":
                depot_position = self._find_option_position(symbol, asset_class)

            case "BILL":
                depot_position = self._find_treasury_bill_position(symbol, asset_class)

            case "CASH":
                # Handle cash trades in process_statement()
                return

        if pd.isna(row["Amount"]):
            # Trade without corresponding entry in statement of funds => Trade without moving any money,
            # e.g. a worthless expired option
            depot_position.add_transaction(Transaction(
                trade_id,
                row["TradeDate"],
                None,
                BuySell(buy_sell),
                OpenCloseIndicator(row["Open/CloseIndicator"]),
                row["Quantity"],
                None,
                None,
                None
            ))
        else:
            depot_position.add_transaction(Transaction(
                row["TradeID"],
                row["Date"],
                row["ActivityDescription"],
                BuySell(row["Buy/Sell"]),
                OpenCloseIndicator(row["Open/CloseIndicator"]),
                row["TradeQuantity"],
                Money(row["Amount"], row["CurrencyPrimary"]),
                Money(row["Amount_orig"], row["CurrencyPrimary_orig"]),
                row["FXRateToBase_orig"]
            ))
