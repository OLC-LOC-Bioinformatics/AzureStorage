#!/usr/bin/env python
"""
Move and/or delete files or folders in Azure storage
"""

# Standard imports
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)
import logging
import sys
import os

# Third party imports
import coloredlogs

# Local imports
from azure_storage.methods import (
    client_prep,
    create_parent_parser,
    delete_container,
    delete_file,
    delete_folder,
    setup_arguments,
    set_blob_retention_policy
)


class AzureContainerDelete:
    """
    Class for deleting an Azure storage container.

    Attributes:
        container_name (str): The name of the container to delete.
        account_name (str): The name of the Azure storage account.
        connect_str (str): The connection string for the Azure storage account.
        blob_service_client (azure.storage.blob.BlobServiceClient): The
        BlobServiceClient object to interact with the Azure storage account.
    """

    def main(self):
        """
        Main method for the AzureContainerDelete class.

        This method prepares the client for the Azure storage account, sets
        the logging level to WARNING to suppress INFO-level messages from
        Azure, and deletes the container.
        """
        self.container_name, \
            self.connect_str, \
            self.blob_service_client, \
            _ = \
            client_prep(
                container_name=self.container_name,
                account_name=self.account_name
            )
        # Hide the INFO-level messages sent to the logger from Azure by
        # increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        delete_container(
            blob_service_client=self.blob_service_client,
            container_name=self.container_name,
            account_name=self.account_name
        )

    def __init__(self, container_name, account_name):
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.account_name = account_name
        self.connect_str = str()
        self.blob_service_client = None


class AzureDelete:
    """
    Class for deleting an object (file or folder) in an Azure storage
    container.

    Attributes:
        container_name (str): Name of the container where the object is.
        connect_str (str): Connection string for the Azure storage account.
        blob_service_client (azure.storage.blob.BlobServiceClient):
            BlobServiceClient object to interact with the Azure storage.
        container_client (azure.storage.blob.ContainerClient):
            ContainerClient object to interact with the Azure container.
        category (str): Category of the object to delete ('file' or 'folder').
        object_name (str): Name of the object to delete.
        retention_time (int): Retention time for the blob in days.
        account_name (str): Name of the Azure storage account.
    """

    def main(self):
        """
        Main method for the AzureDelete class.

        This method prepares the client for the Azure storage account, sets
        the logging level to WARNING to suppress INFO-level messages from
        Azure, sets the blob retention policy, and deletes the specified
        object.
        """
        self.container_name, \
            self.connect_str, \
            self.blob_service_client, \
            self.container_client = \
            client_prep(
                container_name=self.container_name,
                account_name=self.account_name
            )
        # Hide the INFO-level messages sent to the logger from Azure by
        # increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        # Set the file retention policy
        self.blob_service_client = set_blob_retention_policy(
            blob_service_client=self.blob_service_client,
            days=self.retention_time
        )
        # Run the proper method depending on whether a file or a folder
        # is requested
        if self.category == 'file':
            delete_file(
                container_client=self.container_client,
                object_name=self.object_name,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name
            )
        elif self.category == 'folder':
            delete_folder(
                container_client=self.container_client,
                object_name=self.object_name,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                account_name=self.account_name
            )
        else:
            logging.error(
                'Something is wrong. There is no %s option available',
                self.category
                )
            raise SystemExit

    def __init__(
                self,
                object_name,
                container_name,
                account_name,
                retention_time,
                category):
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.account_name = account_name
        self.retention_time = retention_time
        # Ensure that the retention time provided is valid
        try:
            assert 0 < self.retention_time < 366
        except AssertionError as exc:
            logging.error(
                'The provided retention time (%s) is invalid. '
                'It must be between 1 and 365 days',
                self.retention_time
            )
            raise SystemExit from exc
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


def container_delete(args):
    """
    Run the AzureContainerDelete method
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Deleting container %s from Azure storage account %s',
        args.container_name, args.account_name
    )
    del_container = AzureContainerDelete(
        container_name=args.container_name,
        account_name=args.account_name
    )
    del_container.main()


def file_delete(args):
    """
    Run the AzureDelete method for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Deleting file %s from container %s in Azure storage account %s',
        args.file, args.container_name, args.account_name
    )
    del_file = AzureDelete(
        object_name=args.file,
        container_name=args.container_name,
        account_name=args.account_name,
        retention_time=args.retention_time,
        category='file'
    )
    del_file.main()


def folder_delete(args):
    """
    Run the AzureDelete method for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Deleting folder %s from container %s in Azure storage account %s',
        args.folder, args.container_name, args.account_name
    )
    del_folder = AzureDelete(
        object_name=args.folder,
        container_name=args.container_name,
        account_name=args.account_name,
        retention_time=args.retention_time,
        category='folder'
    )
    del_folder.main()


def cli():
    """
    CLI function for moving and/or deleting containers, files, or folders
    in Azure storage.

    This function sets up argument parsing for the CLI, including subparsers
    for deleting a container, a file, or a folder.

    The function then sets up the arguments and runs the appropriate
    subparser based on the provided arguments.

    After the operation is complete, the function logs a completion message
    and suppresses further console output.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = ArgumentParser(
        description='Move and/or delete containers, files, or folders in '
        'Azure storage'
    )
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    # Container delete subparser
    container_delete_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Delete a container in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Delete a container in Azure storage'
    )
    container_delete_subparser.set_defaults(func=container_delete)
    # File delete subparser
    file_delete_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Delete a file in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Delete a file in Azure storage'
    )
    file_delete_subparser.add_argument(
        '-f', '--file',
        type=str,
        required=True,
        help='Name of blob file to delete in Azure storage. '
             'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz'
    )
    file_delete_subparser.add_argument(
        '-r', '--retention_time',
        type=int,
        default=8,
        help='Retention time for deleted files. Default is 8 days. Must be '
        'between 1 and 365'
    )
    file_delete_subparser.set_defaults(func=file_delete)
    # Folder delete subparser
    folder_delete_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Delete a folder in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Delete a folder in Azure storage'
    )
    folder_delete_subparser.add_argument(
        '-f', '--folder',
        type=str,
        required=True,
        help='Name of folder to delete in Azure storage. '
             'e.g. InterOp'
    )
    folder_delete_subparser.add_argument(
        '-r', '--retention_time',
        type=int,
        default=8,
        help='Retention time for deleted files. Default is 8 days'
    )
    folder_delete_subparser.set_defaults(func=folder_delete)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to
    # WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Deletion complete')
    # Prevent the arguments being printed to the console (they are returned in
    # order for the tests to work)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    return arguments


if __name__ == '__main__':
    cli()
