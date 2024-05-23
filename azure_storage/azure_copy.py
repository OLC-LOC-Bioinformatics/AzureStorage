#!/usr/bin/env python

"""
Copy containers, files, or folders in Azure storage
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
from azure_storage.methods import (
    create_parent_parser,
    setup_arguments
)
from azure_storage.azure_move import (
    AzureContainerMove,
    AzureMove
)
import coloredlogs


def container_copy(args):
    """
    Run the AzureContainerMove method with the copy=True argument
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Copying container %s to %s in Azure storage account %s',
        args.container_name, args.target_container, args.account_name
    )
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
    print_str = f'Copying file {
        args.file}  from {
        args.container_name}  to {
        args.target_container} '
    if args.reset_path:
        print_str += f'. Changing path to {args.reset_path}'
    if args.name:
        print_str += f' and renaming it to {args.name}'
    print_str += f' in Azure storage account {args.account_name}'
    logging.info(print_str)
    # Ensure that the source file and target file are different
    if args.container_name == args.target_container:
        source_file = os.path.join(args.container_name, args.file)
        if args.name == os.path.basename(args.file):
            logging.error(
                'Could not detect a difference between the source file: %s '
                'and the target file: %s. You may be simply overwriting the '
                'source file with itself.',
                source_file, source_file
            )
            raise SystemExit
        # Check if reset_path argument is not provided and name argument is
        # not provided or if the directory of the file argument is the same
        # as the reset_path argument
        if not args.reset_path and not args.name or (
            os.path.dirname(
                args.file) == os.path.normpath(
                args.reset_path)):

            # Join container_name and file arguments to create the source
            # file path
            source_file = os.path.join(args.container_name, args.file)

            # If reset_path argument is provided
            if args.reset_path is not None:
                # Join target_container, reset_path, and the base name of the
                # file argument to create the target file path
                target_file = os.path.join(
                    args.target_container,
                    args.reset_path,
                    os.path.basename(
                        args.file))
            else:
                # If reset_path argument is not provided, join
                # target_container and the base name of the file argument to
                # create the target file path
                target_file = os.path.join(
                    args.target_container,
                    os.path.basename(
                        args.file))
            logging.error(
                'Could not detect a difference between the source file: %s '
                'and the target file: %s. You may be simply overwriting the '
                'source file with itself.',
                source_file, target_file
                )
            raise SystemExit
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
    print_str = f'Copying folder {
        args.folder}  from {
        args.container_name}  to {
        args.target_container} '
    if args.reset_path:
        print_str += f'and renaming it to {args.reset_path} '
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
    """
    Command Line Interface (CLI) function for copying containers, files, or
    folders in Azure storage.

    This function sets up argument parsing for the CLI, including arguments
    for the target container, reset path, and storage tier. It also sets up
    subparsers for copying a container, a file, or a folder.

    The function then sets up the arguments and runs the appropriate subparser
    based on the provided arguments.

    After the copy operation is complete, the function logs a completion
    message and suppresses further console output.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = ArgumentParser(
        description='Copy containers, files, or folders in Azure storage')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument(
        '-t', '--target_container', required=True,
        help='The target container to which the container/file/folder is to '
        'be copied (this cannot be the same as the container_name if you want '
        'to copy a file/folder within a container'
    )
    parent_parser.add_argument(
        '-r', '--reset_path', type=str,
        help='Set the path of the container/file/folder within a folder in '
        'the target container e.g. sequence_data/220202-m05722. If you want '
        'to copy it directly in the container without any nesting, use or \'\''
    )
    parent_parser.add_argument(
        '-s', '--storage_tier', type=str, default='Hot',
        choices=['Hot', 'Cool', 'Archive'],
        metavar='STORAGE_TIER',
        help='Set the storage tier for the container/file/folder to be copied.'
        ' Options are "Hot", "Cool", and "Archive". Default is Hot')
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
        '-n', '--name', type=str,
        help='Name of duplicate file. Required if copying within the same '
        'container (and folder). Otherwise, the original name will be used.'
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
    # Return to the requested logging level, as it has been increased to
    # WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Copy complete')
    # Prevent the arguments being printed to the console (they are returned in
    # order for the tests to work)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    return arguments


if __name__ == '__main__':
    cli()
