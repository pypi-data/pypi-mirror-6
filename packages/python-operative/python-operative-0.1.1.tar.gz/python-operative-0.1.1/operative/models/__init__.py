import datetime
from pprint import pformat

ATTR_AS_INT = lambda x: int(x)
ATTR_AS_FLOAT = lambda x: float(x)
ATTR_AS_DATETIME = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')


class OperativeModel(object):

    """
    Parent class for all operative models

    """

    def __init__(self, report_row):
        attribs = {self.REPORT_MAPPINGS[k]: v for k, v in report_row.items() if k in self.REPORT_MAPPINGS}
        for k, v in attribs.items():
            if k in self.ATTR_TRANSLATIONS:
                try:
                    v = self.ATTR_TRANSLATIONS[k](v)
                except ValueError:
                    v = None
            setattr(self, k, v)

    def __repr__(self):
        return pformat(self.__dict__)


class Advertiser(OperativeModel):

    """
    Represents an Operative Advertiser.

    """
    REPORT_MAPPINGS = {'Advertiser ID': 'id',
                       'Advertiser Name': 'name'}

    ATTR_TRANSLATIONS = {}


class Order(OperativeModel):

    """
    Represents an Operative order.

    """
    REPORT_MAPPINGS = {'Order ID': 'id',
                       'Order Name': 'name',
                       'Order Start Date': 'start_date',
                       'Order End Date': 'end_date'}

    ATTR_TRANSLATIONS = {'id': ATTR_AS_INT,
                         'start_date': ATTR_AS_DATETIME,
                         'end_date': ATTR_AS_DATETIME, }

    def __init__(self, report_row):
        OperativeModel.__init__(self, report_row)
        self.advertiser = Advertiser(report_row)


class LineItem(OperativeModel):

    """
    Represents an Operative Line Item.

    """
    REPORT_MAPPINGS = {'Line Item ID': 'id',
                       'Line Item Name': 'name',
                       'Line Item Start Date': 'start_date',
                       'Line Item End Date': 'end_date',
                       'Line Item Action': 'action',
                       'Quantity': 'quantity',
                       'Unit Cost': 'unit_cost',
                       'Cost Type': 'cost_type',
                       'Cost': 'cost', }

    ATTR_TRANSLATIONS = {'id': ATTR_AS_INT,
                         'start_date': ATTR_AS_DATETIME,
                         'end_date': ATTR_AS_DATETIME,
                         'quantity': ATTR_AS_INT,
                         'unit_cost': ATTR_AS_FLOAT,
                         'cost': ATTR_AS_FLOAT, }

    def __init__(self, report_row):
        OperativeModel.__init__(self, report_row)
        self.order = Order(report_row)
