#!/usr/bin/env python
from azure_storage.methods import create_blob_client, create_container, create_container_client, \
    create_blob_service_client, create_parent_parser, delete_container, extract_connection_string, setup_arguments, \
    validate_container_name
from argparse import ArgumentParser, RawTextHelpFormatter
import coloredlogs
import logging
import azure
import time
import os


class AzureContainerMove(object):

    def main(self):
        self.connect_str = extract_connection_string(passphrase=self.passphrase,
                                                     account_name=self.account_name)
        self.blob_service_client = create_blob_service_client(connect_str=self.connect_str)
        self.source_container_client = create_container_client(blob_service_client=self.blob_service_client,
                                                               container_name=self.container_name)
        # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        try:
            self.target_container_client = create_container(blob_service_client=self.blob_service_client,
                                                            container_name=self.target_container)
        except azure.core.exceptions.ResourceExistsError:
            self.target_container_client = create_container_client(blob_service_client=self.blob_service_client,
                                                                   container_name=self.target_container)
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
                # Create the blob client
                blob_client = create_blob_client(blob_service_client=self.blob_service_client,
                                                 container_name=self.container_name,
                                                 blob_file=blob_file)
                # Extract the folder structure of the blob e.g. 220202-m05722/InterOp
                folder_structure = list(os.path.split(os.path.dirname(blob_file.name)))
                # Add the nested folder to the path as requested
                if not self.nested:
                    # Determine the path to output the file. Join the name of the container and the joined (splatted)
                    # folder structure. Logic: https://stackoverflow.com/a/14826889
                    target_path = os.path.join(os.path.join(*folder_structure))
                else:
                    nested_structure = [self.nested] + folder_structure
                    target_path = os.path.join(os.path.join(*nested_structure))
                # Set the name of file by removing any path information
                file_name = os.path.basename(blob_file.name)
                # Finally, set the name and the path of the output file
                target_file = os.path.join(target_path, file_name)
                # Create a blob client for the target blob
                target_blob_client = self.blob_service_client.get_blob_client(self.target_container,
                                                                              target_file)
                # Copy the source file to the target file - allow 1000 seconds total
                target_blob_client.start_copy_from_url(blob_client.url)
                # Ensure that the copy is complete before proceeding
                for i in range(100):
                    # Extract the properties of the target blob client
                    target_blob_properties = target_blob_client.get_blob_properties()
                    # Break when the status is
                    if target_blob_properties.copy.status == 'success':
                        # Copy finished
                        break
                    # Sleep for 10 seconds
                    time.sleep(10)
        except azure.core.exceptions.ResourceNotFoundError:
            logging.error(f' The specified container, {self.container_name}, does not exist.')

    def __init__(self, container_name, account_name, passphrase, target_container, nested):
        # Set the container name variable
        self.container_name = container_name
        # Initialise necessary class variables
        self.passphrase = passphrase
        self.account_name = account_name
        self.target_container = target_container
        self.nested = nested
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
                                       nested=args.nested)
    del_container.main()


def file_move(args):
    pass


def folder_move(args):
    pass


def cli():
    parser = ArgumentParser(description='Move containers, files, or folders in Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument('-t', '--target_container',
                               required=True,
                               help='The target container to which the file is to be moved '
                                    'e.g. sequence_data')
    parent_parser.add_argument('-n', '--nested',
                               type=str,
                               help='Nest the container/file/folder within a folder in the target container '
                                    'e.g. sequence_data/220202-m05722 where "220202-m05722" is the argument')
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
                                       help='Name of blob folder to move in Azure storage. '
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
