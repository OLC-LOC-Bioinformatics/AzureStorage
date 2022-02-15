#!/usr/bin/env python
# Local imports
from azure_storage.methods import create_blob_client, create_container_client, create_blob_service_client,\
    extract_account_key, extract_connection_string, extract_container_name, setup_arguments, write_sas
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import datetime
import logging
import azure
import os


class AzureContainerSAS(object):

    def main(self):
        self.connect_str = extract_connection_string(passphrase=self.passphrase,
                                                     account_name=self.account_name)
        self.account_key = extract_account_key(connect_str=self.connect_str)
        self.blob_service_client = create_blob_service_client(connect_str=self.connect_str)
        self.container_client = create_container_client(blob_service_client=self.blob_service_client,
                                                        container_name=self.container_name)
        self.container_sas()
        write_sas(verbosity=self.verbosity,
                  output_file=self.output_file,
                  sas_urls=self.sas_urls)

    def container_sas(self):
        """
        Create SAS for all files in the container
        """
        # Create a generator containing all the blobs in the container
        generator = self.container_client.list_blobs()
        try:
            # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
            logging.getLogger().setLevel(logging.WARNING)
            for blob_file in generator:
                # Set the name of file by removing any path information
                file_name = os.path.basename(blob_file.name)
                # Create the blob SAS. Use a start time 15 minutes in the past, and the requested expiry
                sas_token = generate_blob_sas(
                    account_name=self.account_name,
                    container_name=self.container_name,
                    blob_name=blob_file.name,
                    account_key=self.account_key,
                    permission=BlobSasPermissions(read=True),
                    start=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
                    expiry=datetime.datetime.utcnow() + datetime.timedelta(days=self.expiry))
                # Generate the SAS URL using the account name, the domain, the container name, the blob name, and the
                # SAS token in the following format:
                # 'https://' + account_name + '.blob.core.windows.net/' + container_name + '/' + blob_name + '?' + blob
                self.sas_urls[file_name] = \
                    f'https://{self.account_name}.blob.core.windows.net/{self.container_name}/' \
                    f'{blob_file.name}?{sas_token}'
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {self.container_name}, does not exist.')

    def __init__(self, container_name, output_file, account_name, passphrase, expiry, verbosity):
        # Set the container name variable
        self.container_name = container_name
        # Output file
        if output_file.startswith('~'):
            self.output_file = os.path.abspath(os.path.expanduser(os.path.join(output_file)))
        else:
            self.output_file = os.path.abspath(os.path.join(output_file))
        # Ensure that the output file can be used
        if not os.path.isfile(self.output_file):
            try:
                open(self.output_file, 'a').close()
            except FileNotFoundError:
                logging.error(f'Cannot use the supplied output file: {self.output_file}')
        # Ensure that the expiry provided is valid
        try:
            assert 0 < expiry < 366
        except AssertionError:
            logging.error(f'The provided expiry ({expiry}) is invalid. It must be between 1 and 365')
            quit()
        self.expiry = expiry
        self.verbosity = verbosity
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.account_key = str()
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None
        self.sas_urls = dict()


class AzureSAS(object):

    def main(self):
        self.connect_str = extract_connection_string(passphrase=self.passphrase,
                                                     account_name=self.account_name)
        self.account_key = extract_account_key(connect_str=self.connect_str)
        self.container_name = extract_container_name(object_name=self.object_name)
        self.blob_service_client = create_blob_service_client(connect_str=self.connect_str)
        self.container_client = create_container_client(blob_service_client=self.blob_service_client,
                                                        container_name=self.container_name)

    def file_sas(self):
        pass

    def folder_sas(self):
        pass

    def __init__(self, object_name, output_file, account_name, passphrase, expiry, verbosity, category):
        # Set the container name variable
        self.object_name = object_name
        # Output file
        if output_file.startswith('~'):
            self.output_file = os.path.abspath(os.path.expanduser(os.path.join(output_file)))
        else:
            self.output_file = os.path.abspath(os.path.join(output_file))
        # Ensure that the output file can be used
        if not os.path.isfile(self.output_file):
            try:
                open(self.output_file, 'a').close()
            except FileNotFoundError:
                logging.error(f'Cannot use the supplied output file: {self.output_file}')
        # Ensure that the expiry provided is valid
        try:
            assert 0 < expiry < 366
        except AssertionError:
            logging.error(f'The provided expiry ({expiry}) is invalid. It must be between 1 and 365')
            quit()
        self.expiry = expiry
        self.verbosity = verbosity
        self.category = category
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.account_key = str()
        self.connect_str = str()
        self.container_name = str()
        self.blob_service_client = None
        self.container_client = None
        self.sas_urls = dict()


def container_sas(args):
    """
   Run the AzureContainerSAS method
   :param args: type ArgumentParser arguments
   """
    logging.info(f'Creating SAS for all files in Azure container {args.container_name}')
    # Create the container SAS object
    sas = AzureContainerSAS(container_name=args.container_name,
                            output_file=args.output_file,
                            account_name=args.account_name,
                            passphrase=args.passphrase,
                            expiry=args.expiry,
                            verbosity=args.verbosity)
    sas.main()


def file_sas(args):
    """
        Run the AzureDownload class for a file
        :param args: type ArgumentParser arguments
        """
    logging.info(f'Creating SAS for {args.file} in Azure storage account {args.account_name}')
    # Create the file download object
    sas_file = AzureSAS(object_name=args.file,
                        output_file=args.output_file,
                        account_name=args.account_name,
                        passphrase=args.passphrase,
                        expiry=args.expiry,
                        verbosity=args.verbosity,
                        category='file')
    sas_file.main()


def folder_sas(args):
    pass


def cli():
    parser = ArgumentParser(description='Create shared access signatures (SAS) for containers/files/folders from Azure '
                                        'storage. Note that each file in the container/folder has to be downloaded '
                                        'separately, so if there are 1000 files in the container, 1000 SAS will be '
                                        'provided')
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
    parent_parser.add_argument('-e', '--expiry',
                               default=10,
                               type=int,
                               help='The number of days that the SAS will be valid. The minimum is 1, and the maximum '
                                    'is 365. The default is 10.')
    parent_parser.add_argument('-v', '--verbosity',
                               choices=['debug', 'info', 'warning', 'error', 'critical'],
                               default='info',
                               help='Set the logging level. Default is info.')
    parent_parser.add_argument('-o', '--output_file',
                               default=os.path.join(os.getcwd(), 'sas.txt'),
                               help='Name and path of file in which the SAS are to be saved. Default is $CWD/sas.txt')
    # Container SAS subparser
    container_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='container',
                                                description='Create SAS for all files in a container in Azure storage',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Create SAS for all files in a container in Azure storage')
    container_subparser.add_argument('-c', '--container_name',
                                     required=True,
                                     type=str,
                                     default=str(),
                                     help='Name of container for which SAS are to be created for all files.')
    container_subparser.set_defaults(func=container_sas)
    # File SAS subparser
    file_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='file',
                                           description='Create a SAS for a file in Azure storage',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Create a SAS for a file in Azure storage')
    file_subparser.add_argument('-f', '--file',
                                type=str,
                                required=True,
                                help='Path of file in Azure storage from which a SAS is to be created. Note that this '
                                     'includes the container name '
                                     'e.g. 220202-m05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    file_subparser.set_defaults(func=file_sas)
    # Folder SAS subparser
    folder_subparser = subparsers.add_parser(parents=[parent_parser],
                                             name='folder',
                                             description='Create SAS for all files in a folder in Azure storage',
                                             formatter_class=RawTextHelpFormatter,
                                             help='Create SAS for all files in a folder in Azure storage')
    folder_subparser.add_argument('-f', '--folder',
                                  type=str,
                                  required=True,
                                  help='Name of the container and folder for which SAS are to be created for all files '
                                       'e.g. sequencing-runs/220202-m05722/InterOp')
    folder_subparser.set_defaults(func=folder_sas)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('SAS creation complete')


if __name__ == '__main__':
    cli()
