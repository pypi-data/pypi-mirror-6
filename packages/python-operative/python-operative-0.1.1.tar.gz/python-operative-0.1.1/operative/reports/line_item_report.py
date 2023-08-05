from operative.reports import Report
from operative.models import (
    LineItem,
)


class LineItemReport(Report):

    def parse_row(self, row):
        """
        Parses a row of csv data into a LineItem object.
        This function contains information on how to translate column headers into object attributes.
        It is meant to be delegated by the parent Report class.

        :param dict row: A row of csv data

        :rtype LineItem:

        """
        return LineItem(row)
