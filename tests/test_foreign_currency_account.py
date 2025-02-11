import datetime
import unittest
from decimal import Decimal

from foreign_currency_account import ForeignCurrencyAccount
from money import Money
from transaction import Transaction, BuySell, OpenCloseIndicator, AcquisitionType
from transaction_collection import TaxableTransaction, apply_estg_23


class DepotPositionCurrencyTests(unittest.TestCase):
    def test_type_long_with_open_txn_should_have_no_taxable_transactions(self):
        account = ForeignCurrencyAccount("USD")
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal(10),
                                            Money(Decimal(9), "EUR"),
                                            Money(Decimal(10), "USD"),
                                            Decimal("0.9")))

        transaction_pairs = account.transaction_pairs(2024)
        self.assertEqual(0, len(transaction_pairs))

    def test_type_long_with_open_and_close_txn_should_have_a_taxable_transaction(self):
        account = ForeignCurrencyAccount("USD")
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal(10),
                                            Money(Decimal(9), "EUR"),
                                            Money(Decimal(10), "USD"),
                                            Decimal("0.9")))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-8), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal("0.8")))

        transaction_pairs = account.transaction_pairs(2024)
        self.assertEqual(1, len(transaction_pairs))
        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-8), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal("0.8")),
                         transaction_pairs[0].closing_transaction)
        self.assertEqual(1, len(transaction_pairs[0].opening_transactions))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(10),
                                             Money(Decimal(9), "EUR"),
                                             Money(Decimal(10), "USD"),
                                             Decimal("0.9"))],
                         transaction_pairs[0].opening_transactions)

        self.assertEqual(Money(Decimal(-1), "EUR"), -transaction_pairs[0].profit())
        self.assertTrue(transaction_pairs[0].is_closed())

    def test_buy_greater_than_sell(self):
        account = ForeignCurrencyAccount("USD")
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal(20),
                                            Money(Decimal(16), "EUR"),
                                            Money(Decimal(20), "USD"),
                                            Decimal("0.8")))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-9), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal("0.9")))

        transaction_pairs = account.transaction_pairs(2024)
        self.assertEqual(1, len(transaction_pairs))
        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-9), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal("0.9")),
                         transaction_pairs[0].closing_transaction)
        self.assertEqual(1, len(transaction_pairs[0].opening_transactions))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(10),
                                             Money(Decimal(8), "EUR"),
                                             Money(Decimal(10), "USD"),
                                             Decimal("0.8"))],
                         transaction_pairs[0].opening_transactions)
        self.assertEqual(Money(Decimal(1), "EUR"), -transaction_pairs[0].profit())
        self.assertTrue(transaction_pairs[0].is_closed())

    def test_buy_smaller_than_sell(self):
        account = ForeignCurrencyAccount("USD")
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal(10),
                                            Money(Decimal(8), "EUR"),
                                            Money(Decimal(10), "USD"),
                                            Decimal("0.8")))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-20),
                                            Money(Decimal(-18), "EUR"),
                                            Money(Decimal(-20), "USD"),
                                            Decimal("0.9")))

        transaction_pairs = account.transaction_pairs(2024)
        self.assertEqual(1, len(transaction_pairs))
        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-20),
                                            Money(Decimal(-18), "EUR"),
                                            Money(Decimal(-20), "USD"),
                                            Decimal("0.9")),
                         transaction_pairs[0].closing_transaction)
        self.assertEqual(1, len(transaction_pairs[0].opening_transactions))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(10),
                                             Money(Decimal(8), "EUR"),
                                             Money(Decimal(10), "USD"),
                                             Decimal("0.8"))],
                         transaction_pairs[0].opening_transactions)
        self.assertEqual(Money(Decimal(10), "EUR"), -transaction_pairs[0].profit())
        self.assertFalse(transaction_pairs[0].is_closed())

    def test_multiple_openings_and_closings(self):
        account = ForeignCurrencyAccount("USD")
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal(5),
                                            Money(Decimal("4.50"), "EUR"),
                                            Money(Decimal(5), "USD"),
                                            Decimal("0.9")))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal(15),
                                            Money(Decimal("13.50"), "EUR"),
                                            Money(Decimal(15), "USD"),
                                            Decimal("0.9")))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-4),
                                            Money(Decimal("-3.60"), "EUR"),
                                            Money(Decimal(-4), "USD"),
                                            Decimal("0.9")))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-16),
                                            Money(Decimal("-14.40"), "EUR"),
                                            Money(Decimal(-16), "USD"),
                                            Decimal("0.9")))

        transaction_pairs = account.transaction_pairs(2024)
        self.assertEqual(2, len(transaction_pairs))
        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-4),
                                            Money(Decimal("-3.60"), "EUR"),
                                            Money(Decimal(-4), "USD"),
                                            Decimal("0.9")),
                         transaction_pairs[0].closing_transaction)
        self.assertEqual(1, len(transaction_pairs[0].opening_transactions))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(4),
                                             Money(Decimal("3.60"), "EUR"),
                                             Money(Decimal(4), "USD"),
                                             Decimal("0.9"))],
                         transaction_pairs[0].opening_transactions)
        self.assertEqual(Money(Decimal(0), "EUR"), transaction_pairs[0].profit())
        self.assertTrue(transaction_pairs[0].is_closed())

        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-16),
                                            Money(Decimal("-14.40"), "EUR"),
                                            Money(Decimal(-16), "USD"),
                                            Decimal("0.9")),
                         transaction_pairs[1].closing_transaction)
        self.assertEqual(2, len(transaction_pairs[1].opening_transactions))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(1),
                                             Money(Decimal("0.90"), "EUR"),
                                             Money(Decimal(1), "USD"),
                                             Decimal("0.9")),
                          TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(15),
                                             Money(Decimal("13.50"), "EUR"),
                                             Money(Decimal(15), "USD"),
                                             Decimal("0.9"))],
                         transaction_pairs[1].opening_transactions)
        self.assertEqual(Money(Decimal(0), "EUR"), -transaction_pairs[0].profit())
        self.assertTrue(transaction_pairs[1].is_closed())

    def test_multiple_openings_and_closings2(self):
        account = ForeignCurrencyAccount("USD")
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal(20),
                                            Money(Decimal(10), "EUR"),
                                            Money(Decimal(20), "USD"),
                                            Decimal("0.5")))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-10), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal(1)))
        account.add_transaction(Transaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-10), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal(1)))

        transaction_pairs = account.transaction_pairs(2024)
        self.assertEqual(2, len(transaction_pairs))
        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-10), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal(1)),
                         transaction_pairs[0].closing_transaction)
        self.assertEqual(1, len(transaction_pairs[0].opening_transactions))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(10),
                                             Money(Decimal(5), "EUR"),
                                             Money(Decimal(10), "USD"),
                                             Decimal("0.5"))],
                         transaction_pairs[0].opening_transactions)
        self.assertEqual(Money(Decimal(5), "EUR"), -transaction_pairs[0].profit())
        self.assertTrue(transaction_pairs[0].is_closed())

        self.assertEqual(TaxableTransaction(None,
                                            datetime.date(2024, 12, 24),
                                            None,
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal(-10),
                                            Money(Decimal(-10), "EUR"),
                                            Money(Decimal(-10), "USD"),
                                            Decimal(1)),
                         transaction_pairs[1].closing_transaction)
        self.assertEqual(1, len(transaction_pairs[1].opening_transactions))
        self.assertEqual([TaxableTransaction(None,
                                             datetime.date(2024, 12, 24),
                                             None,
                                             BuySell.BUY,
                                             OpenCloseIndicator.OPEN,
                                             Decimal(10),
                                             Money(Decimal(5), "EUR"),
                                             Money(Decimal(10), "USD"),
                                             Decimal("0.5"))],
                         transaction_pairs[1].opening_transactions)
        self.assertEqual(Money(Decimal(5), "EUR"), -transaction_pairs[0].profit())
        self.assertTrue(transaction_pairs[1].is_closed())

    def test_full_example_chf(self):
        account = ForeignCurrencyAccount("CHF")
        account.add_transaction(Transaction("785240291",
                                            datetime.date.fromisoformat("20190102"),
                                            "Kauf SGS Ltd.",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-2025.25"),
                                            Money(Decimal("-1787.83"), "EUR"),
                                            Money(Decimal("-2025.25"), "CHF"),
                                            Decimal("0.882770"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("512069927",
                                            datetime.date.fromisoformat("20190102"),
                                            "Verkauf Barry Callebaut AG",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("200.00"),
                                            Money(Decimal("176.55"), "EUR"),
                                            Money(Decimal("200.00"), "CHF"),
                                            Decimal("0.882770"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("468951058",
                                            datetime.date.fromisoformat("20190102"),
                                            "Bardividende Zürich Insurance Group",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("350.00"),
                                            Money(Decimal("308.97"), "EUR"),
                                            Money(Decimal("350.00"), "CHF"),
                                            Decimal("0.882770"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("187346370",
                                            datetime.date.fromisoformat("20190102"),
                                            "Bardividende Schindler Holding",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("475.25"),
                                            Money(Decimal("419.54"), "EUR"),
                                            Money(Decimal("475.25"), "CHF"),
                                            Decimal("0.882770"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("504795099",
                                            datetime.date.fromisoformat("20190109"),
                                            "Bardividende Swisscom AG",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("1404.00"),
                                            Money(Decimal("1239.41"), "EUR"),
                                            Money(Decimal("1404.00"), "CHF"),
                                            Decimal("0.882770"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("531156445",
                                            datetime.date.fromisoformat("20190306"),
                                            "Kauf Roche Holding",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-15468.75"),
                                            Money(Decimal("-13616.86"), "EUR"),
                                            Money(Decimal("-15468.75"), "CHF"),
                                            Decimal("0.880282"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("416245004",
                                            datetime.date.fromisoformat("20190311"),
                                            "Verkauf Novartis AG",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("14575.00"),
                                            Money(Decimal("12842.54"), "EUR"),
                                            Money(Decimal("14575.00"), "CHF"),
                                            Decimal("0.881135"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("815222740",
                                            datetime.date.fromisoformat("20190329"),
                                            "Habenzinsen Q1 2019",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("18.25"),
                                            Money(Decimal("16.11"), "EUR"),
                                            Money(Decimal("18.25"), "CHF"),
                                            Decimal("0.882770"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("125841627",
                                            datetime.date.fromisoformat("20190401"),
                                            "Bardividende Barry Callebaut AG",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("1820.00"),
                                            Money(Decimal("1606.64"), "EUR"),
                                            Money(Decimal("1820.00"), "CHF"),
                                            Decimal("0.882770"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("857357776",
                                            datetime.date.fromisoformat("20190617"),
                                            "Verkauf Alcon S.A.",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("48639.25"),
                                            Money(Decimal("43373.66"), "EUR"),
                                            Money(Decimal("48639.25"), "CHF"),
                                            Decimal("0.891742"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("541976683",
                                            datetime.date.fromisoformat("20190617"),
                                            "Kauf Nestle S.A.",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-27509.70"),
                                            Money(Decimal("-24531.55"), "EUR"),
                                            Money(Decimal("-27509.70"), "CHF"),
                                            Decimal("0.891742"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("271741815",
                                            datetime.date.fromisoformat("20190619"),
                                            "FX Spot",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("140000.00"),
                                            Money(Decimal("129282.44"), "EUR"),
                                            Money(Decimal("140000.00"), "CHF"),
                                            Decimal("0.923446"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("968899265",
                                            datetime.date.fromisoformat("20190625"),
                                            "Bardividende Roche Holding",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("6986.33"),
                                            Money(Decimal("6451.50"), "EUR"),
                                            Money(Decimal("6986.33"), "CHF"),
                                            Decimal("0.923446"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("461015249",
                                            datetime.date.fromisoformat("20190903"),
                                            "Verkauf SGS Ltd.",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("99860.00"),
                                            Money(Decimal("92215.32"), "EUR"),
                                            Money(Decimal("99860.00"), "CHF"),
                                            Decimal("0.923446"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("949019684",
                                            datetime.date.fromisoformat("20190903"),
                                            "Bargeldabhebung",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-170000.00"),
                                            Money(Decimal("-156985.82"), "EUR"),
                                            Money(Decimal("-170000.00"), "CHF"),
                                            Decimal("0.923446"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("872953563",
                                            datetime.date.fromisoformat("20190926"),
                                            "Geldeingang",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("151077.63"),
                                            Money(Decimal("139062.58"), "EUR"),
                                            Money(Decimal("151077.63"), "CHF"),
                                            Decimal("0.920471"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("463095910",
                                            datetime.date.fromisoformat("20190926"),
                                            "Gebührenerstattung",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("75.80"),
                                            Money(Decimal("69.77"), "EUR"),
                                            Money(Decimal("75.80"), "CHF"),
                                            Decimal("0.920471"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("617254479",
                                            datetime.date.fromisoformat("20190930"),
                                            "Habenzinsen Q3 2019",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("19.35"),
                                            Money(Decimal("17.81"), "EUR"),
                                            Money(Decimal("19.35"), "CHF"),
                                            Decimal("0.920471"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("958933088",
                                            datetime.date.fromisoformat("20191101"),
                                            "Kauf Zürich Insurance Group",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-26700.59"),
                                            Money(Decimal("-24244.61"), "EUR"),
                                            Money(Decimal("-26700.59"), "CHF"),
                                            Decimal("0.908018"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("697318797",
                                            datetime.date.fromisoformat("20191101"),
                                            "Verkauf Swisscom AG",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("45632.25"),
                                            Money(Decimal("41434.90"), "EUR"),
                                            Money(Decimal("45632.25"), "CHF"),
                                            Decimal("0.908018"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("191653070",
                                            datetime.date.fromisoformat("20191101"),
                                            "FX Spot",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-97823.02"),
                                            Money(Decimal("-88825.04"), "EUR"),
                                            Money(Decimal("-97823.02"), "CHF"),
                                            Decimal("0.908018"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("929424744",
                                            datetime.date.fromisoformat("20191218"),
                                            "Quellensteuernachzahlung",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-286.35"),
                                            Money(Decimal("-263.58"), "EUR"),
                                            Money(Decimal("-286.35"), "CHF"),
                                            Decimal("0.916326"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("126227693",
                                            datetime.date.fromisoformat("20191218"),
                                            "Überweisung",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-14563.25"),
                                            Money(Decimal("-13344.86"), "EUR"),
                                            Money(Decimal("-14563.25"), "CHF"),
                                            Decimal("0.916326"),
                                            AcquisitionType.NON_GENUINE))
        account.add_transaction(Transaction("170188373",
                                            datetime.date.fromisoformat("20191218"),
                                            "Kauf Barry Callebaut AG",
                                            BuySell.SELL,
                                            OpenCloseIndicator.CLOSE,
                                            Decimal("-155616.98"),
                                            Money(Decimal("-142597.80"), "EUR"),
                                            Money(Decimal("-155616.98"), "CHF"),
                                            Decimal("0.916326"),
                                            AcquisitionType.GENUINE))
        account.add_transaction(Transaction("987920963",
                                            datetime.date.fromisoformat("20191231"),
                                            "Zinszahlung",
                                            BuySell.BUY,
                                            OpenCloseIndicator.OPEN,
                                            Decimal("14.96"),
                                            Money(Decimal("13.71"), "EUR"),
                                            Money(Decimal("14.96"), "CHF"),
                                            Decimal("0.916326"),
                                            AcquisitionType.NON_GENUINE))

        transaction_pairs = account.transaction_pairs(2019)
        self.assertEqual(9, len(transaction_pairs))
        self.assertEqual(Money(Decimal(0), "EUR"), transaction_pairs[0].profit())
        self.assertEqual(Money(Decimal("14.66"), "EUR"), transaction_pairs[1].profit())
        self.assertEqual(Money(Decimal("-12.10"), "EUR"), transaction_pairs[2].profit())
        self.assertEqual(Money(Decimal("-712.64"), "EUR"), transaction_pairs[3].profit())
        self.assertEqual(Money(Decimal("411.94"), "EUR"), transaction_pairs[4].profit())
        self.assertEqual(Money(Decimal("1434.27"), "EUR"), transaction_pairs[5].profit())
        self.assertEqual(Money(Decimal(0), "EUR"), transaction_pairs[6].profit())
        self.assertEqual(Money(Decimal("60.19"), "EUR"), transaction_pairs[7].profit())
        self.assertEqual(Money(Decimal("89.04"), "EUR"), transaction_pairs[8].profit())

        estg23_transaction_pairs = apply_estg_23(transaction_pairs)
        self.assertEqual(9, len(estg23_transaction_pairs))
        self.assertEqual(Money(Decimal(0), "EUR"), estg23_transaction_pairs[0].profit())
        self.assertEqual(Money(Decimal("12.43"), "EUR"), estg23_transaction_pairs[1].profit())
        self.assertEqual(Money(Decimal(0), "EUR"), estg23_transaction_pairs[2].profit())
        self.assertEqual(Money(Decimal("0.01"), "EUR"), estg23_transaction_pairs[3].profit())
        self.assertEqual(Money(Decimal("411.94"), "EUR"), estg23_transaction_pairs[4].profit())
        self.assertEqual(Money(Decimal("1434.27"), "EUR"), estg23_transaction_pairs[5].profit())
        self.assertEqual(Money(Decimal("-1.19"), "EUR"), estg23_transaction_pairs[6].profit())
        self.assertEqual(Money(Decimal("-0.18"), "EUR"), estg23_transaction_pairs[7].profit())
        self.assertEqual(Money(Decimal("88.65"), "EUR"), estg23_transaction_pairs[8].profit())


if __name__ == '__main__':
    unittest.main()
