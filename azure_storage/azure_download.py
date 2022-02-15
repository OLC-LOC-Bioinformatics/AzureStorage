#!/usr/bin/env python
from azure_storage.methods import create_blob_client, create_container_client, create_blob_service_client,\
    extract_connection_string, extract_container_name, setup_arguments
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import azure
import os


class AzureContainerDownload(object):

    def main(self):
        self.connect_str = extract_connection_string(passphrase=self.passphrase,
                                                     account_name=self.account_name)
        self.blob_service_client = create_blob_service_client(connect_str=self.connect_str)
        self.container_client = create_container_client(blob_service_client=self.blob_service_client,
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
                blob_client = create_blob_client(blob_service_client=self.blob_service_client,
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
        try:
            assert os.path.isdir(self.output_path)
        except AssertionError:
            logging.error(f'Could not use the supplied output path: {self.output_path}')
            quit()
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
        self.connect_str = extract_connection_string(passphrase=self.passphrase,
                                                     account_name=self.account_name)
        self.blob_service_client = create_blob_service_client(connect_str=self.connect_str)
        self.container_name = extract_container_name(object_name=self.object_name)
        self.container_client = create_container_client(blob_service_client=self.blob_service_client,
                                                        container_name=self.container_name)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            self.download_file()
        elif self.category == 'folder':
            self.download_folder()
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')

    def download_file(self):
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
            if os.path.join(self.container_name, blob_file.name) == self.object_name:
                # Update the blob presence variable
                present = True
                # Create the blob client
                blob_client = create_blob_client(blob_service_client=self.blob_service_client,
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
            logging.error(f'Could not locate the desired file {self.object_name}')
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
            # Create the path of the file by adding the container name to the path of the file
            blob_path = os.path.join(self.container_name, os.path.split(blob_file.name)[0])
            # Ensure that the supplied folder path is present in the blob path
            if os.path.normpath(self.object_name) in os.path.normpath(blob_path):
                # Update the folder presence boolean
                present = True
                # Create the blob client
                blob_client = create_blob_client(blob_service_client=self.blob_service_client,
                                                 container_name=self.container_name,
                                                 blob_file=blob_file)
                # Determine the path to output the file. Join the supplied path and the path of the blob
                download_path = os.path.join(self.output_path, os.path.join(os.path.dirname(blob_file.name)))
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
            quit()

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


def container(args):
    """
    Run the AzureContainerDownload method
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Downloading Azure container {args.container_name}')
    # Create the container download object
    container_downloader = AzureContainerDownload(container_name=args.container_name,
                                                  output_path=args.output_path,
                                                  account_name=args.account_name,
                                                  passphrase=args.passphrase)
    container_downloader.main()


def file_download(args):
    """
    Run the AzureDownload class for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Downloading {args.file} from Azure storage')
    # Create the file download object
    file_downloader = AzureDownload(object_name=args.file,
                                    output_path=args.output_path,
                                    account_name=args.account_name,
                                    passphrase=args.passphrase,
                                    category='file')
    file_downloader.main()


def folder_download(args):
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
    parser = ArgumentParser(description='Download containers/files/folders from Azure storage')
    subparsers = parser.add_subparsers(title='Available functionality')
    # Create a parental parser that can be inherited by the subparsers
    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument('-a', '--account_name',
                               required=True,
                               type=str,
                               help='Name of the Azure storage account')
    parent_parser.add_argument('-p', '--passphrase',
                               default='AzureStorage',
                               type=str,
                               help='The passphrase to use when encrypting the azure storage-specific connection '
                                    'string to the system keyring. Default is "AzureStorage".')
    parent_parser.add_argument('-v', '--verbosity',
                               choices=['debug', 'info', 'warning', 'error', 'critical'],
                               default='info',
                               help='Set the logging level. Default is info.')
    # Container downloading parser
    container_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='container',
                                                description='Download a container from Azure storage',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Download a container from Azure storage')
    container_subparser.add_argument('-c', '--container_name',
                                     required=True,
                                     type=str,
                                     default=str(),
                                     help='Name of container to download from Azure storage.')
    container_subparser.add_argument('-o', '--output_path',
                                     default=os.getcwd(),
                                     help='Name and path of directory in which the container is to be saved. Note that '
                                          'if you specified a nested container, only that will be used e.g. '
                                          '$output_path/220202-m05722 will be the location of the container whether '
                                          'you specified sequencing-runs/220202-m05722 or 220202-m05722 as the name '
                                          'of the container.')
    container_subparser.set_defaults(func=container)
    # Blob (file) downloading subparser
    file_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='file',
                                           description='Download a file from Azure storage',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Download a blob from Azure storage')
    file_subparser.add_argument('-f', '--file',
                                type=str,
                                required=True,
                                help='Path of blob file to download from Azure storage. Note that this includes'
                                     'the container name '
                                     'e.g. 220202-m05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    file_subparser.add_argument('-o', '--output_path',
                                default=os.getcwd(),
                                help='Name and path of directory in which the file is to be saved.')
    file_subparser.set_defaults(func=file_download)
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
                                  help='Name and path of directory in which the folder is to be saved.')
    folder_subparser.set_defaults(func=folder_download)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Download complete')


if __name__ == '__main__':
    cli()
