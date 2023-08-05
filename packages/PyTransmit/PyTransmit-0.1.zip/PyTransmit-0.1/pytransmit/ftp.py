import sys
from ftplib import FTP

ftp = FTP()

__all__ = (
    'ftp_client'
)

class FTPClient():

    message_array = []

    def __init__(self):
        """
        """
        pass

    def log_message(self, message, clear=True):

        """
        Logs the message to the message_array, from where it is retrieved to display in the console.

        :param message: The message string.
        :param clear: Buffer Clearance.
        """
        if clear:
            self.message_array = message

    def get_message(self):
        """
        Returns the logged message to the console.

        :return: Returns the message.
        """
        return self.message_array

    def connect(self, server, ftp_user, ftp_password, port):
        """
        Connects the remote host to the server from the information provided to the connect method.
        If the connection is successful, the messaged will logged and displayed in the console, otherwise
        Exception is raised with the error displayed to the console and program execution halts.

        :param server: The address of the server
        :param ftp_user: The FTP user id.
        :param ftp_password: The FTP password.
        :param port: The port number.
        """
        try:
            ftp.connect(server, port)
            ftp.login(user=ftp_user, passwd=ftp_password)
            self.log_message("Connected to {0} for {1} on port {2}".format(server, ftp_user, port))
        except Exception, e:
            print(e)
            sys.exit(1)

    def make_directory(self, directory):
        """
        Creates the new directory in the connected server in the root or in the directory specified via the parameter.

        :param directory: Directory name to create.
        """
        try:
            ftp.mkd(directory)
            self.log_message("Directory {0} created successfully".format(directory))
        except Exception, e:
            print(e)
            sys.exit(1)

    def change_directory(self, directory):
        """
        CD's into the directory of our wish by providing the directory name as the parameter to it.

        :param directory: Directory name to change to it.
        """
        try:
            ftp.cwd(directory)
            self.log_message("Current Directory is now {0}".format(ftp.pwd()))
        except Exception, e:
            print(e)
            sys.exit(1)

    def directory_exists(self, directory_name):
        """
        Checks if the directory you are trying to upload the files is already present or not and if
        its already present CD's into the directory and if not, creates the directory and CD's into the
        newly created directory.

        :param directory_name: Directory name to check its existence.
        """
        try:
            new_dir_name = directory_name.strip("/")
            if new_dir_name in ftp.nlst():
                self.change_directory(directory_name)
            else:
                self.make_directory(directory_name)
                self.change_directory(directory_name)
        except Exception, e:
            print(e)
            sys.exit(1)

    def get_directory_listing(self):
        """
        Lists all the contents in the connected server or in the specified folder in the server.

        """
        data = []
        ftp.dir(data.append)
        for line in data:
            print("-", line)
        self.log_message("Listed all the files in {0}".format(ftp.pwd()))

    def upload_file(self, filename):
        """
        The file provided with filename will be uploaded to the server in the recommended
        format automatically to the desired directory.

        :param filename: Name of the file to upload.
        """
        try:
            if filename.lower().endswith(('.*')):
                with open(filename, 'r') as f:
                    ftp.storlines('STOR {}'.format(filename), f)
            else:
                with open(filename, 'rb') as f:
                    ftp.storbinary('STOR {}'.format(filename), f)
            self.log_message("Uploaded {0} in {1}".format(filename, ftp.pwd()))
        except Exception, e:
            print(e)
            sys.exit(1)

    def download_file(self, filename):
        """
        Downloads the file from the connected server, provided the name is passes as the parameter.

        :param filename: Name of the file to download.
        """
        try:
            ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)
            self.log_message("Downloaded {0}".format(filename))
        except Exception, e:
            print(e)
            sys.exit(1)

    def __del__(self):
        """
        Closes the FTP connection.
        """
        ftp.close()


ftp_client = FTPClient