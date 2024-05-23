#!/usr/bin/env python
"""
Set, modify, or delete Azure storage credentials
"""

# Standard imports
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)
import logging
import sys
import os

# Local imports
from azure_storage.methods import (
    create_parent_parser,
    setup_arguments,
    encrypt_credentials,
    delete_credentials_files
)


def store_credentials(args):
    """
    Run the credentials setting methods
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Storing Azure storage credentials for account %s',
        args.account_name
    )
    encrypt_credentials(account_name=args.account_name)


def delete_credentials(args):
    """
    Run the credentials deleting methods
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Deleting Azure storage credentials for account %s',
        args.account_name
    )
    # Delete the credentials files
    delete_credentials_files(account_name=args.account_name)


def cli():
    """
    Command Line Interface (CLI) function for managing Azure storage
    credentials.

    This function sets up argument parsing for the CLI, including subparsers
    for storing/modifying and deleting credentials.

    The function then sets up the arguments and runs the appropriate subparser
    based on the provided arguments.

    After the operation is complete, the function suppresses further
    console output.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = ArgumentParser(
        description='Set, modify, or delete Azure storage credentials'
    )
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(
        parser=parser,
        container=False
    )
    # Credentials storing/modifying subparser
    store_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='store',
        description='Store or update Azure storage credentials',
        formatter_class=RawTextHelpFormatter,
        help='Store or update Azure storage credentials'
    )
    store_subparser.set_defaults(func=store_credentials)
    # Credentials deleting subparser
    delete_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='delete',
        description='Delete Azure storage credentials',
        formatter_class=RawTextHelpFormatter,
        help='Delete Azure storage credentials'
    )
    delete_subparser.set_defaults(func=delete_credentials)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Prevent the arguments being printed to the console (they are returned in
    # order for the tests to work)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    return arguments


if __name__ == '__main__':
    cli()
