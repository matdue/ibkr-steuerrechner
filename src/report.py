from datetime import date
from decimal import Decimal
from itertools import groupby
from typing import Iterable, Tuple

import pandas as pd

from deposit import Deposit
from dividend import Dividend
from foreign_currency_bucket import ForeignCurrencyBucket, ForeignCurrencyFlow, TaxRelevance
from forex import Forex
from interest import Interest
from money import Money
from options import OptionTransaction, OptionTrade, OptionType
from other_fee import OtherFee
from stock import StockTrade, StockTransaction, StockType, ReturnTransaction
from treasury_bill import TreasuryBillTrade, TreasuryBillTransaction
from unknown_line import UnknownLine
from utils import lookahead


class Report:
    def __init__(self):
        self._years: set[str] = set()
        self._deposits: list[Deposit] = []
        self._interests: list[Interest] = []
        self._other_fees: list[OtherFee] = []
        self._dividends: list[Dividend] = []
        self._option_trades: list[OptionTrade] = []
        self._stock_trades: list[StockTrade] = []
        self._treasury_bill_trades: list[TreasuryBillTrade] = []
        self._forexes: list[Forex] = []
        self._foreign_currency_buckets: dict[str, ForeignCurrencyBucket] = {}
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

    def add_option_trade(self, row: pd.Series):
        transaction = OptionTransaction(row["TradeID"],
                                        row["Date"],
                                        row["ActivityDescription"],
                                        row["Buy/Sell"],
                                        row["TradeQuantity"],
                                        Money(row["Amount"], row["CurrencyPrimary"]),
                                        Money(row["Amount_orig"], row["CurrencyPrimary_orig"]))
        symbol = row["Symbol"]
        open_trade = next((trade
                           for trade in self._option_trades
                           if not trade.closed and trade.symbol == symbol), None)
        if open_trade is None:
            new_trade = OptionTrade(symbol,
                                    row["Description"],
                                    row["Expiry"],
                                    [transaction])
            self._option_trades.append(new_trade)
        else:
            remaining = open_trade.add_transaction(transaction)
            if remaining is not None:
                new_trade = OptionTrade(symbol,
                                        row["Description"],
                                        row["Expiry"],
                                        [remaining])
                self._option_trades.append(new_trade)

        self.add_foreign_currency_flow(row, False)

    def add_stock_trade(self, row: pd.Series):
        transaction = StockTransaction(row["TradeID"],
                                       row["Date"],
                                       row["ActivityDescription"],
                                       row["Buy/Sell"],
                                       row["TradeQuantity"],
                                       Money(row["Amount"], row["CurrencyPrimary"]),
                                       Money(row["Amount_orig"], row["CurrencyPrimary_orig"]))
        symbol = row["Symbol"]
        open_trade = next((trade
                           for trade in self._stock_trades
                           if not trade.closed and trade.symbol == symbol), None)
        if open_trade is None:
            new_trade = StockTrade(symbol,
                                   row["Description"],
                                   [transaction])
            self._stock_trades.append(new_trade)
        else:
            remaining = open_trade.add_transaction(transaction)
            if remaining is not None:
                new_trade = StockTrade(symbol,
                                       row["Description"],
                                       [remaining])
                self._stock_trades.append(new_trade)

        self.add_foreign_currency_flow(row, True)

    def add_treasury_bill_trade(self, row: pd.Series):
        transaction = TreasuryBillTransaction(row["TradeID"],
                                              row["Date"],
                                              row["ActivityDescription"],
                                              row["Buy/Sell"],
                                              row["TradeQuantity"],
                                              Money(row["Amount"], row["CurrencyPrimary"]),
                                              Money(row["Amount_orig"], row["CurrencyPrimary_orig"]))
        if row["ActivityCode"] == "CORP":
            # Maturity record does not include quantity, so we copy it from amount as 1 quantity = 1 USD
            transaction.quantity = -row["Amount_orig"]

        symbol = row["Symbol"]
        open_trade = next((trade
                           for trade in self._treasury_bill_trades
                           if not trade.closed and trade.symbol == symbol), None)
        if open_trade is None:
            new_trade = TreasuryBillTrade(symbol,
                                          row["Description"],
                                          [transaction])
            self._treasury_bill_trades.append(new_trade)
        else:
            remaining = open_trade.add_transaction(transaction)
            if remaining is not None:
                new_trade = TreasuryBillTrade(symbol,
                                              row["Description"],
                                              [remaining])
                self._treasury_bill_trades.append(new_trade)

        self.add_foreign_currency_flow(row, True)

    def add_foreign_currency_flow(self, row: pd.Series, taxable: bool):
        foreign_currency_code = row["CurrencyPrimary_orig"]
        if not foreign_currency_code:
            return

        foreign_currency_bucket = self._foreign_currency_buckets.get(foreign_currency_code, None)
        if foreign_currency_bucket is None:
            foreign_currency_bucket = ForeignCurrencyBucket(foreign_currency_code)
            self._foreign_currency_buckets[foreign_currency_code] = foreign_currency_bucket

        foreign_currency_flow = ForeignCurrencyFlow(
            row["TradeID"],
            row["Date"],
            row["ActivityDescription"],
            Money(row["Amount"], row["CurrencyPrimary"]),
            Money(row["Amount_orig"].quantize(Decimal("1.00")), row["CurrencyPrimary_orig"]),
            row["FXRateToBase_orig"],
            TaxRelevance.TAX_RELEVANT if taxable else TaxRelevance.TAX_IRRELEVANT
        )
        foreign_currency_bucket.add(foreign_currency_flow)

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

    def close_expired_options(self, reporting_date: date):
        for trade in self._option_trades:
            if trade.closed:
                continue
            if trade.expiry > reporting_date:
                continue
            trade.close()

    def finish(self, reporting_date: date):
        self.close_expired_options(reporting_date)
        for foreign_currency_bucket in self._foreign_currency_buckets.values():
            returns, unconsumed_returns, unconsumed_accruals = foreign_currency_bucket.calculate_returns()
            for currency_return in returns:
                profit = currency_return.calculate_taxable_profit(reporting_date)

    def get_years(self) -> list[str]:
        years = sorted(self._years)
        return years

    def get_deposits(self, year: str):
        year_int = int(year)
        return pd.DataFrame(columns=["date", "activity", "amount"],
                            data=((x.date, x.activity, float(x.amount))
                                  for x in self._deposits
                                  if x.date.year == year_int))

    def get_other_fees(self, year: str):
        year_int = int(year)
        return pd.DataFrame(columns=["date", "activity", "amount"],
                            data=((x.date, x.activity, float(x.amount))
                                  for x in self._other_fees
                                  if x.date.year == year_int))

    def get_interests(self, year: str):
        year_int = int(year)
        return pd.DataFrame(columns=["date", "activity", "amount"],
                            data=((x.date, x.activity, float(x.amount))
                                  for x in self._interests
                                  if x.date.year == year_int))

    def get_options(self, year: str, option_type: OptionType):
        year_int = int(year)

        def option_line(trades: Iterable[Tuple[OptionTrade, OptionTrade.Profit]]):
            for trade_no, trade_profit in enumerate(trades):
                trade, profit = trade_profit
                for transaction_no, transaction_has_more in enumerate(lookahead(profit.transactions)):
                    transaction, has_more = transaction_has_more
                    line_no = f"{trade_no+1}.{transaction_no+1}"
                    if transaction_no == 0:
                        yield (trade_no,
                               line_no,
                               transaction.date,
                               trade.description,
                               trade.expiry,
                               trade.closed,
                               transaction.activity,
                               transaction.tradeId,
                               float(transaction.quantity),
                               float(transaction.amount.amount),
                               None if has_more else float(profit.total.amount))  # Write total into last line
                    else:
                        yield (trade_no,
                               line_no,
                               transaction.date,
                               None,
                               None,
                               None,
                               transaction.activity,
                               transaction.tradeId,
                               float(transaction.quantity),
                               float(transaction.amount.amount),
                               None if has_more else float(profit.total.amount))  # Write total into last line

        trades_with_profit = ((trade, profit_of_year)
                              for trade in self._option_trades
                              if trade.option_type() == option_type
                              for profit_of_year in [trade.calculate_profit_per_year().get(year_int)]
                              if profit_of_year is not None)
        return pd.DataFrame(columns=["sequence", "no", "date", "description", "expiry", "closed",
                                     "activity", "trade_id", "quantity", "amount", "profit"],
                            data=option_line(trades_with_profit))

    def get_all_stocks(self, year: str):
        year_int = int(year)

        def stock_line(transactions: Iterable[StockTransaction]):
            for transaction_no, transaction in enumerate(transactions):
                yield (transaction_no,
                       transaction.date,
                       transaction.activity,
                       transaction.tradeId,
                       transaction.quantity,
                       float(transaction.amount.amount))

        transactions_with_profit = (transaction
                                    for trade in self._stock_trades
                                    for transaction in trade.transactions
                                    if transaction.date.year == year_int)
        return pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount"],
                            data=stock_line(transactions_with_profit))

    def get_stocks(self, year: str):
        year_int = int(year)

        def stock_line(transactions: Iterable[ReturnTransaction]):
            for transaction_no, return_transaction in enumerate(transactions):
                profit = return_transaction.calculate_profit()
                for accrual in profit.accruals:
                    yield (transaction_no,
                           accrual.transaction.date,
                           accrual.transaction.activity,
                           accrual.transaction.tradeId,
                           accrual.consumed_quantity,
                           accrual.consumed_amount().amount,
                           None)
                yield (transaction_no,
                       return_transaction.transaction.date,
                       return_transaction.transaction.activity,
                       return_transaction.transaction.tradeId,
                       return_transaction.transaction.quantity,
                       return_transaction.transaction.amount.amount,
                       profit.profit_base.amount)

        return_transactions = (return_transaction
                               for trade in self._stock_trades
                               if trade.stock_type() == StockType.LONG  # Ignore short trades as they are not supported
                               for return_transaction in trade.calculate_returns()[0]
                               if return_transaction.transaction.date.year == year_int)
        return pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount", "profit"],
                            data=stock_line(return_transactions))

    def get_all_treasury_bills(self, year: str):
        year_int = int(year)

        def stock_line(transactions: Iterable[TreasuryBillTransaction]):
            for transaction_no, transaction in enumerate(transactions):
                yield (transaction_no,
                       transaction.date,
                       transaction.activity,
                       transaction.tradeId,
                       transaction.quantity,
                       float(transaction.amount.amount))

        transactions_with_profit = (transaction
                                    for trade in self._treasury_bill_trades
                                    for transaction in trade.transactions
                                    if transaction.date.year == year_int)
        return pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount"],
                            data=stock_line(transactions_with_profit))

    def get_treasury_bills(self, year: str):
        year_int = int(year)

        def stock_line(transactions: Iterable[ReturnTransaction]):
            for transaction_no, return_transaction in enumerate(transactions):
                profit = return_transaction.calculate_profit()
                for accrual in profit.accruals:
                    yield (transaction_no,
                           accrual.transaction.date,
                           accrual.transaction.activity,
                           accrual.transaction.tradeId,
                           accrual.consumed_quantity,
                           accrual.consumed_amount().amount,
                           None)
                yield (transaction_no,
                       return_transaction.transaction.date,
                       return_transaction.transaction.activity,
                       return_transaction.transaction.tradeId,
                       return_transaction.transaction.quantity,
                       return_transaction.transaction.amount.amount,
                       profit.profit_base.amount)

        return_transactions = (return_transaction
                               for trade in self._treasury_bill_trades
                               for return_transaction in trade.calculate_returns()[0]
                               if return_transaction.transaction.date.year == year_int)
        return pd.DataFrame(columns=["sequence", "date", "activity", "trade_id", "quantity", "amount", "profit"],
                            data=stock_line(return_transactions))

    def get_dividends(self, year: str):
        year_int = int(year)

        def dividend_line(all_dividends: Iterable[Dividend]):
            all_dividends_by_date_action_id = sorted(all_dividends, key=lambda d: f'{d.date.isoformat()}/{d.action_id}')
            for action_no, (action_id, dividends) in enumerate(groupby(all_dividends_by_date_action_id,
                                                                       lambda d: d.action_id)):
                for dividend_no, dividend in enumerate(dividends):
                    line_no = f"{action_no+1}.{dividend_no+1}"
                    yield (action_no,
                           line_no,
                           dividend.date,
                           dividend.report_date,
                           dividend.activity,
                           float(dividend.amount.amount) if not dividend.is_tax else None,
                           float(dividend.amount.amount) if dividend.is_tax else None,
                           dividend.is_correction)

        dividends_in_year = (x
                             for x in self._dividends
                             if x.date.year == year_int)
        return pd.DataFrame(columns=["sequence", "no", "date", "report_date", "activity", "amount", "tax",
                                     "correction"],
                            data=dividend_line(dividends_in_year))

    def get_forexes(self, year: str):
        year_int = int(year)
        return pd.DataFrame(columns=["date", "activity", "amount"],
                            data=((x.date, x.activity, float(x.amount))
                                  for x in self._forexes
                                  if x.date.year == year_int))

    def get_foreign_currencies(self, year: str):
        year_int = int(year)
        reporting_date = date(year_int + 1, 1, 1)
        result: dict[str, pd.DataFrame] = {}
        for currency in sorted(self._foreign_currency_buckets.keys()):
            bucket = self._foreign_currency_buckets[currency]
            returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()
            returns_in_year = (x for x in returns if x.flow.date.year == year_int)

            df = pd.DataFrame(columns=["sequence",
                                       "Fremdwährung",
                                       "TradeID",
                                       "date",
                                       "Aktivität",
                                       "Ergebnisrelevant",
                                       f"{currency} (gesamt)",
                                       f"{currency} (verbraucht)",
                                       f"{currency} (ergebnisrelevant)",
                                       "Devisenkurs",
                                       "EUR (ergebnisrelevant)",
                                       "profit"])
            for return_no, return_flow in enumerate(returns_in_year):
                profit = return_flow.calculate_taxable_profit(reporting_date)
                rows = [
                    [return_no,
                     "Abgang",
                     return_flow.flow.tradeId,
                     return_flow.flow.date,
                     return_flow.flow.description,
                     return_flow.flow.is_tax_relevant(reporting_date),
                     return_flow.flow.amount_orig.amount,
                     return_flow.consumed().amount * return_flow.flow.amount_orig.sign(),
                     profit.tax_relevant_orig.amount * return_flow.flow.amount_orig.sign(),
                     return_flow.flow.fx_rate,
                     profit.tax_relevant_base.amount.quantize(Decimal("1.00")) * return_flow.flow.amount_orig.sign(),
                     None]
                ]
                for consumed in profit.accruals:
                    rows.append([return_no,
                                 "Zugang",
                                 consumed.flow.tradeId,
                                 consumed.flow.date,
                                 consumed.flow.description,
                                 consumed.flow.is_tax_relevant(reporting_date),
                                 consumed.flow.amount_orig.amount,
                                 consumed.consumed().amount,
                                 consumed.consumed_tax_relevant(reporting_date).amount,
                                 consumed.flow.fx_rate,
                                 consumed.consumed_base_tax_relevant(reporting_date).amount.quantize(Decimal("1.00")),
                                 None])
                rows.append([return_no,
                             None,
                             None,
                             None,
                             None,
                             None,
                             None,
                             None,
                             None,
                             None,
                             None,
                             profit.profit_base.amount.quantize(Decimal("1.00"))])

                df_return = pd.DataFrame(rows, columns=df.columns)
                df = pd.concat([df, df_return], ignore_index=True)

            if not df.empty:
                result[currency] = df

        return result

    def get_unknown_lines(self, year: str):
        year_int = int(year)
        return pd.DataFrame(columns=["date", "activity", "amount"],
                            data=((x.date, x.activity, float(x.amount))
                                  for x in self._unknown_lines
                                  if x.date.year == year_int))


    def process(self, row: pd.Series):
        self.register_year(row["Date"])
        match row["ActivityCode"]:
            case "DEP" | "WITH":
                self.add_deposit(row)

            case "SELL" | "BUY" | "ASSIGN":
                match row["AssetClass"]:
                    case "BILL":
                        self.add_treasury_bill_trade(row)
                    case "OPT":
                        self.add_option_trade(row)
                    case "STK":
                        self.add_stock_trade(row)
                    case _:
                        self.add_unknown_line(row)

            case "DIV" | "PIL" | "FRTAX":
                self.add_dividend(row)

            case "FOREX":
                self.add_forex(row)

            case "OFEE" | "STAX":
                self.add_other_fee(row)

            case "CINT" | "DINT":
                self.add_interest(row)

            case "CORP":
                self.add_treasury_bill_trade(row)

            case _:
                self.add_unknown_line(row)
