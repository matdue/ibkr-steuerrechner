import datetime
import unittest
from decimal import Decimal

import pandas as pd

from foreign_currency_bucket import ForeignCurrencyFlow, TaxRelevance, AccrualFlow, ReturnFlow, ForeignCurrencyBucket
from money import Money

today = datetime.date(2024, 12,31)
today_11_years_ago = datetime.date(2013, 12,31)


class ForeignCurrencyFlow2Test(unittest.TestCase):
    def test_if_is_tax_relevant_is_true_if_tax_type_is_tax_relevant(self):
        flow = ForeignCurrencyFlow("tradeId",
                                   today,
                                    "Tax relevant transaction",
                                   Money(Decimal(9), "EUR"),
                                   Money(Decimal(10), "USD"),
                                   fx_rate=Decimal(0.9),
                                   tax_relevance=TaxRelevance.TAX_RELEVANT)
        self.assertTrue(flow.is_tax_relevant(today))

    def test_if_is_tax_relevant_is_false_if_tax_type_is_tax_irrelevant(self):
        flow = ForeignCurrencyFlow("tradeId",
                                   today,
                                    "Tax irrelevant transaction",
                                   Money(Decimal(9), "EUR"),
                                   Money(Decimal(10), "USD"),
                                   fx_rate=Decimal(0.9),
                                   tax_relevance=TaxRelevance.TAX_IRRELEVANT)
        self.assertFalse(flow.is_tax_relevant(today))

    def test_if_is_tax_relevant_is_false_if_speculative_period_has_passed(self):
        flow = ForeignCurrencyFlow("tradeId",
                                   today_11_years_ago,
                                    "Tax relevant transaction",
                                   Money(Decimal(9), "EUR"),
                                   Money(Decimal(10), "USD"),
                                   fx_rate=Decimal(0.9),
                                   tax_relevance=TaxRelevance.TAX_RELEVANT)
        self.assertFalse(flow.is_tax_relevant(today))


class AccrualFlowTest(unittest.TestCase):
    def test_if_initialized_with_0(self):
        accrual = AccrualFlow(ForeignCurrencyFlow("tradeId",
                                                  today,
                                                   "Tax relevant transaction",
                                                  Money(Decimal(9), "EUR"),
                                                  Money(Decimal(10), "USD"),
                                                  fx_rate=Decimal(0.9),
                                                  tax_relevance=TaxRelevance.TAX_RELEVANT))
        self.assertTrue(accrual.consumed_orig.is_zero())

    def test_if_consume_modifies_consumed_orig(self):
        accrual = AccrualFlow(ForeignCurrencyFlow("tradeId",
                                                  today,
                                                   "Tax relevant transaction",
                                                  Money(Decimal(9), "EUR"),
                                                  Money(Decimal(10), "USD"),
                                                  fx_rate=Decimal(0.9),
                                                  tax_relevance=TaxRelevance.TAX_RELEVANT))

        accrual.consume(Money(Decimal(5), "USD"))

        self.assertEqual(Money(Decimal(5), "USD"), accrual.consumed_orig)

    def test_if_consume_copies_sign(self):
        accrual = AccrualFlow(ForeignCurrencyFlow("tradeId",
                                                  today,
                                                   "Tax relevant transaction",
                                                  Money(Decimal(9), "EUR"),
                                                  Money(Decimal(10), "USD"),
                                                  fx_rate=Decimal(0.9),
                                                  tax_relevance=TaxRelevance.TAX_RELEVANT))

        accrual.consume(Money(Decimal(-5), "USD"))

        self.assertEqual(Money(Decimal(5), "USD"), accrual.consumed_orig)

    def test_if_consumed_after_partly_consumption(self):
        accrual = AccrualFlow(ForeignCurrencyFlow("tradeId",
                                                  today,
                                                   "Tax relevant transaction",
                                                  Money(Decimal(9), "EUR"),
                                                  Money(Decimal(10), "USD"),
                                                  fx_rate=Decimal(0.9),
                                                  tax_relevance=TaxRelevance.TAX_RELEVANT))

        accrual.consume(Money(Decimal(4), "USD"))

        self.assertFalse(accrual.is_consumed())
        self.assertEqual(Money(Decimal(4), "USD"), accrual.consumed())
        self.assertEqual(Money(Decimal(6), "USD"), accrual.unconsumed())

    def test_if_consumed_after_complete_consumption(self):
        accrual = AccrualFlow(ForeignCurrencyFlow("tradeId",
                                                  today,
                                                   "Tax relevant transaction",
                                                  Money(Decimal(9), "EUR"),
                                                  Money(Decimal(10), "USD"),
                                                  fx_rate=Decimal(0.9),
                                                  tax_relevance=TaxRelevance.TAX_RELEVANT))

        accrual.consume(Money(Decimal(10), "USD"))

        self.assertTrue(accrual.is_consumed())
        self.assertEqual(Money(Decimal(10), "USD"), accrual.consumed())
        self.assertEqual(Money(Decimal(0), "USD"), accrual.unconsumed())


class ReturnFlowTest(unittest.TestCase):
    def test_if_initialized_with_empty_accruals_list(self):
        return_flow = ReturnFlow(ForeignCurrencyFlow("tradeId",
                                                     today,
                                                      "Tax relevant transaction",
                                                     Money(Decimal(-9), "EUR"),
                                                     Money(Decimal(-10), "USD"),
                                                     fx_rate=Decimal(0.9),
                                                     tax_relevance=TaxRelevance.TAX_RELEVANT))
        self.assertEqual([], return_flow.consumed_from)

    def test_if_consume_modifies_accruals_list(self):
        return_flow = ReturnFlow(ForeignCurrencyFlow("tradeId",
                                                     today,
                                                      "Tax relevant transaction",
                                                     Money(Decimal(-9), "EUR"),
                                                     Money(Decimal(-10), "USD"),
                                                     fx_rate=Decimal(0.9),
                                                     tax_relevance=TaxRelevance.TAX_RELEVANT))
        accrual = ForeignCurrencyFlow("tradeId",
                                      today,
                                       "Tax relevant transaction",
                                      Money(Decimal(9), "EUR"),
                                      Money(Decimal(10), "USD"),
                                      fx_rate=Decimal(0.9),
                                      tax_relevance=TaxRelevance.TAX_RELEVANT)

        return_flow.consume(accrual, Money(Decimal(5), "USD"))

        self.assertEqual(1, len(return_flow.consumed_from))
        self.assertEqual(Money(Decimal(5), "USD"), return_flow.consumed_from[0].consumed_orig)

    def test_if_consume_copies_sign(self):
        return_flow = ReturnFlow(ForeignCurrencyFlow("tradeId",
                                                     today,
                                                      "Tax relevant transaction",
                                                     Money(Decimal(-9), "EUR"),
                                                     Money(Decimal(-10), "USD"),
                                                     fx_rate=Decimal(0.9),
                                                     tax_relevance=TaxRelevance.TAX_RELEVANT))
        accrual = ForeignCurrencyFlow("tradeId",
                                      today,
                                       "Tax relevant transaction",
                                      Money(Decimal(9), "EUR"),
                                      Money(Decimal(10), "USD"),
                                      fx_rate=Decimal(0.9),
                                      tax_relevance=TaxRelevance.TAX_RELEVANT)

        return_flow.consume(accrual, Money(Decimal(-5), "USD"))

        self.assertEqual(Money(Decimal(5), "USD"), return_flow.consumed_from[0].consumed_orig)

    def test_if_consumed_after_partly_consumption(self):
        return_flow = ReturnFlow(ForeignCurrencyFlow("tradeId",
                                                     today,
                                                      "Tax relevant transaction",
                                                     Money(Decimal(-9), "EUR"),
                                                     Money(Decimal(-10), "USD"),
                                                     fx_rate=Decimal(0.9),
                                                     tax_relevance=TaxRelevance.TAX_RELEVANT))
        accrual = ForeignCurrencyFlow("tradeId",
                                      today,
                                       "Tax relevant transaction",
                                      Money(Decimal(9), "EUR"),
                                      Money(Decimal(10), "USD"),
                                      fx_rate=Decimal(0.9),
                                      tax_relevance=TaxRelevance.TAX_RELEVANT)

        return_flow.consume(accrual, Money(Decimal(4), "USD"))

        self.assertFalse(return_flow.is_consumed())
        self.assertEqual(Money(Decimal(4), "USD"), return_flow.consumed())
        self.assertEqual(Money(Decimal(-6), "USD"), return_flow.unconsumed())

    def test_if_consumed_after_complete_consumption(self):
        return_flow = ReturnFlow(ForeignCurrencyFlow("tradeId",
                                                     today,
                                                      "Tax relevant transaction",
                                                     Money(Decimal(-9), "EUR"),
                                                     Money(Decimal(-10), "USD"),
                                                     fx_rate=Decimal(0.9),
                                                     tax_relevance=TaxRelevance.TAX_RELEVANT))
        accrual = ForeignCurrencyFlow("tradeId",
                                      today,
                                       "Tax relevant transaction",
                                      Money(Decimal(9), "EUR"),
                                      Money(Decimal(10), "USD"),
                                      fx_rate=Decimal(0.9),
                                      tax_relevance=TaxRelevance.TAX_RELEVANT)

        return_flow.consume(accrual, Money(Decimal(10), "USD"))

        self.assertTrue(return_flow.is_consumed())
        self.assertEqual(Money(Decimal(10), "USD"), return_flow.consumed())
        self.assertEqual(Money(Decimal(0), "USD"), return_flow.unconsumed())

    def test_calculate_taxable_profit(self):
        return_flow = ReturnFlow(ForeignCurrencyFlow("tradeId",
                                                     today,
                                                      "Tax relevant transaction",
                                                     Money(Decimal(-8), "EUR"),
                                                     Money(Decimal(-10), "USD"),
                                                     fx_rate=Decimal(0.8),
                                                     tax_relevance=TaxRelevance.TAX_RELEVANT))
        accrual = ForeignCurrencyFlow("tradeId",
                                      today,
                                       "Tax relevant transaction",
                                      Money(Decimal(9), "EUR"),
                                      Money(Decimal(10), "USD"),
                                      fx_rate=Decimal(0.9),
                                      tax_relevance=TaxRelevance.TAX_RELEVANT)
        return_flow.consume(accrual, Money(Decimal(10), "USD"))

        profit = return_flow.calculate_taxable_profit(today)

        self.assertEqual(Money(Decimal(-1), "EUR"), profit.profit_base)


class ForeignCurrencyBucketTest(unittest.TestCase):
    def test_return_with_accrual_of_same_amount(self):
        bucket = ForeignCurrencyBucket("USD")

        # Accrual, i.e. increase of USD bucket (e.g. because of selling some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal(9), "EUR"),
                                       Money(Decimal(10), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        # Return, i.e. decrease of USD bucket (e.g. because of buying some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal(-9), "EUR"),
                                       Money(Decimal(-10), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()

        self.assertEqual(1, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))
        self.assertTrue(returns[0].is_consumed())
        self.assertEqual(1, len(returns[0].consumed_from))
        self.assertTrue(returns[0].consumed_from[0].is_consumed())

    def test_return_without_any_accrual(self):
        bucket = ForeignCurrencyBucket("USD")

        # Return, i.e. decrease of USD bucket (e.g. because of buying some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal(-9), "EUR"),
                                       Money(Decimal(-10), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()

        self.assertEqual(0, len(returns))
        self.assertEqual(1, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))
        self.assertFalse(unconsumed_returns[0].is_consumed())

    def test_accrual_without_any_return(self):
        bucket = ForeignCurrencyBucket("USD")

        # Accrual, i.e. increase of USD bucket (e.g. because of selling some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal(9), "EUR"),
                                       Money(Decimal(10), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()

        self.assertEqual(0, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(1, len(unconsumed_accruals))
        self.assertFalse(unconsumed_accruals[0].is_consumed())

    def test_return_with_accrual_of_greater_amount(self):
        bucket = ForeignCurrencyBucket("USD")

        # Accrual, i.e. increase of USD bucket (e.g. because of selling some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal("13.50"), "EUR"),
                                       Money(Decimal(15), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        # Return, i.e. decrease of USD bucket (e.g. because of buying some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal(-9), "EUR"),
                                       Money(Decimal(-10), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()

        self.assertEqual(1, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(1, len(unconsumed_accruals))
        self.assertTrue(returns[0].is_consumed())
        self.assertEqual(1, len(returns[0].consumed_from))
        self.assertFalse(returns[0].consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal(10), "USD"), returns[0].consumed_from[0].consumed())
        self.assertEqual(Money(Decimal(5), "USD"), unconsumed_accruals[0].unconsumed())

    def test_return_with_accrual_of_smaller_amount(self):
        bucket = ForeignCurrencyBucket("USD")

        # Accrual, i.e. increase of USD bucket (e.g. because of selling some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal("7.20"), "EUR"),
                                       Money(Decimal(8), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        # Return, i.e. decrease of USD bucket (e.g. because of buying some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal(-9), "EUR"),
                                       Money(Decimal(-10), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()

        self.assertEqual(0, len(returns))
        self.assertEqual(1, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))
        self.assertFalse(unconsumed_returns[0].is_consumed())
        self.assertEqual(Money(Decimal(-2), "USD"), unconsumed_returns[0].unconsumed())
        self.assertEqual(1, len(unconsumed_returns[0].consumed_from))
        self.assertTrue(unconsumed_returns[0].consumed_from[0].is_consumed())

    def test_multiple_returns_with_multiple_accruals_of_same_total(self):
        bucket = ForeignCurrencyBucket("USD")

        # Accrual, i.e. increase of USD bucket (e.g. because of selling some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal("4.50"), "EUR"),
                                       Money(Decimal(5), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal("13.50"), "EUR"),
                                       Money(Decimal(15), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        # Return, i.e. decrease of USD bucket (e.g. because of buying some USD stock)
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal("-3.60"), "EUR"),
                                       Money(Decimal(-4), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("tradeId",
                                       today,
                                        "Tax relevant transaction",
                                       Money(Decimal("-14.40"), "EUR"),
                                       Money(Decimal(-16), "USD"),
                                       fx_rate=Decimal(0.9),
                                       tax_relevance=TaxRelevance.TAX_RELEVANT))

        returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()

        # Result should be:
        # Return #1 (-4 USD) should be netted with Accrual #1 (4 USD, leaving 1 USD)
        # Return #2 (-16 USD) should be netted with Accrual #1 (1 USD, see above) and #2 (15 USD)
        self.assertEqual(2, len(returns))
        self.assertEqual(0, len(unconsumed_returns))
        self.assertEqual(0, len(unconsumed_accruals))

        self.assertTrue(returns[0].is_consumed())
        self.assertEqual(1, len(returns[0].consumed_from))
        self.assertFalse(returns[0].consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal(1), "USD"), returns[0].consumed_from[0].unconsumed())

        self.assertTrue(returns[1].is_consumed())
        self.assertEqual(2, len(returns[1].consumed_from))
        self.assertFalse(returns[1].consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal(1), "USD"), returns[1].consumed_from[0].consumed())

    def test_musterbeispiel_chf(self):
        bucket = ForeignCurrencyBucket("CHF")
        bucket.add(ForeignCurrencyFlow("785240291",
                                       datetime.date.fromisoformat("20181219"),
                                        "Kauf SGS Ltd.",
                                       Money(Decimal("-1787.83"), "EUR"),
                                       Money(Decimal("-2025.25"), "CHF"),
                                       Decimal("0.882770"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("512069927",
                                       datetime.date.fromisoformat("20181219"),
                                        "Verkauf Barry Callebaut AG",
                                       Money(Decimal("176.55"), "EUR"),
                                       Money(Decimal("200.00"), "CHF"),
                                       Decimal("0.882770"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("468951058",
                                       datetime.date.fromisoformat("20181219"),
                                        "Bardividende Zürich Insurance Group",
                                       Money(Decimal("308.97"), "EUR"),
                                       Money(Decimal("350.00"), "CHF"),
                                       Decimal("0.882770"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("187346370",
                                       datetime.date.fromisoformat("20181219"),
                                        "Bardividende Schindler Holding",
                                       Money(Decimal("419.54"), "EUR"),
                                       Money(Decimal("475.25"), "CHF"),
                                       Decimal("0.882770"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("504795099",
                                       datetime.date.fromisoformat("20190109"),
                                        "Bardividende Swisscom AG",
                                       Money(Decimal("1239.41"), "EUR"),
                                       Money(Decimal("1404.00"), "CHF"),
                                       Decimal("0.882770"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("531156445",
                                       datetime.date.fromisoformat("20190306"),
                                        "Kauf Roche Holding",
                                       Money(Decimal("-13616.86"), "EUR"),
                                       Money(Decimal("-15468.75"), "CHF"),
                                       Decimal("0.880282"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("416245004",
                                       datetime.date.fromisoformat("20190311"),
                                        "Verkauf Novartis AG",
                                       Money(Decimal("12842.54"), "EUR"),
                                       Money(Decimal("14575.00"), "CHF"),
                                       Decimal("0.881135"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("815222740",
                                       datetime.date.fromisoformat("20190329"),
                                        "Habenzinsen Q1 2019",
                                       Money(Decimal("16.07"), "EUR"),
                                       Money(Decimal("18.25"), "CHF"),
                                       Decimal("0.882770"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("125841627",
                                       datetime.date.fromisoformat("20190401"),
                                        "Bardividende Barry Callebaut AG",
                                       Money(Decimal("1606.64"), "EUR"),
                                       Money(Decimal("1820.00"), "CHF"),
                                       Decimal("0.882770"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("857357776",
                                       datetime.date.fromisoformat("20190617"),
                                        "Verkauf Alcon S.A.",
                                       Money(Decimal("43373.66"), "EUR"),
                                       Money(Decimal("48639.25"), "CHF"),
                                       Decimal("0.891742"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("541976683",
                                       datetime.date.fromisoformat("20190617"),
                                        "Kauf Nestle S.A.",
                                       Money(Decimal("-24531.56"), "EUR"),
                                       Money(Decimal("-27509.70"), "CHF"),
                                       Decimal("0.891742"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("271741815",
                                       datetime.date.fromisoformat("20190619"),
                                        "FX Spot",
                                       Money(Decimal("129282.48"), "EUR"),
                                       Money(Decimal("140000.00"), "CHF"),
                                       Decimal("0.923446"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("968899265",
                                       datetime.date.fromisoformat("20190625"),
                                        "Bardividende Roche Holding",
                                       Money(Decimal("6451.50"), "EUR"),
                                       Money(Decimal("6986.33"), "CHF"),
                                       Decimal("0.923446"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("461015249",
                                       datetime.date.fromisoformat("20190903"),
                                        "Verkauf SGS Ltd.",
                                       Money(Decimal("92215.32"), "EUR"),
                                       Money(Decimal("99860.00"), "CHF"),
                                       Decimal("0.923446"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("949019684",
                                       datetime.date.fromisoformat("20190903"),
                                        "Bargeldabhebung",
                                       Money(Decimal("-156985.87"), "EUR"),
                                       Money(Decimal("-170000.00"), "CHF"),
                                       Decimal("0.923446"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("872953563",
                                       datetime.date.fromisoformat("20190926"),
                                        "Geldeingang",
                                       Money(Decimal("139062.58"), "EUR"),
                                       Money(Decimal("151077.63"), "CHF"),
                                       Decimal("0.920471"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("463095910",
                                       datetime.date.fromisoformat("20190926"),
                                        "Gebührenerstattung",
                                       Money(Decimal("69.77"), "EUR"),
                                       Money(Decimal("75.80"), "CHF"),
                                       Decimal("0.920471"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("617254479",
                                       datetime.date.fromisoformat("20190930"),
                                        "Habenzinsen Q3 2019",
                                       Money(Decimal("17.81"), "EUR"),
                                       Money(Decimal("19.35"), "CHF"),
                                       Decimal("0.920471"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("958933088",
                                       datetime.date.fromisoformat("20191101"),
                                        "Kauf Zürich Insurance Group",
                                       Money(Decimal("-24244.61"), "EUR"),
                                       Money(Decimal("-26700.59"), "CHF"),
                                       Decimal("0.908018"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("697318797",
                                       datetime.date.fromisoformat("20191101"),
                                        "Verkauf Swisscom AG",
                                       Money(Decimal("41434.90"), "EUR"),
                                       Money(Decimal("45632.25"), "CHF"),
                                       Decimal("0.908018"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("191653070",
                                       datetime.date.fromisoformat("20191101"),
                                        "FX Spot",
                                       Money(Decimal("-88825.04"), "EUR"),
                                       Money(Decimal("-97823.02"), "CHF"),
                                       Decimal("0.908018"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("929424744",
                                       datetime.date.fromisoformat("20191218"),
                                        "Quellensteuernachzahlung",
                                       Money(Decimal("-262.39"), "EUR"),
                                       Money(Decimal("-286.35"), "CHF"),
                                       Decimal("0.916326"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("126227693",
                                       datetime.date.fromisoformat("20191218"),
                                        "Überweisung",
                                       Money(Decimal("-13344.86"), "EUR"),
                                       Money(Decimal("-14563.25"), "CHF"),
                                       Decimal("0.916326"),
                                       TaxRelevance.TAX_IRRELEVANT))
        bucket.add(ForeignCurrencyFlow("170188373",
                                       datetime.date.fromisoformat("20191218"),
                                        "Kauf Barry Callebaut AG",
                                       Money(Decimal("-142597.80"), "EUR"),
                                       Money(Decimal("-155616.98"), "CHF"),
                                       Decimal("0.916326"),
                                       TaxRelevance.TAX_RELEVANT))
        bucket.add(ForeignCurrencyFlow("987920963",
                                       datetime.date.fromisoformat("20191231"),
                                        "Zinszahlung",
                                       Money(Decimal("13.71"), "EUR"),
                                       Money(Decimal("14.96"), "CHF"),
                                       Decimal("0.916326"),
                                       TaxRelevance.TAX_IRRELEVANT))

        returns, unconsumed_returns, unconsumed_accruals = bucket.calculate_returns()

        self.assertEqual(9, len(returns))

        return_flow = returns[0]
        self.assertEqual(Money(Decimal(0), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(4, len(return_flow.consumed_from))
        self.assertTrue(return_flow.consumed_from[0].is_consumed())
        self.assertTrue(return_flow.consumed_from[1].is_consumed())
        self.assertTrue(return_flow.consumed_from[2].is_consumed())
        self.assertFalse(return_flow.consumed_from[3].is_consumed())
        self.assertEqual(Money(Decimal("1000.00"), "CHF"), return_flow.consumed_from[3].consumed_orig)

        return_flow = returns[1]
        self.assertEqual(Money(Decimal("-12.43"), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(4, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("404.00"), "CHF"), return_flow.consumed_from[0].consumed_orig)
        self.assertTrue(return_flow.consumed_from[1].is_consumed())
        self.assertTrue(return_flow.consumed_from[2].is_consumed())
        self.assertFalse(return_flow.consumed_from[3].is_consumed())
        self.assertEqual(Money(Decimal("471.50"), "CHF"), return_flow.consumed_from[3].consumed_orig)

        return_flow = returns[2]
        self.assertEqual(Money(Decimal(0), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(2, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("1348.50"), "CHF"), return_flow.consumed_from[0].consumed_orig)
        self.assertFalse(return_flow.consumed_from[1].is_consumed())
        self.assertEqual(Money(Decimal("26161.20"), "CHF"), return_flow.consumed_from[1].consumed_orig)

        return_flow = returns[3]
        self.assertEqual(Money(Decimal(0), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(4, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("22478.05"), "CHF"), return_flow.consumed_from[0].consumed_orig)
        self.assertTrue(return_flow.consumed_from[1].is_consumed())
        self.assertTrue(return_flow.consumed_from[2].is_consumed())
        self.assertFalse(return_flow.consumed_from[3].is_consumed())
        self.assertEqual(Money(Decimal("535.62"), "CHF"), return_flow.consumed_from[3].consumed_orig)

        return_flow = returns[4]
        self.assertEqual(Money(Decimal("-411.93"), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(1, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("26700.59"), "CHF"), return_flow.consumed_from[0].consumed_orig)

        return_flow = returns[5]
        self.assertEqual(Money(Decimal("-1434.25"), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(2, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("72623.79"), "CHF"), return_flow.consumed_from[0].consumed_orig)
        self.assertFalse(return_flow.consumed_from[1].is_consumed())
        self.assertEqual(Money(Decimal("25199.23"), "CHF"), return_flow.consumed_from[1].consumed_orig)

        return_flow = returns[6]
        self.assertEqual(Money(Decimal(0), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(1, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("286.35"), "CHF"), return_flow.consumed_from[0].consumed_orig)

        return_flow = returns[7]
        self.assertEqual(Money(Decimal(0), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(1, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("14563.25"), "CHF"), return_flow.consumed_from[0].consumed_orig)

        return_flow = returns[8]
        self.assertEqual(Money(Decimal("-90.56"), "EUR"), return_flow.calculate_taxable_profit(today).profit_base)
        self.assertEqual(4, len(return_flow.consumed_from))
        self.assertFalse(return_flow.consumed_from[0].is_consumed())
        self.assertEqual(Money(Decimal("111028.80"), "CHF"), return_flow.consumed_from[0].consumed_orig)
        self.assertTrue(return_flow.consumed_from[1].is_consumed())
        self.assertTrue(return_flow.consumed_from[2].is_consumed())
        self.assertFalse(return_flow.consumed_from[3].is_consumed())
        self.assertEqual(Money(Decimal("44493.03"), "CHF"), return_flow.consumed_from[3].consumed_orig)

        df = pd.DataFrame(columns=["Fremdwährung",
                                   "TradeID",
                                   "Datum",
                                   "Aktivität",
                                   "Ergebnisrelevant",
                                   "USD (gesamt)",
                                   "USD (verbraucht)",
                                   "USD (ergebnisrelevant)",
                                   "Devisenkurs",
                                   "EUR (ergebnisrelevant)",
                                   "Gewinn/Verlust"])
        for return_flow in returns:
            profit = return_flow.calculate_taxable_profit(today)
            rows = [
                ["Abgang",
                 return_flow.flow.tradeId,
                 return_flow.flow.date,
                 return_flow.flow.description,
                 return_flow.flow.is_tax_relevant(today),
                 return_flow.flow.amount_orig.amount,
                 return_flow.consumed().amount * return_flow.flow.amount_orig.sign(),
                 profit.tax_relevant_orig.amount * return_flow.flow.amount_orig.sign(),
                 return_flow.flow.fx_rate,
                 profit.tax_relevant_base.amount * return_flow.flow.amount_orig.sign(),
                 None]
            ]
            for consumed in profit.accruals:
                rows.append([
                    "Zugang",
                    consumed.flow.tradeId,
                    consumed.flow.date,
                    consumed.flow.description,
                    consumed.flow.is_tax_relevant(today),
                    consumed.flow.amount_orig.amount,
                    consumed.consumed().amount,
                    consumed.consumed_tax_relevant(today).amount,
                    consumed.flow.fx_rate,
                    consumed.consumed_base_tax_relevant(today).amount,
                    None
                ])
            rows.append([
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
                profit.profit_base.amount
            ])

            df_return = pd.DataFrame(rows, columns=df.columns)
            df = pd.concat([df, df_return], ignore_index=True)

        # print(df.to_csv(index=False))
