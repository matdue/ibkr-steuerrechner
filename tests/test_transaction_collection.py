import datetime
import unittest
from decimal import Decimal

from money import Money
from transaction import Transaction, BuySell, OpenCloseIndicator, AcquisitionType
from transaction_collection import TaxableTransaction, TaxRelevance, SingleTransaction, to_single_transactions, \
    TransactionPair, to_opening_closing_pairs


class TransactionCollectionTest(unittest.TestCase):
    def test_taxable_transaction_from_transaction(self):
        transaction = Transaction(
            trade_id="Trade ID",
            date=datetime.date(2025, 1, 1),
            asset=None,
            activity="Activity",
            buy_sell=BuySell.BUY,
            open_close=OpenCloseIndicator.OPEN,
            quantity=Decimal(1),
            amount=Money(Decimal("-1.80"), "EUR"),
            amount_orig=Money(Decimal("-2.00"), "USD"),
            fx_rate=Decimal("0.9"),
            acquisition=AcquisitionType.GENUINE
        )

        taxable_transaction = TaxableTransaction.from_transaction(transaction, TaxRelevance.TAX_RELEVANT)

        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            taxable_transaction)

    def test_single_transaction_is_always_closed(self):
        transaction = SingleTransaction(
            TaxableTransaction(
                trade_id="Trade ID",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            )
        )

        self.assertTrue(transaction.is_closed())

    def test_single_transaction_profit_equals_amount(self):
        transaction = SingleTransaction(
            TaxableTransaction(
                trade_id="Trade ID",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            )
        )

        self.assertEqual(Money(Decimal("-1.80"), "EUR"), transaction.profit())

    def test_to_single_transactions_should_build_list_of_single_transactions(self):
        transactions = [
            Transaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE
            ),
            Transaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE
            )
        ]

        single_transactions = to_single_transactions(transactions, 2025)

        self.assertEqual([
            SingleTransaction(TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            )),
            SingleTransaction(TaxableTransaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ))
        ], single_transactions)

    def test_to_single_transactions_should_filter_by_year(self):
        transactions = [
            Transaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE
            ),
            Transaction(
                trade_id="Trade ID #2",
                date=datetime.date(2026, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE
            )
        ]

        single_transactions = to_single_transactions(transactions, 2025)

        self.assertEqual([
            SingleTransaction(TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ))
        ], single_transactions)

    def test_transaction_pair_is_closed_if_quantity_total_is_zero(self):
        transaction = TransactionPair(
            TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            [TaxableTransaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            )]
        )

        self.assertTrue(transaction.is_closed())

    def test_transaction_pair_is_open_if_quantity_total_is_nonzero(self):
        transaction = TransactionPair(
            TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(2),
                amount=Money(Decimal("-3.60"), "EUR"),
                amount_orig=Money(Decimal("-4.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            [TaxableTransaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            )]
        )

        self.assertFalse(transaction.is_closed())

    def test_transaction_pair_profit_equals_total_of_amount(self):
        transaction = TransactionPair(
            TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            [TaxableTransaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            )]
        )

        self.assertEqual(Money(Decimal("0.10"), "EUR"), transaction.profit())

    def test_to_opening_closing_pairs_one_open_one_close(self):
        transactions = [
            Transaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE
            ),
            Transaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE
            )
        ]

        transaction_pairs = to_opening_closing_pairs(transactions, 2025)
        self.assertEqual(1, len(transaction_pairs))
        self.assertEqual(1, len(transaction_pairs[0].opening_transactions))
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[0].opening_transactions[0]
        )
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[0].closing_transaction
        )

    def test_to_opening_closing_pairs_one_open_two_close(self):
        transactions = [
            Transaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(2),
                amount=Money(Decimal("-3.60"), "EUR"),
                amount_orig=Money(Decimal("-4.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE
            ),
            Transaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE
            ),
            Transaction(
                trade_id="Trade ID #3",
                date=datetime.date(2025, 1, 3),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.70"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.85"),
                acquisition=AcquisitionType.GENUINE
            )
        ]

        transaction_pairs = to_opening_closing_pairs(transactions, 2025)
        self.assertEqual(2, len(transaction_pairs))
        self.assertEqual(1, len(transaction_pairs[0].opening_transactions))
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[0].opening_transactions[0]
        )
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.90"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[0].closing_transaction
        )

        self.assertEqual(1, len(transaction_pairs[1].opening_transactions))
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[1].opening_transactions[0]
        )
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #3",
                date=datetime.date(2025, 1, 3),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-1),
                amount=Money(Decimal("1.70"), "EUR"),
                amount_orig=Money(Decimal("2.00"), "USD"),
                fx_rate=Decimal("0.85"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[1].closing_transaction
        )

    def test_to_opening_closing_pairs_two_open_one_close(self):
        transactions = [
            Transaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE
            ),
            Transaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.90"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE
            ),
            Transaction(
                trade_id="Trade ID #3",
                date=datetime.date(2025, 1, 3),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-2),
                amount=Money(Decimal("3.40"), "EUR"),
                amount_orig=Money(Decimal("4.00"), "USD"),
                fx_rate=Decimal("0.85"),
                acquisition=AcquisitionType.GENUINE
            )
        ]

        transaction_pairs = to_opening_closing_pairs(transactions, 2025)
        self.assertEqual(1, len(transaction_pairs))
        self.assertEqual(2, len(transaction_pairs[0].opening_transactions))
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #1",
                date=datetime.date(2025, 1, 1),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.80"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.9"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[0].opening_transactions[0]
        )
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #2",
                date=datetime.date(2025, 1, 2),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.BUY,
                open_close=OpenCloseIndicator.OPEN,
                quantity=Decimal(1),
                amount=Money(Decimal("-1.90"), "EUR"),
                amount_orig=Money(Decimal("-2.00"), "USD"),
                fx_rate=Decimal("0.95"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[0].opening_transactions[1]
        )
        self.assertEqual(
            TaxableTransaction(
                trade_id="Trade ID #3",
                date=datetime.date(2025, 1, 3),
                asset=None,
                activity="Activity",
                buy_sell=BuySell.SELL,
                open_close=OpenCloseIndicator.CLOSE,
                quantity=Decimal(-2),
                amount=Money(Decimal("3.40"), "EUR"),
                amount_orig=Money(Decimal("4.00"), "USD"),
                fx_rate=Decimal("0.85"),
                acquisition=AcquisitionType.GENUINE,
                tax_relevance=TaxRelevance.TAX_RELEVANT
            ),
            transaction_pairs[0].closing_transaction
        )


if __name__ == '__main__':
    unittest.main()
