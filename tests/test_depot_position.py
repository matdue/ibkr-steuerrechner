import datetime
import unittest
from decimal import Decimal

from Asset import Asset
from depot_position import DepotPosition, DepotPositionType
from money import Money
from transaction import Transaction, BuySell, OpenCloseIndicator
from transaction_collection import TaxableTransaction


class DepotPositionTests(unittest.TestCase):
    def test_no_transactions_should_be_of_none_type(self):
        depot_position = DepotPosition(Asset("XXX", "ConID", "STK"))
        self.assertEqual(None, depot_position.position_type())

    def test_initial_txn_open_buy_should_be_of_type_long(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(1),
                                                   None,
                                                   None,
                                                   None))

        self.assertEqual(DepotPositionType.LONG, depot_position.position_type())

    def test_initial_txn_open_sell_should_be_of_type_short(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(1),
                                                   None,
                                                   None,
                                                   None))

        self.assertEqual(DepotPositionType.SHORT, depot_position.position_type())

    def test_initial_txn_close_buy_should_be_of_type_short(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(1),
                                                   None,
                                                   None,
                                                   None))

        self.assertEqual(DepotPositionType.SHORT, depot_position.position_type())

    def test_initial_txn_close_sell_should_be_of_type_long(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(1),
                                                   None,
                                                   None,
                                                   None))

        self.assertEqual(DepotPositionType.LONG, depot_position.position_type())

    def test_type_long_with_open_txn_should_have_no_transaction_collections(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(1),
                                                   None,
                                                   None,
                                                   None))

        transaction_collections = depot_position.transaction_collections(2024)
        self.assertEqual(0, len(transaction_collections))

    def test_type_long_with_open_and_close_txn_should_have_a_transaction_collection(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(1),
                                                   None,
                                                   None,
                                                   None))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(-1),
                                                   None,
                                                   None,
                                                   None))

        transaction_collections = depot_position.transaction_collections(2024)
        self.assertEqual(1, len(transaction_collections))
        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            asset,
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-1),
                                            None,
                                            None,
                                            None),
                         transaction_collections[0].get_closing_transaction())
        self.assertEqual(1, len(transaction_collections[0].get_opening_transactions()))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(1),
                                             None,
                                             None,
                                             None)],
                         transaction_collections[0].get_opening_transactions())

    def test_type_long_with_one_open_and_two_close_txn_should_have_two_transactions_collections(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(2),
                                                   Money(Decimal(-220), "EUR"),
                                                   Money(Decimal(-220), "USD"),
                                                   Decimal(1)))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(-1),
                                                   Money(Decimal(100), "EUR"),
                                                   Money(Decimal(100), "USD"),
                                                   Decimal(1)))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 25),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(-1),
                                                   Money(Decimal(100), "EUR"),
                                                   Money(Decimal(100), "USD"),
                                                   Decimal(1)))

        transaction_collections = depot_position.transaction_collections(2024)
        self.assertEqual(2, len(transaction_collections))

        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            asset,
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-1),
                                            Money(Decimal(100), "EUR"),
                                            Money(Decimal(100), "USD"),
                                            Decimal(1)),
                         transaction_collections[0].get_closing_transaction())
        self.assertEqual(1, len(transaction_collections[0].get_opening_transactions()))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(1),
                                             Money(Decimal(-110), "EUR"),
                                             Money(Decimal(-110), "USD"),
                                             Decimal(1))],
                         transaction_collections[0].get_opening_transactions())

        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 25),
                                            asset,
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-1),
                                            Money(Decimal(100), "EUR"),
                                            Money(Decimal(100), "USD"),
                                            Decimal(1)),
                         transaction_collections[1].get_closing_transaction())
        self.assertEqual(1, len(transaction_collections[1].get_opening_transactions()))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(1),
                                             Money(Decimal(-110), "EUR"),
                                             Money(Decimal(-110), "USD"),
                                             Decimal(1))],
                         transaction_collections[1].get_opening_transactions())

    def test_type_long_with_two_open_and_one_close_txn_should_have_one_transaction_collection(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(1),
                                                   Money(Decimal(-220), "EUR"),
                                                   Money(Decimal(-220), "USD"),
                                                   Decimal(1)))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(1),
                                                   Money(Decimal(-100), "EUR"),
                                                   Money(Decimal(-100), "USD"),
                                                   Decimal(1)))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 25),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(-2),
                                                   Money(Decimal(320), "EUR"),
                                                   Money(Decimal(320), "USD"),
                                                   Decimal(1)))

        transaction_collections = depot_position.transaction_collections(2024)
        self.assertEqual(1, len(transaction_collections))

        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 25),
                                            asset,
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-2),
                                            Money(Decimal(320), "EUR"),
                                            Money(Decimal(320), "USD"),
                                            Decimal(1)),
                         transaction_collections[0].get_closing_transaction())
        self.assertEqual(2, len(transaction_collections[0].get_opening_transactions()))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(1),
                                             Money(Decimal(-220), "EUR"),
                                             Money(Decimal(-220), "USD"),
                                             Decimal(1)),
                          TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(1),
                                             Money(Decimal(-100), "EUR"),
                                             Money(Decimal(-100), "USD"),
                                             Decimal(1))],
                         transaction_collections[0].get_opening_transactions())

    def test_type_long_with_unclosed_txn_should_have_a_transaction_collection(self):
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(2),
                                                   Money(Decimal(-220), "EUR"),
                                                   Money(Decimal(-220), "USD"),
                                                   Decimal(1)))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 25),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(-1),
                                                   Money(Decimal(100), "EUR"),
                                                   Money(Decimal(100), "USD"),
                                                   Decimal(1)))

        transaction_collections = depot_position.transaction_collections(2024)
        self.assertEqual(1, len(transaction_collections))

        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 25),
                                            asset,
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-1),
                                            Money(Decimal(100), "EUR"),
                                            Money(Decimal(100), "USD"),
                                            Decimal(1)),
                         transaction_collections[0].get_closing_transaction())
        self.assertEqual(1, len(transaction_collections[0].get_opening_transactions()))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(1),
                                             Money(Decimal(-110), "EUR"),
                                             Money(Decimal(-110), "USD"),
                                             Decimal(1))],
                         transaction_collections[0].get_opening_transactions())

    def test_type_long_with_open_close_open_txn_should_have_one_transaction_collection(self):
        # Special case: Foreign currency bucket
        # The quantity is equal to the amount
        asset = Asset("XXX", "ConID", "STK")
        depot_position = DepotPosition(asset)
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 23),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(100),
                                                   Money(Decimal(-100), "EUR"),
                                                   Money(Decimal(-100), "USD"),
                                                   Decimal(1)))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 24),
                                                   asset,
                                                   None,
                                                   BuySell.SELL,
                                                   OpenCloseIndicator.CLOSE,
                                                   Decimal(-200),
                                                   Money(Decimal(200), "EUR"),
                                                   Money(Decimal(200), "USD"),
                                                   Decimal(1)))
        depot_position.add_transaction(Transaction(None,
                                                   datetime.date(2024, 12, 25),
                                                   asset,
                                                   None,
                                                   BuySell.BUY,
                                                   OpenCloseIndicator.OPEN,
                                                   Decimal(100),
                                                   Money(Decimal(-100), "EUR"),
                                                   Money(Decimal(-100), "USD"),
                                                   Decimal(1)))

        transaction_collections = depot_position.transaction_collections(2024)
        self.assertEqual(1, len(transaction_collections))

        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            asset,
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-200),
                                            Money(Decimal(200), "EUR"),
                                            Money(Decimal(200), "USD"),
                                            Decimal(1)),
                         transaction_collections[0].get_closing_transaction())
        self.assertEqual(2, len(transaction_collections[0].get_opening_transactions()))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 23),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(100),
                                             Money(Decimal(-100), "EUR"),
                                             Money(Decimal(-100), "USD"),
                                             Decimal(1)),
                          TaxableTransaction(None,
                                             datetime.date(2024, 12, 25),
                                             asset,
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(100),
                                             Money(Decimal(-100), "EUR"),
                                             Money(Decimal(-100), "USD"),
                                             Decimal(1))],
                         transaction_collections[0].get_opening_transactions())

if __name__ == '__main__':
    unittest.main()
