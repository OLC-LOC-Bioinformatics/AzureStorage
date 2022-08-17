#!/usr/bin/env python
from azure_storage.methods import \
    client_prep, \
    create_parent_parser, \
    delete_container, \
    delete_file, \
    delete_folder, \
    setup_arguments, \
    set_blob_retention_policy
from argparse import \
    ArgumentParser, \
    RawTextHelpFormatter
import coloredlogs
import logging
import sys
import os


class AzureContainerDelete(object):

    def main(self):
        self.container_name, self.connect_str, self.blob_service_client, container_client = \
            client_prep(
                container_name=self.container_name,
                account_name=self.account_name
            )
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
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


class AzureDelete(object):

    def main(self):
        self.container_name, self.connect_str, self.blob_service_client, self.container_client = \
            client_prep(
                container_name=self.container_name,
                account_name=self.account_name
            )
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        # Set the file retention policy
        self.blob_service_client = set_blob_retention_policy(
            blob_service_client=self.blob_service_client,
            days=self.retention_time
        )
        # Run the proper method depending on whether a file or a folder is requested
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
            logging.error(f'Something is wrong. There is no {self.category} option available')
            raise SystemExit

    def __init__(self, object_name, container_name, account_name, retention_time, category):
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.account_name = account_name
        self.retention_time = retention_time
        # Ensure that the retention time provided is valid
        try:
            assert 0 < self.retention_time < 366
        except AssertionError:
            logging.error(f'The provided retention time ({self.retention_time}) is invalid. '
                          f'It must be between 1 and 365 days')
            raise SystemExit
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


def container_delete(args):
    """
    Run the AzureContainerDelete method
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Deleting container {args.container_name} from Azure storage account {args.account_name}')
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
    logging.info(f'Deleting file {args.file} from container {args.container_name} in Azure storage account '
                 f'{args.account_name}')
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
    logging.info(f'Deleting folder {args.folder} from container {args.container_name} in Azure storage account '
                 f'{args.account_name}')
    del_folder = AzureDelete(
        object_name=args.folder,
        container_name=args.container_name,
        account_name=args.account_name,
        retention_time=args.retention_time,
        category='folder'
    )
    del_folder.main()


def cli():
    parser = ArgumentParser(description='Move and/or delete containers, files, or folders in Azure storage')
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
        help='Retention time for deleted files. Default is 8 days. Must be between '
             '1 and 365'
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
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Deletion complete')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
