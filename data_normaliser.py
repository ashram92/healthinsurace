import csv
import datetime
import logging
from typing import List

logger = logging.getLogger(__name__)


class Transaction:
    """Represents a normalised transaction object from a health insurer."""

    def __init__(self, transaction_id: int, date_claimed: datetime.datetime,
                 first_name: str, last_name: str, dob: datetime.datetime,
                 item_id: str, item_description: str, cost: float,
                 fund_cover: float, payment_method: str, provider: str,
                 health_fund: str):
        self.transaction_id = transaction_id
        self.date_claimed = date_claimed
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.item_id = item_id
        self.item_description = item_description
        self.cost = cost
        self.fund_cover = fund_cover
        self.payment_method = payment_method
        self.provider = provider
        self.health_fund = health_fund


class TransactionsCSVWriter:
    """Class to convert a list of `Transaction` objects to a csv file"""

    # The normalised fields names (in order)
    field_names = [
        'TransactionID',
        'DateClaimed',
        'FirstName',
        'LastName',
        'DateOfBirth',
        'ItemID',
        'ItemDescription',
        'Cost',
        'FundCover',
        'PaymentMethod',
        'Provider',
        'HealthFund'
    ]

    def dictify_transaction(self, transaction: Transaction) -> dict:
        """Converts a `Transaction` into a dictionary, with the `field_names`
        as keys. The values will be correctly formatted for CSV import
        purposes.

        An exception will be raised if fields are missing or cannot be
        formatted.
        """
        return {
            'TransactionID': transaction.transaction_id,
            'DateClaimed': transaction.date_claimed.strftime('%d-%b-%y'),
            'FirstName': transaction.first_name,
            'LastName': transaction.last_name,
            'DateOfBirth': transaction.dob.strftime('%d/%m/%Y'),
            'ItemID': transaction.item_id,
            'ItemDescription': transaction.item_description,
            'Cost': transaction.cost,
            'FundCover': transaction.fund_cover,
            'PaymentMethod': transaction.payment_method,
            'Provider': transaction.provider,
            'HealthFund': transaction.health_fund,
        }

    def create_csv(self, transactions: List[Transaction], filename):
        """
        Converts the given list of `Transaction` objects into a csv file with
        the name given in the `filename` parameter in the current working
         directory.

        The rows are not written into the file unless all fields are
        present in the transaction and can be correctly formatted.

        The final output will be a CSV file and a message with the error count.
        """
        full_file_name = "{}.csv".format(filename)
        with open(full_file_name, 'w') as f:
            writer = csv.DictWriter(f, quoting=csv.QUOTE_NONE,
                                    fieldnames=self.field_names)
            writer.writeheader()
            for transaction in transactions:
                try:
                    transaction_dict = self.dictify_transaction(transaction)
                    writer.writerow(transaction_dict)
                except Exception as e:
                    logger.error(e)

        logger.info('CSV file created - {}'.format(full_file_name))


class AbstractCustomerToTransactionCSVConverter:
    """Abstract class that defines the methods to convert a customer
    CSV file into a Lorica normalised transactions CSV file.

    Basic Logic:
    Customer CSV -> List[Transaction] -> Normalised CSV File
    """

    def __init__(self):
        self.normalised_csv_writer = TransactionsCSVWriter()

    def _build_string_value(self, row, fieldname):
        try:
            if not row[fieldname]:
                raise Exception('No data in field')
            return row[fieldname]
        except Exception:
            raise ValueError('Invalid value for {}'.format(fieldname))

    def _build_monetary_value(self, row, fieldname):
        try:
            return float(row[fieldname])
        except Exception:
            raise ValueError('Invalid value for {}'.format(fieldname))

    def build_transaction_id(self, row, fieldname='TransactionID'):
        try:
            return int(row[fieldname])
        except Exception:
            raise ValueError('Invalid value for {}'.format(fieldname))

    def build_date_claimed(self, row, date_format, fieldname='DateClaimed'):
        try:
            return datetime.datetime.strptime(row[fieldname], date_format)
        except Exception:
            raise ValueError('Invalid value for {}'.format(fieldname))

    def build_first_name(self, row, fieldname='FirstName'):
        return self._build_string_value(row, fieldname)

    def build_last_name(self, row, fieldname='LastName'):
        return self._build_string_value(row, fieldname)

    def build_dob(self, row, date_format, fieldname='DOB'):
        try:
            return datetime.datetime.strptime(row[fieldname], date_format)
        except Exception:
            raise ValueError('Invalid value for {}'.format(fieldname))

    def build_item_id(self, row, fieldname='ItemID'):
        return self._build_string_value(row, fieldname)

    def build_item_description(self, row, fieldname='ItemDescription'):
        return self._build_string_value(row, fieldname)

    def build_cost(self, row, fieldname='Cost'):
        return self._build_monetary_value(row, fieldname)

    def build_fund_cover(self, row, fieldname='FundCover'):
        return self._build_monetary_value(row, fieldname)

    def build_payment_method(self, row, fieldname='PaymentMethod'):
        return self._build_string_value(row, fieldname)

    def build_provider(self, row, fieldname='Provider'):
        return self._build_string_value(row, fieldname)

    def build_health_fund(self, row, fieldname='HealthFund'):
        return self._build_string_value(row, fieldname)

    def convert_row_to_transaction(self, row) -> Transaction:
        raise NotImplementedError  # noqa

    def convert_raw_csv_to_transaction(self, file_path) -> List[Transaction]:
        """This method will convert a raw csv file into a
        list of `Transaction` objects"""
        transactions = []
        error_count = 0
        with open(file_path) as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                try:
                    transactions.append(self.convert_row_to_transaction(row))
                except Exception as e:
                    error_count += 1
                    logger.error('Error converting record to Transaction '
                                 '(Error: {}): Row {}'.format(e, i))

        if error_count:
            logger.error('Errors: {}'.format(error_count))
        return transactions

    def convert(self, file_path, output_file_name):
        transactions = self.convert_raw_csv_to_transaction(file_path)
        self.normalised_csv_writer.create_csv(transactions, output_file_name)


class ABCConverter(AbstractCustomerToTransactionCSVConverter):
    """Converter for Customer ABC"""

    HEALTH_FUND = 'ABC'

    def build_health_fund(self, *args, **kwargs):
        return self.HEALTH_FUND

    def convert_row_to_transaction(self, row) -> Transaction:
        return Transaction(
            transaction_id=self.build_transaction_id(row),
            date_claimed=self.build_date_claimed(row, '%d/%m/%Y'),
            dob=self.build_dob(row, '%d/%m/%Y'),
            first_name=self.build_first_name(row),
            last_name=self.build_last_name(row),
            item_id=self.build_item_id(row),
            item_description=self.build_item_description(row),
            cost=self.build_cost(row),
            fund_cover=self.build_fund_cover(row, fieldname='FundCoverAmount'),
            payment_method=self.build_payment_method(row),
            provider=self.build_provider(row, fieldname='ProviderCode'),
            health_fund=self.build_health_fund()
        )


class CoverallConverter(AbstractCustomerToTransactionCSVConverter):
    """Converter for Customer ABC"""

    def build_first_name(self, row, fieldname='FirstName'):
        """Needs to merge MiddleName"""
        first_name = super(CoverallConverter, self).build_first_name(row,
                                                                     fieldname)
        if row['MiddleName']:
            return '{} {}'.format(first_name, row['MiddleName'])

        return first_name

    def convert_row_to_transaction(self, row) -> Transaction:
        return Transaction(
            transaction_id=self.build_transaction_id(row),
            date_claimed=self.build_date_claimed(row, '%d-%b-%y'),
            first_name=self.build_first_name(row),
            last_name=self.build_last_name(row),
            dob=self.build_dob(row, '%d/%m/%Y', fieldname='DateOfBirth'),
            item_id=self.build_item_id(row),
            item_description=self.build_item_description(row,
                                                         fieldname='ItemDesc'),
            cost=self.build_cost(row),
            fund_cover=self.build_fund_cover(row),
            payment_method=self.build_payment_method(row,
                                                     fieldname='PaymentType'),
            provider=self.build_provider(row),
            health_fund=self.build_health_fund(row)
        )


if __name__ == '__main__':  # pragma: no cover

    # Setup Logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # ABC Converter
    abc_converter = ABCConverter()
    abc_converter.convert('datafiles/ABC_2017_02_01.csv', 'ABC-normalised')

    print('\n')

    # ABC Converter
    coverall_converter = CoverallConverter()
    coverall_converter.convert('datafiles/Coverall_2017_02_18.csv',
                               'Coverall-normalised')
