import dataclasses
import operator
from collections import deque
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum, auto
from functools import reduce
from typing import Self, Deque

from dateutil import relativedelta

from ibkr_steuerrechner.money import Money


class TaxRelevance(Enum):
    TAX_RELEVANT = auto()
    TAX_IRRELEVANT = auto()


@dataclass
class ForeignCurrencyFlow:
    tradeId: str
    date: date
    description: str
    amount_base: Money  # Amount in base currency (EUR)
    amount_orig: Money  # Amount in original (foreign) currency, e.g. USD
    fx_rate: Decimal    # FX rate to base, i.e. amount_orig * fx_rate = amount_base
    tax_relevance: TaxRelevance

    def is_tax_relevant(self, reporting_date: date):
        # Transaction is tax-relevant if within speculative period (of 10 years with accounts paying interests)
        return (self.tax_relevance == TaxRelevance.TAX_RELEVANT and
                (self.date + relativedelta.relativedelta(years=+10) > reporting_date))


@dataclass
class AccrualFlow:
    flow: ForeignCurrencyFlow
    consumed_orig: Money = field(init=False)  # Amount which has been netted with a return flow

    def __post_init__(self):
        self.consumed_orig = self.flow.amount_orig.as_zero()

    def consumed(self) -> Money:
        return self.consumed_orig

    def consumed_tax_relevant(self, reporting_date: date):
        return self.consumed() if self.flow.is_tax_relevant(reporting_date) else self.consumed().as_zero()

    def consumed_base_tax_relevant(self, reporting_date: date):
        if self.flow.is_tax_relevant(reporting_date):
            return self.flow.amount_base.with_value_keep_precision(self.consumed().amount * self.flow.fx_rate)
        else:
            return self.flow.amount_base.as_zero()

    def unconsumed(self) -> Money:
        return self.flow.amount_orig - self.consumed()

    def is_consumed(self) -> bool:
        return self.consumed() == self.flow.amount_orig

    def consume(self, amount: Money) -> Self:
        self.consumed_orig += amount.copy_sign(self.flow.amount_orig)
        return self


@dataclass
class ReturnFlow:
    flow: ForeignCurrencyFlow
    consumed_from: list[AccrualFlow] = field(default_factory=list)  # Return flow has been netted with these accruals

    def consumed(self) -> Money:
        sum_accruals = reduce(operator.add,
                              (accrual.consumed_orig for accrual in self.consumed_from),
                              self.flow.amount_orig.as_zero())
        return sum_accruals

    def unconsumed(self) -> Money:
        # Beware: ReturnFlow is always negative, Accruals always positive.
        return self.flow.amount_orig + self.consumed()

    def is_consumed(self) -> bool:
        return self.flow.amount_orig + self.consumed() == self.flow.amount_orig.as_zero()

    def consume(self, accrual: ForeignCurrencyFlow, amount: Money):
        accrual_flow = AccrualFlow(accrual).consume(amount)
        self.consumed_from.append(accrual_flow)

    @dataclass
    class Profit:
        profit_base: Money
        tax_relevant_base: Money
        tax_relevant_orig: Money
        accruals: list[AccrualFlow]

    def calculate_taxable_profit(self, reporting_date: date):
        return_is_tax_relevant = self.flow.is_tax_relevant(reporting_date)

        # Sum up all tax-relevant accruals only
        # The sum of accruals.amount_orig may be lower than self.flow.amount_orig
        # as some, probably all, accruals are not tax-relevant.
        consumed_amount_orig = self.flow.amount_orig.as_zero()
        consumed_amount_base = self.flow.amount_base.as_zero()
        taxable_consumed_from = (accrual
                                 for accrual in self.consumed_from
                                 if (accrual.flow.is_tax_relevant(reporting_date)) and return_is_tax_relevant)
        for accrual in taxable_consumed_from:
            consumed_amount_orig += accrual.consumed_orig
            consumed_amount_base += accrual.flow.amount_base.with_value_keep_precision(accrual.consumed_orig.amount *
                                                                                       accrual.flow.fx_rate)

        taxable_amount_base: Money = self.flow.amount_base.with_value_keep_precision(consumed_amount_orig.amount *
                                                                                     self.flow.fx_rate)

        # Example: 10 USD, equivalent to 9 EUR, have been added,
        # i.e. consumed_amount_orig = 10 USD and consumed_amount_base = 9 EUR.
        # Later, the fx rate changes. 10 USD, equivalent to 8 EUR, will leave, i.e. 10 USD / 8 EUR,
        # i.e. taxable_amount_base = 8 EUR
        profit_base = taxable_amount_base - consumed_amount_base
        accruals_copy = [accrual
                         if return_is_tax_relevant
                         else (AccrualFlow(dataclasses.replace(accrual.flow, tax_relevance=TaxRelevance.TAX_IRRELEVANT))
                               .consume(accrual.consumed_orig))
                         for accrual in self.consumed_from]
        return ReturnFlow.Profit(profit_base, taxable_amount_base, consumed_amount_orig, accruals_copy)


class ForeignCurrencyBucket:
    currency: str
    flows: list[ForeignCurrencyFlow]

    def __init__(self, currency: str):
        self.currency = currency
        self.flows = []

    def add(self, amount: ForeignCurrencyFlow):
        if amount.amount_orig.currency != self.currency:
            raise ValueError(f"Currency must match: expected {self.currency}, got {amount.amount_orig.currency}")
        self.flows.append(amount)

    def calculate_returns(self):
        unconsumed_accruals: Deque[AccrualFlow] = deque()
        unconsumed_returns: Deque[ReturnFlow] = deque()
        returns: list[ReturnFlow] = list()

        for flow in self.flows:
            if flow.amount_orig.is_non_negative():
                unconsumed_accruals.append(AccrualFlow(flow))
            else:
                unconsumed_returns.append(ReturnFlow(flow))

            if len(unconsumed_returns) == 0 or len(unconsumed_accruals) == 0:
                # Nothing to do if there are no pending returns, or no accruals to net the return
                continue

            return_flow = unconsumed_returns[0]
            while not return_flow.is_consumed() and len(unconsumed_accruals) != 0:
                accrual = unconsumed_accruals[0]
                amount_to_consume = min(abs(return_flow.unconsumed()), abs(accrual.unconsumed()))

                accrual.consume(amount_to_consume)
                return_flow.consume(accrual.flow, amount_to_consume)

                if accrual.is_consumed():
                    unconsumed_accruals.popleft()
                if return_flow.is_consumed():
                    returns.append(unconsumed_returns.popleft())

        return returns, list(unconsumed_returns), list(unconsumed_accruals)
