import csv

from operative import FTPConnection


class Report(object):

    """
    Represents an operative report.

    """

    class ReportFile(object):

        """
        Represents an individual report file.

        """

        def __init__(self, raw_file, data):
            """
            Initializes the object and set attributes.

            :param FTPFile raw_file: The raw file from the FTP server.
            :param [OperativeModel] data: A list of models parsed from the raw file.

            """
            self.raw_file = raw_file
            self.data = data

    def __init__(self):
        """
        Initializes the object and sets attributes.

        """
        self.reports = []

    def get_report_files(self, ftp_credentials, ftp_path, since=None):
        """
        Retrieves a list of objects representing the reports available on the FTP server.

        :param FTPCredentials ftp_credentials: The credentials needed to establish an FTP connection
        :param str ftp_path: The path to get the reports from
        :param datetime since: Min datetime to retrieve reports from

        """

        def __parse_csv(csv_file):
            """
            Parses a csv file into a list of dicts.
            We utilize the parse_row function which has been delegated to the child class.

            :param StringIO csv_file: An open csv file

            :rtype list(dict): A list of dicts representing the data from the report

            """
            return [self.parse_row(row) for row in csv.DictReader(csv_file)]

        with FTPConnection(ftp_credentials) as ftp_conn:
            self.report_files = [self.ReportFile(raw_file=f, data=__parse_csv(f.data.getvalue().split('\n'))) for f in ftp_conn.get_files(path=ftp_path, since=since)]

        return self.report_files
