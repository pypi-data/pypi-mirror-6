import unittest
import operative
import datetime

from caliendo.patch import patch
from caliendo import expected_value
from nose.tools import eq_, ok_
from operative.settings import TEST_FTP_LOGIN


class ReportTest(unittest.TestCase):

    """
    Test the various reports.

    """

    @patch('operative.FTPConnection.get_files')
    @patch('operative.FTPConnection._establish_connection')
    @patch('operative.FTPConnection._close_connection')
    def test_line_item_report(self):
        """
        Test LineItemReport

        """
        from operative.reports.line_item_report import LineItemReport

        def __get_and_test(path, since):
            ftp_creds = operative.FTPCredentials(**TEST_FTP_LOGIN)
            line_item_reports = LineItemReport().get_report_files(ftp_credentials=ftp_creds, ftp_path=path, since=since)
            for lir in line_item_reports:
                observed_value = str(lir.data[0])
                eq_(expected_value.get_or_store(observed_value), observed_value)

        # get all files
        __get_and_test(path='/flatfile', since=None)

        # get one file - using "since"
        __get_and_test(path='/flatfile', since=datetime.datetime(2014, 1, 7, 0, 42))

        # get zero files - using "since"
        __get_and_test(path='/flatfile', since=datetime.datetime(2014, 2, 1))

        # get zero files - only directories in path
        __get_and_test(path='/', since=None)
