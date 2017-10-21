import unittest
import datetime

import os

from data_normaliser import TransactionsCSVWriter, Transaction, CoverallConverter, ABCConverter


class TransactionsCSVWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.transaction = Transaction(
            transaction_id=1,
            date_claimed=datetime.datetime.strptime('01/01/2017', '%d/%m/%Y'),
            first_name='Ash',
            last_name='Ramesh',
            dob=datetime.datetime.strptime('04/09/1992', '%d/%m/%Y'),
            item_id='Dental01',
            item_description='New Teeth',
            cost=10000,
            fund_cover=9000,
            payment_method='Cash',
            provider='AshCover',
            health_fund='AshHealth'
        )

    def test_correct_dictify(self):
        transaction = self.transaction

        writer = TransactionsCSVWriter()
        dict_ = writer.dictify_transaction(transaction)

        self.assertDictEqual(dict_, {
            'TransactionID': transaction.transaction_id,
            'DateClaimed': '01-Jan-17',
            'FirstName': transaction.first_name,
            'LastName': transaction.last_name,
            'DateOfBirth': '04/09/1992',
            'ItemID': transaction.item_id,
            'ItemDescription': transaction.item_description,
            'Cost': transaction.cost,
            'FundCover': transaction.fund_cover,
            'PaymentMethod': transaction.payment_method,
            'Provider': transaction.provider,
            'HealthFund': transaction.health_fund,
        })

    def test_correctly_create_csv(self):
        try:
            writer = TransactionsCSVWriter()
            transactions = [self.transaction]
            file = 'testcsv'
            writer.create_csv(transactions, file)
            with open('{}.csv'.format(file)) as f:
                line_count = len([l for l in f])
                self.assertEqual(line_count, 2)  # Header, 1 Transaction
        finally:  # Cleanup file
            try:
                os.remove('testcsv.csv')
            except OSError:  # pragma: no cover
                pass


class CoverterTestCase(unittest.TestCase):

    def test_ABC_converter(self):
        abc = ABCConverter()

        row = {
            'TransactionID': 1,
            'DateClaimed': '01/01/2017',
            'DOB': '01/01/2014',
            'FirstName': 'Ash',
            'LastName': 'Ramesh',
            'ItemID': 'AAA',
            'ItemDescription': 'BBBB',
            'Cost': 10,
            'FundCoverAmount': 10,
            'PaymentMethod': 'Cash',
            'ProviderCode': 'ABCX'
        }
        transaction = abc.convert_row_to_transaction(row)
        self.assertEqual(transaction.date_claimed,
                         datetime.datetime(year=2017, day=1, month=1))
        self.assertEqual(transaction.dob,
                         datetime.datetime(year=2014, day=1, month=1))
        self.assertEqual(transaction.health_fund, abc.HEALTH_FUND)

    def test_ABC_invalid_data(self):
        abc = ABCConverter()

        row1 = {
            'TransactionID': 1,
            'DateClaimed': '01/01/2017',
            'DOB': '01/01/2014',
            'FirstName': '',  # No First Name
            'LastName': 'Ramesh',
            'ItemID': 'AAA',
            'ItemDescription': 'BBBB',
            'Cost': 10,
            'FundCoverAmount': 10,
            'PaymentMethod': 'Cash',
            'ProviderCode': 'ABCX'
        }

        row2 = {
            'TransactionID': 'A',  # Not an int
            'DateClaimed': '01/01/2017',
            'DOB': '01/01/2014',
            'FirstName': 'Adsgsd',
            'LastName': 'Ramesh',
            'ItemID': 'AAA',
            'ItemDescription': 'BBBB',
            'Cost': 10,
            'FundCoverAmount': 10,
            'PaymentMethod': 'Cash',
            'ProviderCode': 'ABCX'
        }

        row3 = {
            'TransactionID': 1,
            'DateClaimed': '01/01/2017',
            'DOB': '01/01/2014',
            'FirstName': 'Ash',
            'LastName': 'Ramesh',
            'ItemID': 'AAA',
            'ItemDescription': 'BBBB',
            'Cost': None,  # No cost
            'FundCoverAmount': 10,
            'PaymentMethod': 'Cash',
            'ProviderCode': 'ABCX'
        }

        row4 = {
            'TransactionID': 1,
            'DateClaimed': '01-01/2017',  # Invalid Date
            'DOB': '01/01/2014',
            'FirstName': 'Ash',
            'LastName': 'Ramesh',
            'ItemID': 'AAA',
            'ItemDescription': 'BBBB',
            'Cost': 1,
            'FundCoverAmount': 10,
            'PaymentMethod': 'Cash',
            'ProviderCode': 'ABCX'
        }

        row5 = {
            'TransactionID': 1,
            'DateClaimed': '01/01/2017',
            'DOB': None,
            'FirstName': 'Ash',
            'LastName': 'Ramesh',
            'ItemID': 'AAA',
            'ItemDescription': 'BBBB',
            'Cost': 1,
            'FundCoverAmount': 10,
            'PaymentMethod': 'Cash',
            'ProviderCode': 'ABCX'
        }

        for row in [row1, row2, row3, row4, row5]:
            self.assertRaises(ValueError, abc.convert_row_to_transaction, row)

    def test_Coverall_data(self):
        coverall = CoverallConverter()

        row = {
            'TransactionID': 1,
            'DateClaimed': '01-Jan-17',
            'DateOfBirth': '01/01/2014',
            'FirstName': '',  # No First Name
            'MiddleName': 'Baab',
            'LastName': 'Ramesh',
            'ItemID': 'AAA',
            'ItemDesc': 'BBBB',
            'Cost': 10,
            'FundCover': 10,
            'PaymentType': 'Cash',
            'Provider': 'ABCX',
            'HealthFund': 'Coverall'
        }
        self.assertRaises(ValueError,
                          coverall.convert_row_to_transaction, row)

        row['FirstName'] = 'Ash'

        transaction = coverall.convert_row_to_transaction(row)
        self.assertEqual(transaction.health_fund, row['HealthFund'])

    def test_Coverall_middlename_logic(self):
        c = CoverallConverter()
        row = {
            'FirstName': 'Ash',
            'MiddleName': None
        }

        self.assertEqual(c.build_first_name(row), 'Ash')

        row['MiddleName'] = 'Bab'
        self.assertEqual(c.build_first_name(row), 'Ash Bab')
