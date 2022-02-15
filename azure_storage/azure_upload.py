#!/usr/bin/env python
from azure_storage.methods import create_blob_client, create_container, create_container_client, \
    create_blob_service_client, extract_connection_string, setup_arguments

from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import azure
import os


class AzureUpload(object):

    def main(self):
        self.connect_str = extract_connection_string(passphrase=self.passphrase,
                                                     account_name=self.account_name)
        self.blob_service_client = create_blob_service_client(connect_str=self.connect_str)

        self.container_client = create_container_client(blob_service_client=self.blob_service_client,
                                                        container_name=self.container_name)
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            # If the container doesn't exist, run the container creation method, and re-run the upload
            try:
                self.upload_file()
            except azure.core.exceptions.ResourceNotFoundError:
                self.container_client = create_container(blob_service_client=self.blob_service_client,
                                                         container_name=self.container_name)
                self.upload_file()
        elif self.category == 'folder':
            try:
                self.upload_folder()
            except azure.core.exceptions.ResourceNotFoundError:
                self.container_client = create_container(blob_service_client=self.blob_service_client,
                                                         container_name=self.container_name)
                self.upload_folder()
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')

    def upload_file(self):
        """
        Upload a single file to Azure storage
        """
        # Extract the name of the file from the provided name, as it may include the path
        file_name = os.path.basename(self.object_name)
        # Create a blob client for this file in the container in which it will be stored
        blob_client = create_blob_client(blob_service_client=self.blob_service_client,
                                         container_name=self.container_name,
                                         blob_file=file_name)
        # Attempt to upload the file to the specified container.
        try:
            # Read in the file data as binary
            with open(self.object_name, "rb") as data:
                # Upload the file data to the blob
                blob_client.upload_blob(data)
        # If a file with that name already exists in that container, warn the user
        except azure.core.exceptions.ResourceExistsError:
            logging.error(f'The file {self.object_name} already exists in container {self.container_name} in '
                          f'storage account {self.account_name}')

    def upload_folder(self):
        """
        Upload all the files (and sub-folders as applicable) in the specified folder to Azure storage
        """
        # Use os.walk to find all the files and folders in the supplied directory
        for root, dirs, files in os.walk(self.object_name):
            # Determine the relative path for the current sub-folder to the supplied root folder by creating a list
            # from the splitting of the root path using the OS-appropriate separator (os.sep) and slicing the list to
            # remove the first entry (the root) e.g. outputs/files/reports, where 'outputs/files' is the supplied
            # directory, would return 'files/reports'
            rel_path = os.path.join(os.sep.join(root.split(os.sep)[1:]))
            # Using the same logic as above, extract the root directory e.g. outputs/files/reports, where
            # 'outputs/files' is the supplied  directory, would return 'outputs'
            root_path = root.split(os.sep)[0]
            print(f'r, {root}, rel {rel_path}, root path {root_path}')
            for file_name in files:
                # Add the file name to the calculated relative path to set the name of the blob in Azure storage e.g.
                # files/reports/summary.tsv
                upload_file = os.path.join(rel_path, file_name)
                # Create a blob client for this file using the supplied container name
                blob_client = create_blob_client(blob_service_client=self.blob_service_client,
                                                 container_name=self.container_name,
                                                 blob_file=upload_file)
                # Attempt to upload the file to the specified container
                try:
                    # Re-add the root path to find the file on the local system
                    with open(os.path.join(root_path, upload_file), "rb") as data:
                        # Upload the file to Azure storage
                        blob_client.upload_blob(data)
                # Log an error if a file with that name already exists in the specified container
                except azure.core.exceptions.ResourceExistsError:
                    logging.error(f'The file {self.object_name} already exists in container {self.container_name} in '
                                  f'storage account {self.account_name}')

    def __init__(self, object_name, container_name, account_name, passphrase, category):
        # Set the name of the file/folder to upload
        self.object_name = object_name
        if category == 'file':
            try:
                assert os.path.isfile(self.object_name)
            except AssertionError:
                logging.error(f'Cannot locate the specified file to upload: {self.object_name}')
                quit()
        else:
            try:
                assert os.path.isdir(self.object_name)
            except AssertionError:
                logging.error(f'Cannot located the specified folder to upload: {self.object_name}')
                quit()
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.container_name = container_name
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


def file_upload(args):
    """
    Run the AzureUpload class for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Uploading {args.file} to container {args.container_name} in Azure storage account '
                 f'{args.account_name}')
    # Create the file_upload object
    file_uploader = AzureUpload(object_name=args.file,
                                account_name=args.account_name,
                                container_name=args.container_name,
                                passphrase=args.passphrase,
                                category='file')
    file_uploader.main()


def folder_upload(args):
    """
    Run the AzureUpload class for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Uploading folder (and its contents) {args.folder} to container {args.container_name} in Azure '
                 f'storage account {args.account_name}')
    folder_uploader = AzureUpload(object_name=args.folder,
                                  account_name=args.account_name,
                                  container_name=args.container_name,
                                  passphrase=args.passphrase,
                                  category='folder')
    folder_uploader.main()


def cli():
    parser = ArgumentParser(description='Upload files or folders to Azure storage')
    subparsers = parser.add_subparsers(title='Available functionality')
    # Create a parental parser that can be inherited by subparsers
    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument('-c', '--container_name',
                               required=True,
                               type=str,
                               default=str(),
                               help='Name of the Azure storage container to which the files are to be uploaded. '
                                    'If you want to specify a nested container, use "/" to separate the containers '
                                    'e.g. sequencing-runs/220202-m05722')
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
    # File upload subparser
    file_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='file',
                                           description='Upload a file to Azure storage',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Upload a file to Azure storage')
    file_subparser.add_argument('-f', '--file',
                                type=str,
                                required=True,
                                help='Name and path of the file to upload to Azure storage.'
                                     'e.g. /mnt/sequences/220202_M05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    file_subparser.set_defaults(func=file_upload)
    # Folder upload subparser
    folder_subparser = subparsers.add_parser(parents=[parent_parser],
                                             name='folder',
                                             description='Upload a folder to Azure storage',
                                             formatter_class=RawTextHelpFormatter,
                                             help='Upload a folder to Azure storage')
    folder_subparser.add_argument('-f', '--folder',
                                  type=str,
                                  required=True,
                                  help='Name and path of the folder to upload to Azure storage.'
                                       'e.g. /mnt/sequences/220202_M05722/')
    folder_subparser.set_defaults(func=folder_upload)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Upload complete')


if __name__ == '__main__':
    cli()
