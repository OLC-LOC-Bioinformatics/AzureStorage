#!/usr/bin/env python
from azure_storage.methods import create_parent_parser, set_connection_string, setup_arguments
from argparse import ArgumentParser
import logging


def credentials(args):
    """
    Run the credentials setting methods
    :param args: type ArgumentParser arguments
    """
    logging.info('Setting Azure storage credentials')
    # Run the credentials setting method
    set_connection_string(passphrase=args.passphrase,
                          account_name=args.account_name)


def cli():
    parser = ArgumentParser(description='Set or modify Azure storage credentials in the system keyring')
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser,
                                                     container=False)
    parser.set_defaults(func=credentials)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    return arguments


if __name__ == '__main__':
    cli()
