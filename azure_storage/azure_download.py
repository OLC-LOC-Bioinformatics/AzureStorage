#!/usr/bin/env python
from azure_storage.methods import client_prep, create_blob_client, create_parent_parser, setup_arguments
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import azure
import sys
import os


class AzureContainerDownload(object):

    def main(self):
        self.container_name, self.connect_str, self.blob_service_client, self.container_client = \
            client_prep(container_name=self.container_name,
                        passphrase=self.passphrase,
                        account_name=self.account_name,
                        create=False)
        self.download_container(container_client=self.container_client,
                                blob_service_client=self.blob_service_client,
                                container_name=self.container_name,
                                output_path=self.output_path)

    @staticmethod
    def download_container(container_client, blob_service_client, container_name, output_path):
        """
        Download the container from Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param output_path: type str: Name and path of the folder into which the container is to be downloaded
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        try:
            # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
            logging.getLogger().setLevel(logging.WARNING)
            for blob_file in generator:
                # Create the blob client
                blob_client = create_blob_client(blob_service_client=blob_service_client,
                                                 container_name=container_name,
                                                 blob_file=blob_file)
                # Extract the folder structure of the blob e.g. 220202-m05722/InterOp
                folder_structure = os.path.split(os.path.dirname(blob_file.name))
                # Determine the path to output the file. Join the supplied path, the name of the container and
                # the joined (splatted) folder structure. Logic: https://stackoverflow.com/a/14826889
                download_path = os.path.join(output_path, container_name, os.path.join(*folder_structure))
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
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit

    def __init__(self, container_name, output_path, account_name, passphrase):
        # Set the container name variable
        self.container_name = container_name
        # Output path
        if output_path.startswith('~'):
            self.output_path = os.path.abspath(os.path.expanduser(os.path.join(output_path)))
        else:
            self.output_path = os.path.abspath(os.path.join(output_path))
        # Create the output path
        try:
            os.makedirs(self.output_path, exist_ok=True)
        except PermissionError:
            logging.error(f'Could not use the supplied output path: {self.output_path}')
            raise SystemExit
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


class AzureDownload(object):

    def main(self):
        self.container_name, self.connect_str, self.blob_service_client, self.container_client = \
            client_prep(container_name=self.container_name,
                        passphrase=self.passphrase,
                        account_name=self.account_name,
                        create=False)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            self.download_file(container_client=self.container_client,
                               blob_service_client=self.blob_service_client,
                               container_name=self.container_name,
                               object_name=self.object_name,
                               output_path=self.output_path)
        elif self.category == 'folder':
            self.download_folder(container_client=self.container_client,
                                 blob_service_client=self.blob_service_client,
                                 container_name=self.container_name,
                                 object_name=self.object_name,
                                 output_path=self.output_path)
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')
            raise SystemExit

    @staticmethod
    def download_file(container_client, blob_service_client, container_name, object_name, output_path):
        """
        Download the specified file from Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param object_name: type str: Name and path of file to download from Azure storage
        :param output_path: type str: Name and path of the folder into which the file is to be downloaded
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Create a boolean to determine if the file has been located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        try:
            for blob_file in generator:
                # Filter for the blob name
                if blob_file.name == object_name:
                    # Update the file presence variable
                    present = True
                    # Create the blob client
                    blob_client = create_blob_client(blob_service_client=blob_service_client,
                                                     container_name=container_name,
                                                     blob_file=blob_file)
                    # Set the name of file by removing any path information
                    file_name = os.path.basename(blob_file.name)
                    # Finally, set the name and the path of the output file
                    download_file = os.path.join(output_path, file_name)
                    # Open the target output file as binary
                    with open(download_file, 'wb') as downloaded_file:
                        # Write the data from the blob client to the local file
                        downloaded_file.write(blob_client.download_blob().readall())
            # Send an error to the user that the file could not be found
            if not present:
                logging.error(f'Could not locate the desired file {object_name} in {container_name}')
                raise SystemExit
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit

    @staticmethod
    def download_folder(container_client, blob_service_client, container_name, object_name, output_path):
        """
        Download the specified folder from Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param object_name: type str: Name and path of folder to download from Azure storage
        :param output_path: type str: Name and path of the folder into which the folder is to be downloaded
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Boolean to track whether the folder was located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        try:
            for blob_file in generator:
                # Create the path of the file by adding the container name to the path of the file
                blob_path = os.path.join(container_name, os.path.split(blob_file.name)[0])
                # Ensure that the supplied folder path is present in the blob path
                if os.path.normpath(object_name) in os.path.normpath(blob_path):
                    # Update the folder presence boolean
                    present = True
                    # Create the blob client
                    blob_client = create_blob_client(blob_service_client=blob_service_client,
                                                     container_name=container_name,
                                                     blob_file=blob_file)
                    # Determine the path to output the file. Join the supplied path and the path of the blob
                    download_path = os.path.join(output_path, os.path.join(os.path.dirname(blob_file.name)))
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
            # Send an error to the user that the folder could not be found
            if not present:
                logging.error(f'Could not locate the desired folder {object_name} in container {container_name}')
                raise SystemExit
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit

    def __init__(self, object_name, container_name, output_path, account_name, passphrase, category):
        # Set the name of the file/folder to download
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Output path
        if output_path.startswith('~'):
            self.output_path = os.path.abspath(os.path.expanduser(os.path.join(output_path)))
        else:
            self.output_path = os.path.abspath(os.path.join(output_path))
        # Create the output path
        try:
            os.makedirs(self.output_path, exist_ok=True)
        except PermissionError:
            logging.error(f'Could not use the supplied output path: {self.output_path}')
            raise SystemExit
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


def container_download(args):
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
                                    container_name=args.container_name,
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
                                      container_name=args.container_name,
                                      output_path=args.output_path,
                                      account_name=args.account_name,
                                      passphrase=args.passphrase,
                                      category='folder')
    folder_downloader.main()


def cli():
    parser = ArgumentParser(description='Download containers/files/folders from Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument('-o', '--output_path',
                               default=os.getcwd(),
                               help='Name and path of directory in which the outputs are to be saved. Default is '
                                    'your $CWD')
    # Container downloading parser
    container_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='container',
                                                description='Download a container from Azure storage',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Download a container from Azure storage')
    container_subparser.set_defaults(func=container_download)
    # Blob (file) downloading subparser
    file_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='file',
                                           description='Download a file from Azure storage',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Download a file from Azure storage')
    file_subparser.add_argument('-f', '--file',
                                type=str,
                                required=True,
                                help='Name of file to download from Azure storage.'
                                     'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
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
                                  help='Name of the folder to download from Azure storage e.g. InterOp')
    folder_subparser.set_defaults(func=folder_download)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Download complete')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
