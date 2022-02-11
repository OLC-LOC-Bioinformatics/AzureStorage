#!/usr/bin/env python
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import os

# Communication string storing imports
import getpass
import keyring

# Azure-related imports
from azure.storage.blob import BlobServiceClient
import azure


class DownloadMethods:

    @staticmethod
    def set_connection_string(passphrase, account_name):
        """
        Prompt the user for the connection string, and store it the system keyring
        Uses logic from https://stackoverflow.com/a/31882203
        :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
        :param account_name: type str: Name of the Azure storage account
        :return: connect_str: String of the connection string
        """
        # Prompt the user for the connection string. Use decode to convert from bytes. Use getpass, so the plain text
        # password isn't printed to the screen
        connect_str = getpass.getpass(prompt='Please enter the connection string for your Azure storage account:\n')\
            .encode('utf-8').decode()
        # Set the password in the keyring. Use the passphrase as the service ID, the account name as the username,
        # and the connection string as the password
        keyring.set_password(passphrase, account_name, connect_str)
        return connect_str

    @staticmethod
    def extract_connection_string(passphrase, account_name):
        """
        Extract the connection string from the keyring using the account name and passphrase
        :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
        :param account_name: type str: Name of the Azure storage account
        connect_str: String of the connection string
        """
        # Use the passphrase and the account name to extract the connection string from the keyring
        connect_str = keyring.get_password(passphrase,
                                           account_name)
        # If the connection string can't be found in the keyring using the supplied passphrase, prompt the user for
        # the passphrase, and store it
        if not connect_str:
            logging.warning(f'Connection string linked to the provided passphrase: {passphrase} and account name: '
                            f'{account_name} not found in the system keyring. You will now be prompted to enter it.')
            connect_str = DownloadMethods.set_connection_string(passphrase=passphrase,
                                                                account_name=account_name)
        return connect_str

    @staticmethod
    def create_blob_service_client(connect_str):
        """
        Create a blob service client using the connection string
        :param connect_str: type str: Connection string for Azure storage
        :return: blob_service_client: type BlobServiceClient
        """
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        return blob_service_client

    @staticmethod
    def create_container_client(blob_service_client, container_name):
        """
        Create a container-specific client from the blob service client
        :param blob_service_client: type: BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :return: container_client: type BlobServiceClient.ContainerClient:
        """
        # Create the container client from the blob service client with the get container client method
        # and the container name
        container_client = blob_service_client.get_container_client(container_name)
        return container_client

    @staticmethod
    def create_blob_client(blob_service_client, container_name, blob_file):
        """
        Create a blob-specific client
        :param blob_service_client: type: BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param blob_file: type iterable from BlobServiceClient.ContainerClient.list_blobs
        :return: blob_client: type BlobServiceClient.BlobClient
        """
        # Create a blob client for the current blob
        blob_client = blob_service_client.get_blob_client(container=container_name,
                                                          blob=blob_file)
        return blob_client


class AzureContainerDownload(object):

    def main(self):
        self.connect_str = DownloadMethods.extract_connection_string(passphrase=self.passphrase,
                                                                     account_name=self.account_name)
        self.blob_service_client = DownloadMethods.create_blob_service_client(connect_str=self.connect_str)
        self.container_client = DownloadMethods.create_container_client(blob_service_client=self.blob_service_client,
                                                                        container_name=self.container_name)
        self.download_container()

    def download_container(self):
        """
        Download the container from Azure storage
        """
        # Create a generator containing all the blobs in the container
        generator = self.container_client.list_blobs()
        try:
            # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
            logging.getLogger().setLevel(logging.WARNING)
            for blob_file in generator:
                # Create the blob client
                blob_client = DownloadMethods.create_blob_client(blob_service_client=self.blob_service_client,
                                                                 container_name=self.container_name,
                                                                 blob_file=blob_file)
                # Extract the folder structure of the blob e.g. 220202-m05722/InterOp
                folder_structure = os.path.split(os.path.dirname(blob_file.name))
                # Determine the path to output the file. Join the supplied path, the name of the container and
                # the joined (splatted) folder structure. Logic: https://stackoverflow.com/a/14826889
                download_path = os.path.join(self.output_path, self.container_name, os.path.join(*folder_structure))
                # Create the path if required
                os.makedirs(download_path, exist_ok=True)
                # Set the name of file by removing any path information
                file_name = os.path.basename(blob_file.name)
                # Finally, set the name and the path of the output file
                download_file = os.path.join(download_path, file_name)
                # Open the target output file as binary
                with open(download_file, 'wb') as downloaded_file:
                    # Write the data from the blob client to the local file
                    downloaded_file.write(blob_client.download_blob().readall())
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {self.container_name}, does not exist.')

    def __init__(self, container_name, output_path, account_name, passphrase):
        # Set the container name variable
        self.container_name = container_name
        # Output path
        if output_path.startswith('~'):
            self.output_path = os.path.abspath(os.path.expanduser(os.path.join(output_path)))
        else:
            self.output_path = os.path.abspath(os.path.join(output_path))
        # Create the output path
        os.makedirs(self.output_path, exist_ok=True)
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


class AzureDownload(object):

    def main(self):
        self.connect_str = DownloadMethods.extract_connection_string(passphrase=self.passphrase,
                                                                     account_name=self.account_name)
        self.blob_service_client = DownloadMethods.create_blob_service_client(connect_str=self.connect_str)
        self.extract_container_name()
        self.container_client = DownloadMethods.create_container_client(blob_service_client=self.blob_service_client,
                                                                        container_name=self.container_name)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            self.download_blob()
        elif self.category == 'folder':
            self.download_folder()
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')

    def extract_container_name(self):
        """
        Extract the name of the container in which the blob is to be downloaded
        """
        # Split the container name from the file name (and possibly path). Use the first entry.
        # For a blob: 220202-m05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz yields 220202-m05722
        # For a folder: 220202-m05722/InterOp yields 220202-m05722
        self.container_name = self.object_name.split('/')[0]

    def download_blob(self):
        """
        Download the specified file from Azure storage
        """
        # Create a generator containing all the blobs in the container
        generator = self.container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        for blob_file in generator:
            # Filter for the blob name
            if os.path.basename(blob_file.name) == os.path.basename(self.object_name):
                # Update the blob presence variable
                present = True
                # Create the blob client
                blob_client = DownloadMethods.create_blob_client(blob_service_client=self.blob_service_client,
                                                                 container_name=self.container_name,
                                                                 blob_file=blob_file)
                # Set the name of file by removing any path information
                file_name = os.path.basename(blob_file.name)
                # Finally, set the name and the path of the output file
                download_file = os.path.join(self.output_path, file_name)
                # Open the target output file as binary
                with open(download_file, 'wb') as downloaded_file:
                    # Write the data from the blob client to the local file
                    downloaded_file.write(blob_client.download_blob().readall())
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired blob {self.object_name}')
            quit()

    def download_folder(self):
        """
        Download the specified folder from Azure storage
        """
        # Create a generator containing all the blobs in the container
        generator = self.container_client.list_blobs()
        # Boolean to track whether the folder was located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        for blob_file in generator:
            blob_path = os.path.join(self.container_name, os.path.split(blob_file.name)[0])
            if os.path.normpath(blob_path) == os.path.normpath(self.object_name):
                # Update the folder presence boolean
                present = True
                # Create the blob client
                blob_client = DownloadMethods.create_blob_client(blob_service_client=self.blob_service_client,
                                                                 container_name=self.container_name,
                                                                 blob_file=blob_file)
                # Extract the folder structure of the blob e.g. 220202-m05722/InterOp
                folder_structure = os.path.split(os.path.dirname(blob_file.name))
                # Determine the path to output the file. Join the supplied path and the folder name
                download_path = os.path.join(self.output_path, folder_structure[-1])
                # Create the path if required
                os.makedirs(download_path, exist_ok=True)
                # Set the name of file by removing any path information
                file_name = os.path.basename(blob_file.name)
                # Finally, set the name and the path of the output file
                download_file = os.path.join(download_path, file_name)
                # Open the target output file as binary
                with open(download_file, 'wb') as downloaded_file:
                    # Write the data from the blob client to the local file
                    downloaded_file.write(blob_client.download_blob().readall())
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired folder {self.object_name}')

    def __init__(self, object_name, output_path, account_name, passphrase, category):
        # Set the name of the file/folder to download
        self.object_name = object_name
        # Output path
        if output_path.startswith('~'):
            self.output_path = os.path.abspath(os.path.expanduser(os.path.join(output_path)))
        else:
            self.output_path = os.path.abspath(os.path.join(output_path))
        # Create the output path
        os.makedirs(self.output_path, exist_ok=True)
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.category = category
        self.connect_str = str()
        self.container_name = str()
        self.blob_service_client = None
        self.container_client = None


def credentials(args):
    """
    Run the credentials setting methods
    :param args: type ArgumentParser arguments
    """
    logging.info('Setting Azure storage credentials')
    # Run the credentials setting method
    DownloadMethods.set_connection_string(passphrase=args.passphrase,
                                          account_name=args.account_name)
    logging.info('Successfully entered credentials into keyring')


def container(args):
    """
    Run the AzureContainerDownload method
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Downloading Azure container {args.name}')
    # Create the container download object
    container_downloader = AzureContainerDownload(container_name=args.name,
                                                  output_path=args.output_path,
                                                  account_name=args.account_name,
                                                  passphrase=args.passphrase)
    container_downloader.main()


def blob(args):
    """
    Run the AzureDownload class for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Downloading {args.blob} from Azure storage')
    # Create the blob download object
    blob_downloader = AzureDownload(object_name=args.blob,
                                    output_path=args.output_path,
                                    account_name=args.account_name,
                                    passphrase=args.passphrase,
                                    category='file')
    blob_downloader.main()


def folder(args):
    """
    Run the AzureDownload class for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Downloading contents of folder {args.folder} from Azure storage')
    folder_downloader = AzureDownload(object_name=args.folder,
                                      output_path=args.output_path,
                                      account_name=args.account_name,
                                      passphrase=args.passphrase,
                                      category='folder')
    folder_downloader.main()


def cli():
    parser = ArgumentParser(description='Download containers from Azure storage')
    subparsers = parser.add_subparsers(title='Available functionality')
    # Create a parental parser from which the
    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument('-a', '--account_name',
                               required=True,
                               type=str,
                               help='Name of the Azure storage account')
    parent_parser.add_argument('-p', '--passphrase',
                               default='AzureDownload',
                               type=str,
                               help='The passphrase to use when encrypting the azure storage-specific connection '
                                    'string to the system keyring. Default is "AzureDownload".')
    parent_parser.add_argument('-v', '--verbosity',
                               choices=['debug', 'info', 'warning', 'error', 'critical'],
                               default='info',
                               help='Set the logging level. Default is info.')
    # Credentials creating/modifying subparser
    credentials_subparser = subparsers.add_parser(parents=[parent_parser],
                                                  name='credentials',
                                                  description='Set or modify Azure storage credentials in the system '
                                                              'keyring',
                                                  formatter_class=RawTextHelpFormatter,
                                                  help='Set or modify Azure storage credentials in the system keyring')
    credentials_subparser.set_defaults(func=credentials)
    # Container downloading parser
    container_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='container',
                                                description='Download a container from Azure storage',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Download a container from Azure storage')
    container_subparser.add_argument('-n', '--name',
                                     required=True,
                                     type=str,
                                     default=str(),
                                     help='Name of container to download from Azure storage. If you want to specify '
                                          'a nested container, use "/" to separate the containers e.g. '
                                          'sequencing-runs/220202-m05722')
    container_subparser.add_argument('-o', '--output_path',
                                     default=os.getcwd(),
                                     help='Name and path of directory in which the container is to be saved. Note that '
                                          'if you specified a nested container, only that will be used e.g. '
                                          '$output_path/220202-m05722 will be the location of the container whether '
                                          'you specified sequencing-runs/220202-m05722 or 220202-m05722 as the name '
                                          'of the container.')
    container_subparser.set_defaults(func=container)
    # Blob (file) downloading subparser
    blob_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='blob',
                                           description='Download a blob from Azure storage',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Download a blob from Azure storage')
    blob_subparser.add_argument('-b', '--blob',
                                type=str,
                                required=True,
                                help='Path of blob file to download from Azure storage. Note that this includes'
                                     'the container name '
                                     'e.g. 220202-m05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    blob_subparser.add_argument('-o', '--output_path',
                                default=os.getcwd(),
                                help='Name and path of directory in which the blob is to be saved.')
    blob_subparser.set_defaults(func=blob)
    # Folder downloading subparser
    folder_subparser = subparsers.add_parser(parents=[parent_parser],
                                             name='folder',
                                             description='Download a folder from Azure storage',
                                             formatter_class=RawTextHelpFormatter,
                                             help='Download a folder from Azure storage')
    folder_subparser.add_argument('-f', '--folder',
                                  type=str,
                                  required=True,
                                  help='Name of the container and folder to download from Azure storage '
                                       'e.g. sequencing-runs/220202-m05722/InterOp')
    folder_subparser.add_argument('-o', '--output_path',
                                  default=os.getcwd(),
                                  help='Name and path of directory in which the blob is to be saved.')
    folder_subparser.set_defaults(func=folder)
    # Get the arguments into an object
    arguments = parser.parse_args()
    # Set up logging
    coloredlogs.DEFAULT_LEVEL_STYLES = {'debug': {'bold': True, 'color': 'green'},
                                        'info': {'bold': True, 'color': 'blue'},
                                        'warning': {'bold': True, 'color': 'yellow'},
                                        'error': {'bold': True, 'color': 'red'},
                                        'critical': {'bold': True, 'background': 'red'}
                                        }
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
    coloredlogs.install(level=arguments.verbosity.upper())
    # Run the appropriate function for each sub-parser.
    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    # If the 'func' attribute doesn't exist, display the basic help
    else:
        parser.parse_args(['-h'])
    coloredlogs.install(level=arguments.verbosity.upper())
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    logging.info('Download complete')



if __name__ == '__main__':
    cli()
