import unittest
import operative
import datetime

from caliendo.patch import patch
from nose.tools import eq_, ok_
from operative.settings import TEST_FTP_LOGIN


class FTPTest(unittest.TestCase):

    """
    Tests for the basic ftp functionality.

    """

    @patch('operative.FTPConnection.get_files')
    @patch('operative.FTPConnection._establish_connection')
    @patch('operative.FTPConnection._close_connection')
    def test_get_files(self):
        """
        Test FTPConnection.get_files

        """
        def __get_and_test(path, since, num_expected_files):
            ftp_creds = operative.FTPCredentials(**TEST_FTP_LOGIN)
            with operative.FTPConnection(ftp_creds) as ftp_conn:
                files = ftp_conn.get_files(path=path, since=since)
            eq_(len(files), num_expected_files)

        # get all files
        __get_and_test(path='/flatfile', since=None, num_expected_files=3)

        # get one file - using "since"
        __get_and_test(path='/flatfile', since=datetime.datetime(2014, 1, 7, 0, 42), num_expected_files=2)

        # get zero files - using "since"
        __get_and_test(path='/flatfile', since=datetime.datetime(2014, 2, 1), num_expected_files=0)

        # get zero files - only directories in path
        __get_and_test(path='/', since=None, num_expected_files=0)
