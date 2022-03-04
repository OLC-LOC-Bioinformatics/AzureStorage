#!/usr/bin/env python
from azure_storage.methods import create_parent_parser, delete_container, delete_file, delete_folder, copy_blob, \
     move_prep, setup_arguments
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import pathlib
import azure
import sys
import os


class AzureContainerMove(object):

    def main(self):
        # Validate the container names, and prepare all the necessary clients
        self.container_name, self.target_container, self.blob_service_client, self.source_container_client, \
            self.target_container_client = move_prep(
                passphrase=self.passphrase,
                account_name=self.account_name,
                container_name=self.container_name,
                target_container=self.target_container)
        # Rename (move) the container
        self.move_container(source_container_client=self.source_container_client,
                            blob_service_client=self.blob_service_client,
                            container_name=self.container_name,
                            target_container=self.target_container,
                            path=self.path,
                            storage_tier=self.storage_tier)
        # Delete the original container once the copy is complete
        delete_container(blob_service_client=self.blob_service_client,
                         container_name=self.container_name,
                         account_name=self.account_name)

    @staticmethod
    def move_container(source_container_client, blob_service_client, container_name, target_container, path,
                       storage_tier):
        """
        Rename (move) the specified container in Azure storage
        :param source_container_client: type azure.storage.blob.BlobServiceClient.ContainerClient for source container
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container in which the folder is located
        :param target_container: type str: Name of the container into which the folder is to be moved
        :param path: type str: Path of folders in which the files are to be placed
        :param storage_tier: type str: Storage tier to use for the container
        """
        # Create a generator containing all the blobs in the container
        generator = source_container_client.list_blobs()
        try:
            for blob_file in generator:
                # Copy the file to the new container
                copy_blob(blob_file=blob_file,
                          blob_service_client=blob_service_client,
                          container_name=container_name,
                          target_container=target_container,
                          path=path,
                          storage_tier=storage_tier,
                          category='container')
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')

    def __init__(self, container_name, account_name, passphrase, target_container, path, storage_tier):
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.target_container = target_container
        self.path = path
        self.storage_tier = storage_tier
        self.connect_str = str()
        self.blob_service_client = None
        self.source_container_client = None
        self.target_container_client = None


class AzureMove(object):

    def main(self):
        # Validate the container names, and prepare all the necessary clients
        self.container_name, self.target_container, self.blob_service_client, self.source_container_client, \
            self.target_container_client = move_prep(
                passphrase=self.passphrase,
                account_name=self.account_name,
                container_name=self.container_name,
                target_container=self.target_container)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            self.move_file(source_container_client=self.source_container_client,
                           object_name=self.object_name,
                           blob_service_client=self.blob_service_client,
                           container_name=self.container_name,
                           target_container=self.target_container,
                           path=self.path,
                           storage_tier=self.storage_tier)
            delete_file(container_client=self.source_container_client,
                        object_name=self.object_name,
                        blob_service_client=self.blob_service_client,
                        container_name=self.container_name,
                        account_name=self.account_name)
        elif self.category == 'folder':
            self.move_folder(source_container_client=self.source_container_client,
                             object_name=self.object_name,
                             blob_service_client=self.blob_service_client,
                             container_name=self.container_name,
                             target_container=self.target_container,
                             path=self.path,
                             category=self.category,
                             storage_tier=self.storage_tier)
            delete_folder(container_client=self.source_container_client,
                          object_name=self.object_name,
                          blob_service_client=self.blob_service_client,
                          container_name=self.container_name,
                          account_name=self.account_name)
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')
            raise SystemExit

    @staticmethod
    def move_file(source_container_client, object_name, blob_service_client, container_name, target_container,
                  path, storage_tier):
        """
        Move the specified file to the desired container in Azure storage
        :param source_container_client: type azure.storage.blob.BlobServiceClient.ContainerClient for source container
        :param object_name: type str: Name and path of folder to move in Azure storage
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container in which the folder is located
        :param target_container: type str: Name of the container into which the folder is to be moved
        :param path: type str: Path of folders in which the files are to be placed
        :param storage_tier: type str: Storage tier to use for the file
        """
        # Create a generator containing all the blobs in the container
        generator = source_container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        try:
            for blob_file in generator:
                # Filter for the blob name
                if blob_file.name == object_name:
                    # Update the blob presence variable
                    present = True
                    # Copy the file to the new container
                    copy_blob(blob_file=blob_file,
                              blob_service_client=blob_service_client,
                              container_name=container_name,
                              target_container=target_container,
                              path=path,
                              storage_tier=storage_tier)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired file {object_name}')
            raise SystemExit

    @staticmethod
    def move_folder(source_container_client, object_name, blob_service_client, container_name, target_container, path,
                    storage_tier, category):
        """
        Move the specified folder (and its contents) to the desired container in Azure storage
        :param source_container_client: type azure.storage.blob.BlobServiceClient.ContainerClient for source container
        :param object_name: type str: Name and path of folder to move in Azure storage
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container in which the folder is located
        :param target_container: type str: Name of the container into which the folder is to be moved
        :param path: type str: Path of folders in which the files are to be placed
        :param storage_tier: type str: Storage tier to use for the moved folder
        :param category: type str: Category of object to be copied. Limited to file or folder
        """
        # Create a generator containing all the blobs in the container
        generator = source_container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        try:
            for blob_file in generator:
                # Create the pathlib.Path objects for both the folder and the blob file
                object_path = pathlib.Path(os.path.normpath(object_name))
                blob_path = pathlib.Path(blob_file.name).parent
                # If there is a common path between the folder and the blob file path, then there is a match
                try:
                    common_path = blob_path.relative_to(object_path)
                    # Change the dot returned by an exact match to the directory with ''
                    common_path = common_path if str(common_path) != '.' else ''
                except ValueError:
                    common_path = None
                # Only copy the file if there is a common path between the object path and the blob path (they match)
                if common_path is not None:
                    # Update the blob presence variable
                    present = True
                    # Copy the file to the new container
                    copy_blob(blob_file=blob_file,
                              blob_service_client=blob_service_client,
                              container_name=container_name,
                              target_container=target_container,
                              path=path,
                              object_name=object_name,
                              category=category,
                              common_path=common_path,
                              storage_tier=storage_tier)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {container_name}, does not exist.')
            raise SystemExit
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired folder {object_name}')
            raise SystemExit

    def __init__(self, object_name, container_name, account_name, passphrase, target_container, path,
                 storage_tier, category):
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.target_container = target_container
        self.path = path
        self.storage_tier = storage_tier
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.source_container_client = None
        self.target_container_client = None


def container_move(args):
    """
    Run the AzureContainerMove method
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Renaming container {args.container_name} to {args.target_container} in Azure storage '
                 f'account {args.account_name}')
    move_container = AzureContainerMove(container_name=args.container_name,
                                        account_name=args.account_name,
                                        passphrase=args.passphrase,
                                        target_container=args.target_container,
                                        path=args.reset_path,
                                        storage_tier=args.storage_tier)
    move_container.main()


def file_move(args):
    """
    Run the AzureMove method for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Moving file {args.file} from {args.container_name} to {args.target_container} in Azure storage '
                 f'account {args.account_name}')
    move_file = AzureMove(object_name=args.file,
                          container_name=args.container_name,
                          account_name=args.account_name,
                          passphrase=args.passphrase,
                          target_container=args.target_container,
                          path=args.reset_path,
                          storage_tier=args.storage_tier,
                          category='file')
    move_file.main()


def folder_move(args):
    """
    Run the AzureMove method for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Moving folder {args.folder} from {args.container_name} to {args.target_container} in Azure storage '
                 f'account {args.account_name}')
    move_folder = AzureMove(object_name=args.folder,
                            container_name=args.container_name,
                            account_name=args.account_name,
                            passphrase=args.passphrase,
                            target_container=args.target_container,
                            path=args.reset_path,
                            storage_tier=args.storage_tier,
                            category='folder')
    move_folder.main()


def cli():
    parser = ArgumentParser(description='Move containers, files, or folders in Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument('-t', '--target_container',
                               required=True,
                               help='The target container to which the container/file/folder is to be moved '
                                    '(this can be the same as the container_name if you want to move a file/folder'
                                    ' within a container')
    parent_parser.add_argument('-r', '--reset_path',
                               type=str,
                               help='Set the path of the container/file/folder within a folder in the target container '
                                    'e.g. sequence_data/220202-m05722. If you want to place it directly in the '
                                    'container without any nesting, use or \'\'')
    parent_parser.add_argument('-s', '--storage_tier',
                               type=str,
                               default='Hot',
                               choices=['Hot', 'Cool', 'Archive'],
                               metavar='STORAGE_TIER',
                               help='Set the storage tier for the container/file/folder to be moved. '
                                    'Options are "Hot", "Cool", and "Archive". Default is Hot')
    # Container move subparser
    container_move_subparser = subparsers.add_parser(parents=[parent_parser],
                                                     name='container',
                                                     description='Move a container in Azure storage',
                                                     formatter_class=RawTextHelpFormatter,
                                                     help='Move a container in Azure storage')
    container_move_subparser.set_defaults(func=container_move)
    # File move subparser
    file_move_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='file',
                                                description='Move a file within Azure storage',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Move a file within Azure storage')
    file_move_subparser.add_argument('-f', '--file',
                                     type=str,
                                     required=True,
                                     help='Name of blob file to move in Azure storage. '
                                          'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    file_move_subparser.set_defaults(func=file_move)
    # Folder move subparser
    folder_move_subparser = subparsers.add_parser(parents=[parent_parser],
                                                  name='folder',
                                                  description='Move a folder within Azure storage',
                                                  formatter_class=RawTextHelpFormatter,
                                                  help='Move a folder within Azure storage')
    folder_move_subparser.add_argument('-f', '--folder',
                                       type=str,
                                       required=True,
                                       help='Name of folder to move in Azure storage. '
                                            'e.g. InterOp')
    folder_move_subparser.set_defaults(func=folder_move)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Move complete')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
