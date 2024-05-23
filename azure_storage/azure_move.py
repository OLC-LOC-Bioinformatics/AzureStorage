#!/usr/bin/env python
"""
Move containers, files, or folders in Azure storage
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
    copy_blob,
    create_parent_parser,
    delete_container,
    delete_file,
    delete_folder,
    extract_common_path,
    move_prep,
    setup_arguments
)


class AzureContainerMove:
    """
    Class for moving Azure storage containers.

    Attributes:
        container_name (str): Name of the source container.
        target_container (str): Name of the target container.
        blob_service_client (azure.storage.blob.BlobServiceClient):
            BlobServiceClient object to interact with the Azure storage.
        source_container_client (azure.storage.blob.ContainerClient):
            ContainerClient object for the source container.
        target_container_client (azure.storage.blob.ContainerClient):
            ContainerClient object for the target container.
        account_name (str): Name of the Azure storage account.
        path (str): Path to the files in the container.
        storage_tier (str): The storage tier to use for the moved files.
        copy (bool): Whether to keep a copy of the files in the source
        container.
    """

    def main(self):
        """
        Main method for the AzureContainerMove class.

        This method validates the container names, prepares the necessary
        clients, moves the container, and optionally deletes the original
        container.
        """
        # Validate the container names, and prepare all the necessary clients
        self.container_name, \
            self.target_container, \
            self.blob_service_client, \
            self.source_container_client, \
            self.target_container_client = \
            move_prep(
                account_name=self.account_name,
                container_name=self.container_name,
                target_container=self.target_container
            )
        # Rename (move) the container
        self.move_container(
            source_container_client=self.source_container_client,
            blob_service_client=self.blob_service_client,
            container_name=self.container_name,
            target_container=self.target_container,
            path=self.path,
            storage_tier=self.storage_tier
        )
        if not self.copy:
            # Delete the original container once the copy is complete
            delete_container(
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                account_name=self.account_name
            )

    @staticmethod
    def move_container(
            source_container_client,
            blob_service_client,
            container_name,
            target_container,
            path,
            storage_tier):
        """
        Rename (move) the specified container in Azure storage
        :param source_container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient for
        source container
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container in which the
        folder is located
        :param target_container: type str: Name of the container into which
        the folder is to be moved
        :param path: type str: Path of folders in which the files are to
        be placed
        :param storage_tier: type str: Storage tier to use for the container
        """
        # Create a generator containing all the blobs in the container
        generator = source_container_client.list_blobs()
        for blob_file in generator:
            # Copy the file to the new container
            copy_blob(
                blob_file=blob_file,
                blob_service_client=blob_service_client,
                container_name=container_name,
                target_container=target_container,
                path=path,
                storage_tier=storage_tier,
                category='container'
            )

    def __init__(
            self,
            container_name,
            account_name,
            target_container,
            path,
            storage_tier,
            copy=False):
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.account_name = account_name
        self.target_container = target_container
        self.path = path
        self.storage_tier = storage_tier
        self.copy = copy
        self.connect_str = str()
        self.blob_service_client = None
        self.source_container_client = None
        self.target_container_client = None


class AzureMove:
    """
    Class for moving files or folders in Azure storage containers.

    Attributes:
        container_name (str): Name of the source container.
        target_container (str): Name of the target container.
        blob_service_client (azure.storage.blob.BlobServiceClient):
            BlobServiceClient object to interact with the Azure storage.
        source_container_client (azure.storage.blob.ContainerClient):
            ContainerClient object for the source container.
        target_container_client (azure.storage.blob.ContainerClient):
            ContainerClient object for the target container.
        account_name (str): Name of the Azure storage account.
        path (str): Path to the files in the container.
        storage_tier (str): The storage tier to use for the moved files.
        copy (bool): Whether to keep a copy of the files in the source
        container.
        category (str): The category of the object to move ('file' or 'folder')
        object_name (str): The name of the object to move.
        name (str): The new name for the moved object.
    """

    def main(self):
        """
        Main method for the AzureMove class.

        This method validates the container names, prepares the necessary
        clients, moves the specified file or folder, and optionally deletes
        the original file or folder.
        """
        # Validate the container names, and prepare all the necessary clients
        self.container_name, \
            self.target_container, \
            self.blob_service_client, \
            self.source_container_client, \
            self.target_container_client = \
            move_prep(
                account_name=self.account_name,
                container_name=self.container_name,
                target_container=self.target_container
            )
        # Run the proper method depending on whether a file or a folder is
        # requested
        if self.category == 'file':
            self.move_file(
                source_container_client=self.source_container_client,
                object_name=self.object_name,
                rename=self.name,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                target_container=self.target_container,
                path=self.path,
                storage_tier=self.storage_tier,
            )
            if not self.copy:
                delete_file(
                    container_client=self.source_container_client,
                    object_name=self.object_name,
                    blob_service_client=self.blob_service_client,
                    container_name=self.container_name
                )
        elif self.category == 'folder':
            self.move_folder(
                source_container_client=self.source_container_client,
                object_name=self.object_name,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                target_container=self.target_container,
                path=self.path,
                category=self.category,
                storage_tier=self.storage_tier,
            )
            if not self.copy:
                delete_folder(
                    container_client=self.source_container_client,
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

    @staticmethod
    def move_file(
            source_container_client,
            object_name,
            blob_service_client,
            container_name,
            target_container,
            path,
            storage_tier,
            rename=None):
        """
        Move the specified file to the desired container in Azure storage
        :param source_container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient for
        source container
        :param object_name: type str: Name and path of folder to move in
        Azure storage
        :param rename: type str: Desired string to use to rename the file
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container in which the
        folder is located
        :param target_container: type str: Name of the container into which
        the folder is to be moved
        :param path: type str: Path of folders in which the files are to
        be placed
        :param storage_tier: type str: Storage tier to use for the file
        """
        # Create a generator containing all the blobs in the container
        generator = source_container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        for blob_file in generator:
            # Filter for the blob name
            if blob_file.name == object_name:
                # Update the blob presence variable
                present = True
                # Copy the file to the new container
                copy_blob(
                    blob_file=blob_file,
                    blob_service_client=blob_service_client,
                    container_name=container_name,
                    target_container=target_container,
                    path=path,
                    storage_tier=storage_tier,
                    rename=rename,
                )
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error('Could not locate the desired file %s', object_name)
            raise SystemExit

    @staticmethod
    def move_folder(
            source_container_client,
            object_name,
            blob_service_client,
            container_name,
            target_container,
            path,
            storage_tier,
            category):
        """
        Move the specified folder (and its contents) to the desired container
        in Azure storage
        :param source_container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient for
        source container
        :param object_name: type str: Name and path of folder to move in
        Azure storage
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container in which the
        folder is located
        :param target_container: type str: Name of the container into which
        the folder is to be moved
        :param path: type str: Path of folders in which the files are to
        be placed
        :param storage_tier: type str: Storage tier to use for the moved folder
        :param category: type str: Category of object to be copied. Limited
        to file or folder
        """
        # Create a generator containing all the blobs in the container
        generator = source_container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        for blob_file in generator:
            # Extract the common path between the current file and the
            # requested folder
            common_path = extract_common_path(
                object_name=object_name,
                blob_file=blob_file
            )
            # Only copy the file if there is a common path between the object
            # path and the blob path (they match)
            if common_path is not None:
                # Update the blob presence variable
                present = True
                # Copy the file to the new container
                copy_blob(
                    blob_file=blob_file,
                    blob_service_client=blob_service_client,
                    container_name=container_name,
                    target_container=target_container,
                    path=path,
                    object_name=object_name,
                    category=category,
                    common_path=common_path,
                    storage_tier=storage_tier
                )
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(
                'Could not locate the desired folder %s',
                object_name
            )
            raise SystemExit

    def __init__(
            self,
            object_name,
            container_name,
            account_name,
            target_container,
            path,
            storage_tier,
            category,
            copy=False,
            name=None):
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.account_name = account_name
        self.target_container = target_container
        self.path = path
        self.storage_tier = storage_tier
        self.category = category
        self.copy = copy
        self.name = name if name else None
        self.connect_str = str()
        self.blob_service_client = None
        self.source_container_client = None
        self.target_container_client = None


def container_move(args):
    """
    Run the AzureContainerMove method
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Renaming container %s to %s in Azure storage account %s',
        args.container_name, args.target_container, args.account_name
        )
    move_container = AzureContainerMove(
        container_name=args.container_name,
        account_name=args.account_name,
        target_container=args.target_container,
        path=args.reset_path,
        storage_tier=args.storage_tier
    )
    move_container.main()


def file_move(args):
    """
    Run the AzureMove method for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Moving file %s from %s to %s in Azure storage account %s',
        args.file,
        args.container_name,
        args.target_container,
        args.account_name
    )
    move_file = AzureMove(
        object_name=args.file,
        container_name=args.container_name,
        account_name=args.account_name,
        target_container=args.target_container,
        path=args.reset_path,
        storage_tier=args.storage_tier,
        category='file'
    )
    move_file.main()


def folder_move(args):
    """
    Run the AzureMove method for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Moving folder %s from %s to %s in Azure storage account %s',
        args.folder,
        args.container_name,
        args.target_container,
        args.account_name
        )
    move_folder = AzureMove(
        object_name=args.folder,
        container_name=args.container_name,
        account_name=args.account_name,
        target_container=args.target_container,
        path=args.reset_path,
        storage_tier=args.storage_tier,
        category='folder'
    )
    move_folder.main()


def cli():
    """
    CLI function for moving containers, files, or folders in Azure storage.

    This function sets up argument parsing for the CLI, including subparsers
    for moving containers, files, and folders.

    The function then sets up the arguments and runs the appropriate
    subparser based on the provided arguments.

    After the operation is complete, the function logs a completion message
    and suppresses further console output.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = ArgumentParser(
        description='Move containers, files, or folders in Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument(
        '-t', '--target_container', required=True,
        help='The target container to which the container/file/folder is to '
        'be moved (this can be the same as the container_name if you want to '
        'move a file/folder within a container'
    )
    parent_parser.add_argument(
        '-r', '--reset_path', type=str,
        help='Set the path of the container/file/folder within a folder in '
        'the target container e.g. sequence_data/220202-m05722. If you want '
        'to place it directly in the container without any nesting, use '
        'or \'\''
    )
    parent_parser.add_argument(
        '-s', '--storage_tier',
        type=str,
        default='Hot',
        choices=['Hot', 'Cool', 'Archive'],
        metavar='STORAGE_TIER',
        help='Set the storage tier for the container/file/folder to be moved. '
             'Options are "Hot", "Cool", and "Archive". Default is Hot'
    )
    # Container move subparser
    container_move_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Move a container in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Move a container in Azure storage'
    )
    container_move_subparser.set_defaults(func=container_move)
    # File move subparser
    file_move_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Move a file within Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Move a file within Azure storage'
    )
    file_move_subparser.add_argument(
        '-f', '--file',
        type=str,
        required=True,
        help='Name of blob file to move in Azure storage. '
             'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz'
    )
    file_move_subparser.set_defaults(func=file_move)
    # Folder move subparser
    folder_move_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Move a folder within Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Move a folder within Azure storage'
    )
    folder_move_subparser.add_argument(
        '-f', '--folder',
        type=str,
        required=True,
        help='Name of folder to move in Azure storage. '
             'e.g. InterOp'
    )
    folder_move_subparser.set_defaults(func=folder_move)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to
    # WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Move complete')
    # Prevent the arguments being printed to the console (they are returned in
    # order for the tests to work)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    return arguments


if __name__ == '__main__':
    cli()
