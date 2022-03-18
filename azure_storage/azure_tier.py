#!/usr/bin/env python
from azure_storage.methods import client_prep, create_blob_client, create_container, \
    create_parent_parser, setup_arguments
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import azure
import sys
import os


class AzureContainerTier(object):

    def main(self):
        self.container_name, self.connect_str, self.blob_service_client, self.container_client = \
            client_prep(container_name=self.container_name,
                        passphrase=self.passphrase,
                        account_name=self.account_name,
                        create=False)
        self.container_tier(container_client=self.container_client,
                            blob_service_client=self.blob_service_client,
                            container_name=self.container_name,
                            storage_tier=self.storage_tier)

    @staticmethod
    def container_tier(container_client, blob_service_client, container_name, storage_tier):
        """
        Set the storage tier for the specified container in Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param storage_tier: type str: Storage tier to use for the container
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
                # Set the storage tier
                blob_client.set_standard_blob_tier(standard_blob_tier=storage_tier)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit

    def __init__(self, container_name, account_name, passphrase, storage_tier):
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.storage_tier = storage_tier
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


class AzureTier(object):

    def main(self):
        self.container_name, self.connect_str, self.blob_service_client, self.container_client = \
            client_prep(container_name=self.container_name,
                        passphrase=self.passphrase,
                        account_name=self.account_name,
                        create=False)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            self.file_tier(container_client=self.container_client,
                           object_name=self.object_name,
                           blob_service_client=self.blob_service_client,
                           container_name=self.container_name,
                           storage_tier=self.storage_tier)
        elif self.category == 'folder':
            self.folder_tier(container_client=self.container_client,
                             object_name=self.object_name,
                             blob_service_client=self.blob_service_client,
                             container_name=self.container_name,
                             storage_tier=self.storage_tier)
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')
            raise SystemExit

    @staticmethod
    def file_tier(container_client, object_name, blob_service_client, container_name, storage_tier):
        """
        Set the storage tier for the specified file in Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param object_name: type str: Name and path of file for which a SAS URL is to be created
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param storage_tier: type str: Storage tier to use for the file
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        try:
            for blob_file in generator:
                # Filter for the blob name
                if blob_file.name == object_name:
                    # Update the blob presence variable
                    present = True
                    # Create the blob client
                    blob_client = create_blob_client(blob_service_client=blob_service_client,
                                                     container_name=container_name,
                                                     blob_file=blob_file)
                    # Set the storage tier
                    blob_client.set_standard_blob_tier(standard_blob_tier=storage_tier)
            # Send an error to the user that the blob could not be found
            if not present:
                logging.error(f'Could not locate the desired file {object_name} in {container_name}')
                raise SystemExit
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit

    @staticmethod
    def folder_tier(container_client, object_name, blob_service_client, container_name, storage_tier):
        """
        Set the storage tier for the specified folder in Azure storage
        :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
        :param object_name: type str: Name and path of file for which a SAS URL is to be created
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param storage_tier: type str: Storage tier to use for the folder
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        try:
            for blob_file in generator:
                # Create the path of the file by extracting the path of the file
                blob_path = os.path.join(os.path.split(blob_file.name)[0])
                # Ensure that the supplied folder path is present in the blob path
                if os.path.normpath(object_name) in os.path.normpath(blob_path):
                    # Update the folder presence boolean
                    present = True
                    # Create the blob client
                    blob_client = create_blob_client(blob_service_client=blob_service_client,
                                                     container_name=container_name,
                                                     blob_file=blob_file)
                    # Set the storage tier
                    blob_client.set_standard_blob_tier(standard_blob_tier=storage_tier)
            # Send an error to the user that the folder could not be found
            if not present:
                logging.error(f'Could not locate the desired folder {object_name} in container {container_name}')
                raise SystemExit
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit

    def __init__(self, object_name, container_name, account_name, passphrase, storage_tier, category):
        # Set the name of the file/folder to have its storage tier set
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.storage_tier = storage_tier
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


def container_tier(args):
    """
    Run the AzureContainerTier method
    :param args: type ArgumentParser arguments
        """
    logging.info(f'Setting the storage tier for Azure container {args.container_name} to {args.storage_tier}')
    # Create the container tier object
    container_tier_set = AzureContainerTier(container_name=args.container_name,
                                            account_name=args.account_name,
                                            passphrase=args.passphrase,
                                            storage_tier=args.storage_tier)
    container_tier_set.main()


def file_tier(args):
    """
    Run the AzureTier method for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Setting the storage tier for file {args.file} in Azure container {args.container_name} to '
                 f'{args.storage_tier}')
    # Create the file tier object
    file_tier_set = AzureTier(container_name=args.container_name,
                              object_name=args.file,
                              account_name=args.account_name,
                              passphrase=args.passphrase,
                              storage_tier=args.storage_tier,
                              category='file')
    file_tier_set.main()


def folder_tier(args):
    """
    Run the AzureTier method for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Setting the storage tier for folder {args.folder} in Azure container {args.container_name} to '
                 f'{args.storage_tier}')
    # Create the folder tier object
    folder_tier_set = AzureTier(container_name=args.container_name,
                                object_name=args.folder,
                                account_name=args.account_name,
                                passphrase=args.passphrase,
                                storage_tier=args.storage_tier,
                                category='folder')
    folder_tier_set.main()


def cli():
    parser = ArgumentParser(description='Set the storage tier of containers/files/folders in Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument('-s', '--storage_tier',
                               type=str,
                               required=True,
                               choices=['Hot', 'Cool', 'Archive'],
                               metavar='STORAGE_TIER',
                               help='Set the storage tier for a container/file/folder. Options are "Hot", '
                                    '"Cool", and "Archive"')
    # Container tier setting parser
    container_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='container',
                                                description='Change the storage tier of a container in Azure storage',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Change the storage tier of a container in Azure storage')
    container_subparser.set_defaults(func=container_tier)
    # File tier setting parser
    file_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='file',
                                           description='Change the storage tier of a file in Azure storage',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Change the storage tier of a file in Azure storage')
    file_subparser.add_argument('-f', '--file',
                                type=str,
                                required=True,
                                help='Name of file in Azure storage that will have its storage tier set'
                                     'e.g. 220202-m05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    file_subparser.set_defaults(func=file_tier)
    # Folder downloading subparser
    folder_subparser = subparsers.add_parser(parents=[parent_parser],
                                             name='folder',
                                             description='Change the storage tier of a folder in Azure storage',
                                             formatter_class=RawTextHelpFormatter,
                                             help='Change the storage tier of a folder in Azure storage')
    folder_subparser.add_argument('-f', '--folder',
                                  type=str,
                                  required=True,
                                  help='Name of the folder in Azure storage that will have its storage tier set '
                                       'e.g. InterOp')
    folder_subparser.set_defaults(func=folder_tier)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Storage tier set')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
