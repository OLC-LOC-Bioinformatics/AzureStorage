#!/usr/bin/env python
from azure_storage.methods import create_parent_parser, sas_prep, setup_arguments
from azure_storage.azure_upload import AzureUpload
from argparse import ArgumentParser, RawTextHelpFormatter
import pandas as pd
import coloredlogs
import logging
import sys
import os


class AzureAutomate(object):

    def main(self):
        pass

    def __init__(self):
        pass


def file_upload(args):
    try:
        assert os.path.isfile(args.batch_file)
    except AssertionError:
        logging.error(f'Could not locate the supplied batch file {args.batch_file}. Please ensure the you entered the '
                      f'name and path correctly')
    # Read in the batch file
    batch_dict = pd.read_csv(
        args.batch_file,
        sep='\t',
        names=['container', 'file', 'reset_path', 'storage_tier']
    ).transpose().to_dict()
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional
        arg_dict['reset_path'] = arg_dict['reset_path'] if type(arg_dict['reset_path']) is not float else None
        arg_dict['storage_tier'] = arg_dict['storage_tier'] if type(arg_dict['storage_tier']) is not float else 'Hot'
        if arg_dict['reset_path'] == "''":
            arg_dict['reset_path'] = str()
        # Create the file_upload object
        file_uploader = AzureUpload(object_name=arg_dict['file'],
                                    account_name=args.account_name,
                                    container_name=arg_dict['container'],
                                    passphrase=args.passphrase,
                                    path=arg_dict['reset_path'],
                                    storage_tier=arg_dict['storage_tier'],
                                    category='file')
        try:
            file_uploader.main()
            pass
        except SystemExit as e:
            pass


def folder_upload(args):
    pass


def container_sas(args):
    pass


def file_sas(args):
    pass


def folder_sas(args):
    pass


def container_move(args):
    pass


def file_move(args):
    pass


def folder_move(args):
    pass


def container_download(args):
    pass


def file_download(args):
    pass


def folder_download(args):
    pass


def container_tier(args):
    pass


def file_tier(args):
    pass


def folder_tier(args):
    pass


def container_delete(args):
    pass


def file_delete(args):
    pass


def folder_delete(args):
    pass


def cli():
    parser = ArgumentParser(
        description='Automate the submission of multiple AzureStorage commands'
    )
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(
        parser=parser,
        container=False
    )
    # Upload parser
    upload = subparsers.add_parser(
        parents=[],
        name='upload',
        description='Upload files/folders to Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Upload files/folders to Azure storage'
    )
    # Upload subparser
    upload_subparsers = upload.add_subparsers(
        title='Upload functionality',
        dest='upload'
    )
    # File upload subparser
    upload_file_subparser = upload_subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Upload files to Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Upload files to Azure storage'
    )
    upload_file_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, file name, destination path (optional), storage tier (optional)'
    )
    upload_file_subparser.set_defaults(func=file_upload)
    # Folder upload subparser
    upload_folder_subparser = upload_subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Upload folders to Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Upload folders to Azure storage'
    )
    upload_folder_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields (one entry per line): '
             'container name, folder name, destination path (optional), storage tier (optional)'
    )

    upload_folder_subparser.set_defaults(func=folder_upload)
    # SAS URLs subparser
    sas_urls = subparsers.add_parser(
        parents=[],
        name='sas',
        description='Create SAS URLs for containers/files/folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Create SAS URLs for containers/files/folders in Azure storage')
    sas_url_subparsers = sas_urls.add_subparsers(
        title='SAS URL creation functionality',
        dest='sas'
    )
    # Container SAS URL subparser
    sas_url_container_subparser = sas_url_subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Create SAS URLs for containers in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Create SAS URLs for containers in Azure storage'
    )
    sas_url_container_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, expiry (optional), output file (optional)'
    )
    sas_url_container_subparser.set_defaults(func=container_sas)
    # File SAS URL subparser
    sas_url_file_subparser = sas_url_subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Create SAS URLs for files in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Create SAS URLs for files in Azure storage'
    )
    sas_url_file_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, file name and path, expiry (optional), output file (optional)'
    )
    sas_url_file_subparser.set_defaults(func=file_sas)
    # Folder SAS URL subparser
    sas_url_folder_subparser = sas_url_subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Create SAS URLs for folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Create SAS URLs for folders in Azure storage'
    )
    sas_url_folder_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, folder name and path, expiry (optional), output file (optional)'
    )
    sas_url_folder_subparser.set_defaults(func=folder_sas)
    # Move subparser
    move = subparsers.add_parser(
        parents=[],
        name='move',
        description='Move containers/files/folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Move containers/files/folders in Azure storage'
    )
    move_subparsers = move.add_subparsers(
        title='Move functionality',
        dest='move'
    )
    # Container move subparser
    move_container_subparser = move_subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Move containers in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Move containers in Azure storage'
    )
    move_container_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, target container, destination path (optional), storage tier (optional)'
    )
    move_container_subparser.set_defaults(func=container_move)
    # File move subparser
    move_file_subparser = move_subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Move files in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Move files in Azure storage'
    )
    move_file_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, target container, file name, destination path (optional), storage tier (optional)'
    )
    move_file_subparser.set_defaults(func=file_move)
    # Folder move subparser
    move_folder_subparser = move_subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Move folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Move folders in Azure storage'
    )
    move_folder_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, target container, folder name, destination path (optional), storage tier (optional)'
    )
    move_folder_subparser.set_defaults(func=folder_move)
    # Download subparser
    download = subparsers.add_parser(
        parents=[],
        name='download',
        description='Download containers/files/folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Download containers/files/folders in Azure storage'
    )
    download_subparsers = download.add_subparsers(
        title='Download functionality',
        dest='download'
    )
    # Container download subparser
    download_container_subparser = download_subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Download containers from Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Download containers from Azure storage'
    )
    download_container_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, output path (optional)'
    )
    download_container_subparser.set_defaults(func=container_download)
    # File download subparser
    download_file_subparser = download_subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Download files from Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Download files from Azure storage'
    )
    download_file_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, file name, output path (optional)'
    )
    download_file_subparser.set_defaults(func=file_download)
    # Folder download subparser
    download_folder_subparser = download_subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Download folders from Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Download folders from Azure storage'
    )
    download_folder_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, folder name, output path (optional)'
    )
    download_folder_subparser.set_defaults(func=folder_download)
    # Storage tier subparser
    tier = subparsers.add_parser(
        parents=[],
        name='tier',
        description='Set the storage tier of containers/files/folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Set the storage tier of containers/files/folders in Azure storage'
    )
    tier_subparsers = tier.add_subparsers(
        title='Storage tier setting functionality',
        dest='tier'
    )
    # Container storage tier subparser
    tier_container_subparser = tier_subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Set the storage tier of containers in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Set the storage tier of containers in Azure storage'
    )
    tier_container_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, storage tier'
    )
    tier_container_subparser.set_defaults(func=container_tier)
    # File storage tier subparser
    tier_file_subparser = tier_subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Set the storage tier of files in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Set the storage tier of files in Azure storage'
    )
    tier_file_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, file name, storage tier'
    )
    tier_file_subparser.set_defaults(func=file_tier)
    # Folder storage tier subparser
    tier_folder_subparser = tier_subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Set the storage tier of folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Set the storage tier of folders in Azure storage'
    )
    tier_folder_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, folder name, storage tier'
    )
    tier_folder_subparser.set_defaults(func=folder_tier)
    # Delete subparser
    delete = subparsers.add_parser(
        parents=[],
        name='delete',
        description='Delete containers/files/folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Delete containers/files/folders in Azure storage'
    )
    delete_subparsers = delete.add_subparsers(
        title='Delete functionality',
        dest='delete'
    )
    # Container delete subparser
    delete_container_subparser = delete_subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Delete containers in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Delete containers in Azure storage'
    )
    delete_container_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name'
    )
    delete_container_subparser.set_defaults(func=container_delete)
    # File delete subparser
    delete_file_subparser = delete_subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Delete files in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Delete files in Azure storage'
    )
    delete_file_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, file name'
    )
    delete_file_subparser.set_defaults(func=file_delete)
    # Folder delete subparser
    delete_folder_subparser = delete_subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Delete folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Delete folders in Azure storage'
    )
    delete_folder_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields: '
             'container name, folder name'
    )
    delete_folder_subparser.set_defaults(func=folder_delete)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Upload complete')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
