#!/usr/bin/env python
from azure_storage.methods import create_blob_client, create_container, create_container_client, \
    create_blob_service_client, create_parent_parser, delete_container, delete_file, delete_folder, copy_blob, \
    extract_connection_string, move_prep, setup_arguments, validate_container_name
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import azure
import os


class AzureContainerMove(object):

    def main(self):
        # Prepare all the necessary clients
        self.blob_service_client, self.source_container_client, self.target_container_client = move_prep(
            passphrase=self.passphrase,
            account_name=self.account_name,
            container_name=self.container_name,
            target_container=self.target_container)
        self.rename_container()
        # Delete the original container once the copy is complete
        delete_container(blob_service_client=self.blob_service_client,
                         container_name=self.container_name,
                         account_name=self.account_name)

    def rename_container(self):
        """
        Rename the container in Azure storage
        """
        # Create a generator containing all the blobs in the container
        generator = self.source_container_client.list_blobs()
        try:
            for blob_file in generator:
                # Copy the file to the new container
                copy_blob(blob_file=blob_file,
                          blob_service_client=self.blob_service_client,
                          container_name=self.container_name,
                          target_container=self.target_container,
                          path=self.path)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {self.container_name}, does not exist.')

    def __init__(self, container_name, account_name, passphrase, target_container, path):
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.target_container = target_container
        self.path = path
        self.connect_str = str()
        self.blob_service_client = None
        self.source_container_client = None
        self.target_container_client = None


class AzureMove(object):

    def main(self):
        # Prepare all the necessary clients
        self.blob_service_client, self.source_container_client, self.target_container_client = move_prep(
            passphrase=self.passphrase,
            account_name=self.account_name,
            container_name=self.container_name,
            target_container=self.target_container)
        # Run the proper method depending on whether a file or a folder is requested
        if self.category == 'file':
            self.move_file()
            delete_file(container_client=self.source_container_client,
                        object_name=self.object_name,
                        blob_service_client=self.blob_service_client,
                        container_name=self.container_name,
                        account_name=self.account_name)
        elif self.category == 'folder':
            self.move_folder()
            delete_folder(container_client=self.source_container_client,
                          object_name=self.object_name,
                          blob_service_client=self.blob_service_client,
                          container_name=self.container_name,
                          account_name=self.account_name)
        else:
            logging.error(f'Something is wrong. There is no {self.category} option available')
            raise SystemExit

    def move_file(self):
        """
        Move the specified file to the desired container in Azure storage
        """
        # Create a generator containing all the blobs in the container
        generator = self.source_container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        try:
            for blob_file in generator:
                # Filter for the blob name
                if blob_file.name == self.object_name:
                    # Update the blob presence variable
                    present = True
                    # Copy the file to the new container
                    copy_blob(blob_file=blob_file,
                              blob_service_client=self.blob_service_client,
                              container_name=self.container_name,
                              target_container=self.target_container,
                              path=self.path)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {self.container_name}, does not exist.')
            raise SystemExit
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired file {self.object_name}')
            raise SystemExit

    def move_folder(self):
        """
        Move the specified folder to the desired container in Azure storage
        """
        # Create a generator containing all the blobs in the container
        generator = self.source_container_client.list_blobs()
        # Create a boolean to determine if the blob has been located
        present = False
        try:
            for blob_file in generator:
                # Create the path of the file by adding the container name to the path of the file
                blob_path = os.path.join(self.container_name, os.path.split(blob_file.name)[0])
                # Ensure that the supplied folder path is present in the blob path
                if os.path.normpath(self.object_name) in os.path.normpath(blob_path):
                    # Update the blob presence variable
                    present = True
                    # Copy the file to the new container
                    copy_blob(blob_file=blob_file,
                              blob_service_client=self.blob_service_client,
                              container_name=self.container_name,
                              target_container=self.target_container,
                              path=self.path)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {self.container_name}, does not exist.')
            raise SystemExit
        # Send a warning to the user that the blob could not be found
        if not present:
            logging.error(f'Could not locate the desired file {self.object_name}')
            raise SystemExit

    def __init__(self, object_name, container_name, account_name, passphrase, target_container, path, category):
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.target_container = target_container
        self.path = path
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.source_container_client = None
        self.target_container_client = None


def container_rename(args):
    """
    Run the AzureContainerMove method
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Renaming container {args.container_name} to {args.target_container} in Azure storage '
                 f'account {args.account_name}')
    del_container = AzureContainerMove(container_name=args.container_name,
                                       account_name=args.account_name,
                                       passphrase=args.passphrase,
                                       target_container=args.target_container,
                                       path=args.path)
    del_container.main()


def file_move(args):
    """
    Run the AzureMove method for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Moving file {args.file} to {args.target_container} in Azure storage '
                 f'account {args.account_name}')
    move_file = AzureMove(object_name=args.file,
                          container_name=args.container_name,
                          account_name=args.account_name,
                          passphrase=args.passphrase,
                          target_container=args.target_container,
                          path=args.reset_path,
                          category='file')
    move_file.main()


def folder_move(args):
    """
    Run the AzureMove method for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Moving folder {args.folder} to {args.target_container} in Azure storage '
                 f'account {args.account_name}')
    move_folder = AzureMove(object_name=args.folder,
                            container_name=args.container_name,
                            account_name=args.account_name,
                            passphrase=args.passphrase,
                            target_container=args.target_container,
                            path=args.reset_path,
                            category='folder')
    move_folder.main()


def cli():
    parser = ArgumentParser(description='Move containers, files, or folders in Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument('-t', '--target_container',
                               required=True,
                               help='The target container to which the file is to be moved (this can be the same as '
                                    'the container_name if you want to move a file/folder within a container)'
                                    'e.g. sequence_data')
    parent_parser.add_argument('-r', '--reset_path',
                               type=str,
                               help='Set the path of the container/file/folder within a folder in the target container '
                                    'e.g. sequence_data/220202-m05722. If you want to place it directly in the '
                                    'container without any nesting, use "" or \'\'')
    # Container rename subparser
    container_rename_subparser = subparsers.add_parser(parents=[parent_parser],
                                                       name='container',
                                                       description='Rename a container in Azure storage',
                                                       formatter_class=RawTextHelpFormatter,
                                                       help='Rename a container in Azure storage')

    container_rename_subparser.set_defaults(func=container_rename)
    # File move subparser
    file_move_subparser = subparsers.add_parser(parents=[parent_parser],
                                                name='file',
                                                description='Move a file in Azure storage from one container to '
                                                            'another',
                                                formatter_class=RawTextHelpFormatter,
                                                help='Move a file in Azure storage from one container to another')
    file_move_subparser.add_argument('-f', '--file',
                                     type=str,
                                     required=True,
                                     help='Name of blob file to move in Azure storage. '
                                          'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz')
    file_move_subparser.set_defaults(func=file_move)
    # Folder move subparser
    folder_move_subparser = subparsers.add_parser(parents=[parent_parser],
                                                  name='folder',
                                                  description='Move a folder in Azure storage from one container to '
                                                              'another',
                                                  formatter_class=RawTextHelpFormatter,
                                                  help='Move a folder in Azure storage from one container to another')
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


if __name__ == '__main__':
    cli()
