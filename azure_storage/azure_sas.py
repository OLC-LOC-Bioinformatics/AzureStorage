#!/usr/bin/env python
from azure_storage.methods import create_blob_sas, create_parent_parser, sas_prep, setup_arguments, write_sas
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import azure
import sys
import os


class AzureContainerSAS(object):

    def main(self):
        # Validate container name, retrieve connection string, extract account key, create blob service client and
        # container clients
        self.container_name, \
            self.connect_str, \
            self.account_key, \
            self.blob_service_client, \
            self.container_client = sas_prep(container_name=self.container_name,
                                             passphrase=self.passphrase,
                                             account_name=self.account_name,
                                             create=False)
        # Create the SAS URLs for the files in the container
        self.sas_urls = self.container_sas(container_client=self.container_client,
                                           account_name=self.account_name,
                                           container_name=self.container_name,
                                           account_key=self.account_key,
                                           expiry=self.expiry,
                                           sas_urls=self.sas_urls)
        # Return to the requested logging level, as it has been increased to WARNING to suppress the log being
        # filled with information from azure.core.pipeline.policies.http_logging_policy
        coloredlogs.install(level=self.verbosity.upper())
        write_sas(output_file=self.output_file,
                  sas_urls=self.sas_urls)
        # Write the SAS URLs to the output file
        write_sas(output_file=self.output_file,
                  sas_urls=self.sas_urls)

    @staticmethod
    def container_sas(container_client, account_name, container_name, account_key, expiry, sas_urls):
        """
        Create SAS URLs for all files in the container
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param account_name: type str: Name of the Azure storage account
        :param container_name: type str: Name of the container of interest
        :param account_key: type str: Account key of Azure storage account
        :param expiry: type int: Number of days that the SAS URL will be valid
        :param sas_urls: type dict: Dictionary of file name: SAS URL (empty)
        :return: populated sas_urls
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        try:
            # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
            logging.getLogger().setLevel(logging.WARNING)
            for blob_file in generator:
                # Create the SAS URLs
                sas_urls = create_blob_sas(blob_file=blob_file,
                                           account_name=account_name,
                                           container_name=container_name,
                                           account_key=account_key,
                                           expiry=expiry,
                                           sas_urls=sas_urls)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit
        return sas_urls

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
                # Create the parental directory for the output file as required
                os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            except PermissionError:
                logging.error(f'Insufficient permissions to create output file {self.output_file}')
                raise SystemExit
            try:
                open(self.output_file, 'w').close()
            except IsADirectoryError:
                logging.error(f'A directory or an empty file name was provided for the output file {self.output_file}')
                raise SystemExit
            except PermissionError:
                logging.error(f'Insufficient permissions to create output file {self.output_file}')
                raise SystemExit
        else:
            open(self.output_file, 'w').close()
        # Ensure that the expiry provided is valid
        try:
            assert 0 < expiry < 366
        except AssertionError:
            logging.error(f'The provided expiry ({expiry}) is invalid. It must be between 1 and 365')
            raise SystemExit
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
        # Validate container name, retrieve connection string, extract account key, create blob service client and
        # container clients
        self.container_name, \
            self.connect_str, \
            self.account_key, \
            self.blob_service_client, \
            self.container_client = sas_prep(container_name=self.container_name,
                                             passphrase=self.passphrase,
                                             account_name=self.account_name,
                                             create=False)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            self.sas_urls = self.file_sas(container_client=self.container_client,
                                          account_name=self.account_name,
                                          container_name=self.container_name,
                                          object_name=self.object_name,
                                          account_key=self.account_key,
                                          expiry=self.expiry,
                                          sas_urls=self.sas_urls)
        elif self.category == 'folder':
            self.sas_urls = self.folder_sas(container_client=self.container_client,
                                            account_name=self.account_name,
                                            container_name=self.container_name,
                                            object_name=self.object_name,
                                            account_key=self.account_key,
                                            expiry=self.expiry,
                                            sas_urls=self.sas_urls)
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')
            raise SystemExit
        # Return to the requested logging level, as it has been increased to WARNING to suppress the log being
        # filled with information from azure.core.pipeline.policies.http_logging_policy
        coloredlogs.install(level=self.verbosity.upper())
        write_sas(output_file=self.output_file,
                  sas_urls=self.sas_urls)

    @staticmethod
    def file_sas(container_client, account_name, container_name, object_name, account_key, expiry, sas_urls):
        """
        Create a SAS URL for the specified file in Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param account_name: type str: Name of the Azure storage account
        :param container_name: type str: Name of the container of interest
        :param object_name: type str: Name and path of file for which a SAS URL is to be created
        :param account_key: type str: Account key of Azure storage account
        :param expiry: type int: Number of days that the SAS URL will be valid
        :param sas_urls: type dict: Dictionary of file name: SAS URL (empty)
        :return: populated sas_urls
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        for blob_file in generator:
            # Filter for the blob name
            if blob_file.name == object_name:
                # Update the blob presence variable
                present = True
                sas_urls = create_blob_sas(blob_file=blob_file,
                                           account_name=account_name,
                                           container_name=container_name,
                                           account_key=account_key,
                                           expiry=expiry,
                                           sas_urls=sas_urls)
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired file {object_name} in container {container_name}')
            raise SystemExit
        return sas_urls

    @staticmethod
    def folder_sas(container_client, account_name, container_name, object_name, account_key, expiry, sas_urls):
        """
        Create SAS URLs for all the files in the specified folder in Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param account_name: type str: Name of the Azure storage account
        :param container_name: type str: Name of the container of interest
        :param object_name: type str: Name and path of folder containing files for which SAS URLs are to be created
        :param account_key: type str: Account key of Azure storage account
        :param expiry: type int: Number of days that the SAS URL will be valid
        :param sas_urls: type dict: Dictionary of file name: SAS URL (empty)
        :return: populated sas_urls
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Boolean to track whether the folder was located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        for blob_file in generator:
            # Create the path of the file by adding the container name to the path of the file
            blob_path = os.path.join(container_name, os.path.split(blob_file.name)[0])
            # Ensure that the supplied folder path is present in the blob path
            if os.path.normpath(object_name) in os.path.normpath(blob_path):
                # Update the folder presence boolean
                present = True
                sas_urls = create_blob_sas(blob_file=blob_file,
                                           account_name=account_name,
                                           container_name=container_name,
                                           account_key=account_key,
                                           expiry=expiry,
                                           sas_urls=sas_urls)
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired folder {object_name} in container {container_name}')
            raise SystemExit
        return sas_urls

    def __init__(self, object_name, container_name, output_file, account_name, passphrase, expiry, verbosity, category):
        # Set the name of the file/folder of interest
        self.object_name = object_name
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
                # Create the parental directory for the output file as required
                os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            except PermissionError:
                logging.error(f'Insufficient permissions to create output file {self.output_file}')
                raise SystemExit
            try:
                open(self.output_file, 'w').close()
            except IsADirectoryError:
                logging.error(f'A directory or an empty file name was provided for the output file {self.output_file}')
                raise SystemExit
            except PermissionError:
                logging.error(f'Insufficient permissions to create output file {self.output_file}')
                raise SystemExit
        else:
            open(self.output_file, 'w').close()
        # Ensure that the expiry provided is valid
        try:
            assert 0 < expiry < 366
        except AssertionError:
            logging.error(f'The provided expiry ({expiry}) is invalid. It must be between 1 and 365')
            raise SystemExit
        self.expiry = expiry
        self.verbosity = verbosity
        self.category = category
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.account_key = str()
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None
        self.sas_urls = dict()


def container_sas(args):
    """
   Run the AzureContainerSAS method
   :param args: type ArgumentParser arguments
   """
    logging.info(f'Creating SAS URLs for all files in Azure container {args.container_name}')
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
    Run the AzureSAS class for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Creating SAS URL for {args.file} in container {args.container_name} Azure storage account '
                 f'{args.account_name}')
    # Create the file SAS object
    sas_file = AzureSAS(object_name=args.file,
                        container_name=args.container_name,
                        output_file=args.output_file,
                        account_name=args.account_name,
                        passphrase=args.passphrase,
                        expiry=args.expiry,
                        verbosity=args.verbosity,
                        category='file')
    sas_file.main()


def folder_sas(args):
    """
    Run the AzureSAS class for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Creating SAS URLs for all files in folder {args.folder} in container {args.container_name} in '
                 f'Azure storage account '
                 f'{args.account_name}')
    # Create the folder SAS object
    sas_folder = AzureSAS(object_name=args.folder,
                          container_name=args.container_name,
                          output_file=args.output_file,
                          account_name=args.account_name,
                          passphrase=args.passphrase,
                          expiry=args.expiry,
                          verbosity=args.verbosity,
                          category='folder')
    sas_folder.main()


def cli():
    parser = ArgumentParser(description='Create shared access signatures (SAS) URLs for containers/files/folders in '
                                        'Azure storage. Note that each file in a container/folder has to be downloaded '
                                        'separately, so if there are 1000 files in the container, 1000 SAS URLs will '
                                        'be provided')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument('-e', '--expiry',
                               default=10,
                               type=int,
                               help='The number of days that the SAS URL will be valid. The minimum is 1, and the '
                                    'maximum is 365. The default is 10.')
    parent_parser.add_argument('-o', '--output_file',
                               default=os.path.join(os.getcwd(), 'sas.txt'),
                               help='Name and path of file in which the SAS URLs are to be saved. '
                                    'Default is $CWD/sas.txt')
    # Container SAS subparser
    container_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='container',
                                                description='Create SAS URLs for all files in a container in Azure '
                                                            'storage',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Create SAS URLs for all files in a container in Azure storage')
    container_subparser.set_defaults(func=container_sas)
    # File SAS subparser
    file_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='file',
                                           description='Create a SAS URL for a file in Azure storage',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Create a SAS URL for a file in Azure storage')
    file_subparser.add_argument('-f', '--file',
                                type=str,
                                required=True,
                                help='Path of file in Azure storage from which a SAS URL is to be created. '
                                     'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    file_subparser.set_defaults(func=file_sas)
    # Folder SAS subparser
    folder_subparser = subparsers.add_parser(parents=[parent_parser],
                                             name='folder',
                                             description='Create SAS URLs for all files in a folder in Azure storage',
                                             formatter_class=RawTextHelpFormatter,
                                             help='Create SAS URLs for all files in a folder in Azure storage')
    folder_subparser.add_argument('-f', '--folder',
                                  type=str,
                                  required=True,
                                  help='Name of the folder for which SAS URLs are to be created for all files. '
                                       'e.g. InterOp')
    folder_subparser.set_defaults(func=folder_sas)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('SAS creation complete')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
