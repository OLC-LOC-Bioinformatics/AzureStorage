#!/usr/bin/env python
from azure_storage.methods import set_connection_string, setup_arguments
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
    parser.add_argument('-a', '--account_name',
                        required=True,
                        type=str,
                        help='Name of the Azure storage account')
    parser.add_argument('-p', '--passphrase',
                        default='AzureDownload',
                        type=str,
                        help='The passphrase to use when encrypting the azure storage-specific connection '
                             'string to the system keyring. Default is "AzureDownload".')
    parser.add_argument('-v', '--verbosity',
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        default='info',
                        help='Set the logging level. Default is info.')
    parser.set_defaults(func=credentials)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    return arguments


if __name__ == '__main__':
    cli()
