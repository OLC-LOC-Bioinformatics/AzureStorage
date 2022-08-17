#!/usr/bin/env python
from azure_storage.methods import \
    create_parent_parser, \
    setup_arguments
from azure_storage.azure_move import \
    AzureContainerMove, \
    AzureMove
from argparse import \
    ArgumentParser, \
    RawTextHelpFormatter
import coloredlogs
import logging
import sys
import os


def container_copy(args):
    """
    Run the AzureContainerMove method with the copy=True argument
    :param args: type ArgumentParser arguments
    """
    logging.info(f'Copying container {args.container_name} to {args.target_container} in Azure storage '
                 f'account {args.account_name}')
    copy_container = AzureContainerMove(
        container_name=args.container_name,
        account_name=args.account_name,
        target_container=args.target_container,
        path=args.reset_path,
        storage_tier=args.storage_tier,
        copy=True
    )
    copy_container.main()


def file_copy(args):
    """
    Run the AzureMove method for a file with the copy=True argument
    :param args: type ArgumentParser arguments
    """
    print_str = f'Copying file {args.file} from {args.container_name} to {args.target_container}'
    if args.name:
        print_str += f'and renaming it to {args.name} '
    print_str += f'in Azure storage account {args.account_name}'
    logging.info(print_str)

    copy_file = AzureMove(
        object_name=args.file,
        container_name=args.container_name,
        account_name=args.account_name,
        target_container=args.target_container,
        path=args.reset_path,
        storage_tier=args.storage_tier,
        category='file',
        copy=True,
        name=args.name
    )
    copy_file.main()


def folder_copy(args):
    """
    Run the AzureMove method for a folder with the copy=True argument
    :param args: type ArgumentParser arguments
    """
    print_str = f'Copying folder {args.file} from {args.container_name} to {args.target_container}'
    if args.name:
        print_str += f'and renaming it to {args.name} '
    print_str += f'in Azure storage account {args.account_name}'
    logging.info(print_str)
    copy_folder = AzureMove(
        object_name=args.folder,
        container_name=args.container_name,
        account_name=args.account_name,
        target_container=args.target_container,
        path=args.reset_path,
        storage_tier=args.storage_tier,
        category='folder',
        copy=True,
    )
    copy_folder.main()


def cli():
    parser = ArgumentParser(description='Copy containers, files, or folders in Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument(
        '-t', '--target_container',
        required=True,
        help='The target container to which the container/file/folder is to be copied '
             '(this cannot be the same as the container_name if you want to copy a file/folder'
             ' within a container'
    )
    parent_parser.add_argument(
        '-r', '--reset_path',
        type=str,
        help='Set the path of the container/file/folder within a folder in the target container '
             'e.g. sequence_data/220202-m05722. If you want to copy it directly in the '
             'container without any nesting, use or \'\''
    )
    parent_parser.add_argument(
        '-s', '--storage_tier',
        type=str,
        default='Hot',
        choices=['Hot', 'Cool', 'Archive'],
        metavar='STORAGE_TIER',
        help='Set the storage tier for the container/file/folder to be copied. '
             'Options are "Hot", "Cool", and "Archive". Default is Hot'
    )
    # Container copy subparser
    container_copy_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Copy a container in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Copy a container in Azure storage'
    )
    container_copy_subparser.set_defaults(func=container_copy)
    # File copy subparser
    file_copy_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Copy a file within Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Copy a file within Azure storage'
    )
    file_copy_subparser.add_argument(
        '-f', '--file',
        type=str,
        required=True,
        help='Name of blob file to copy in Azure storage. '
             'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz'
    )
    file_copy_subparser.add_argument(
        '-n', '--name',
        type=str,
        help='Name of duplicate file. Required if copying within the same container, otherwise, the original name will '
             'be used'
    )
    file_copy_subparser.set_defaults(func=file_copy)
    # Folder copy subparser
    folder_copy_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Copy a folder within Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Copy a folder within Azure storage'
    )
    folder_copy_subparser.add_argument(
        '-f', '--folder',
        type=str,
        required=True,
        help='Name of folder to copy in Azure storage. '
             'e.g. InterOp'
    )
    folder_copy_subparser.set_defaults(func=folder_copy)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Copy complete')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
