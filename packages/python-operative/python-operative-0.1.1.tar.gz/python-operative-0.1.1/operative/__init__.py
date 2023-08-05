import ftplib
import StringIO
from datetime import datetime


class FTPCredentials(object):

    """
    Represents the FTP credentials needed for establishing an FTP connection

    """

    def __init__(self, host, username, password, port=None):
        """
        Initializes the object and sets attributes.

        :param str host: The hostname of the FTP server
        :param str user: The username for the FTP server
        :param str passwd: The password for the FTP user
        :param int port: The port number for the FTP server

        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port


class FTPFile(object):

    """
    Represents a file in an FTP directory

    """

    def __init__(self, name, last_modified):
        """
        Initializes the object and sets attributes.

        :param str name: The name of the file
        :param datetime last_modified: The datetime that the file was last modified

        """
        self.name = name
        self.last_modified = last_modified


class FTPConnection(object):

    """
    Represents an open FTP connection to an Operative Flat File Production System

    Be sure to use this object in a "with" block to ensure that open connections are always closed.

    """

    def __init__(self, ftp_credentials):
        """
        Initializes the object and sets attributes

        :param ftp_credentials FTPCredentials: The credentials needed to establish a connection

        """
        self._ftp = ftplib.FTP()
        self.ftp_credentials = ftp_credentials

    def __enter__(self):
        """
        Provides functionality for "with" statement blocks.
        Establishes the FTP connection.

        :rtype FTPConnection:

        """
        self._establish_connection()
        return self

    def __exit__(self, type, value, traceback):
        """
        Cleans up the open connection when exiting a "with" statement

        """
        self._close_connection()

    def _establish_connection(self):
        """
        Establishes the FTP connection

        """
        ftp_connect = dict(host=self.ftp_credentials.host)
        if self.ftp_credentials.port:
            ftp_connect['port'] = self.ftp_credentials.port
        ftp_account = dict(user=self.ftp_credentials.username, passwd=self.ftp_credentials.password)

        self._ftp.connect(**ftp_connect)
        self._ftp.login(**ftp_account)

    def _close_connection(self):
        """
        Closes the open connection, if it exists

        """
        if getattr(self, '_ftp', False):
            self._ftp.close()

    def get_files(self, path=None, since=None):
        """
        Gets files from an FTP directory

        :param str path: The path of the FTP directory
        :param datetime since: Min datetime to retrieve files from

        :rtype list(FTPFile):

        """
        def __parse_file_descriptors(file_descriptors):
            """
            Accepts a list of file descriptors and returns a list of FTPFile objects with just names and modified dates

            :param list(str) file_descriptors: A list of file descriptors from the FTP server

            """
            files = []
            for fd in file_descriptors:
                chunks = fd.split(';')
                name = chunks.pop().strip()
                file_metadata = dict(map(lambda chunk: chunk.lower().split('='), chunks))
                if file_metadata['type'] == 'file':
                    this_file = FTPFile(**{'name': name,
                                           'last_modified': datetime.strptime(str(file_metadata['modify']), '%Y%m%d%H%M%S')})
                    files.append(this_file)
            return files

        def __download_file_data(file_path):
            """
            Gets a file from the FTP server

            :param str file_path: The full path of the file, with filename included

            :rtype StringIO:

            """
            file_io = StringIO.StringIO()
            self._ftp.retrbinary('RETR %s' % file_path, file_io.write)
            return file_io

        file_descriptors = []
        if path:
            self._ftp.cwd(path)
        self._ftp.retrlines('MLSD', file_descriptors.append)
        ftp_files = __parse_file_descriptors(file_descriptors)
        ftp_files = filter(lambda f: not(since) or f.last_modified > since, ftp_files)
        for ftp_file in ftp_files:
            ftp_file.data = __download_file_data(path + '/' + ftp_file.name)
        return ftp_files
