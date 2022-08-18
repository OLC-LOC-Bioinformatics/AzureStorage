#!/usr/bin/env python
from azure_storage.methods import \
    arg_dict_cleanup, \
    create_batch_dict, \
    create_parent_parser, \
    parse_batch_file, \
    setup_arguments
from azure_storage.azure_upload import AzureUpload
from azure_storage.azure_sas import \
    AzureContainerSAS, \
    AzureSAS
from azure_storage.azure_move import \
    AzureContainerMove, \
    AzureMove
from azure_storage.azure_download import \
    AzureContainerDownload, \
    AzureDownload
from azure_storage.azure_tier import \
    AzureContainerTier, \
    AzureTier
from azure_storage.azure_delete import \
    AzureContainerDelete, \
    AzureDelete
from argparse import \
    ArgumentParser, \
    RawTextHelpFormatter
import coloredlogs
import logging
import sys
import os


def file_upload(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureUpload class for each file
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'file', 'reset_path', 'storage_tier']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, file: $FILE_NAME...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        # Run the file upload
        try:
            # Create the upload_file object
            upload_file = AzureUpload(
                object_name=arg_dict['file'],
                account_name=args.account_name,
                container_name=arg_dict['container'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier'],
                category='file'
            )
            # Run the file upload
            upload_file.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def folder_upload(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureUpload class for each folder
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'folder', 'reset_path', 'storage_tier']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, file: $FOLDER_NAME...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the upload_folder object
            upload_folder = AzureUpload(
                object_name=arg_dict['folder'],
                account_name=args.account_name,
                container_name=arg_dict['container'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier'],
                category='folder'
            )
            # Run the folder upload
            upload_folder.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def container_sas(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureSAS class for each container
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'expiry', 'output_file']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, expiry: $EXPIRY...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the sas_container object
            sas_container = AzureContainerSAS(
                container_name=arg_dict['container'],
                output_file=arg_dict['output_file'],
                account_name=args.account_name,
                expiry=arg_dict['expiry'],
                verbosity=args.verbosity
            )
            # Run the container SAS URL creation
            sas_container.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def file_sas(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureSAS class for each file
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'file', 'expiry', 'output_file']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, file: $FILE...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the sas_file object
            sas_file = AzureSAS(
                object_name=arg_dict['file'],
                container_name=arg_dict['container'],
                output_file=arg_dict['output_file'],
                account_name=args.account_name,
                expiry=arg_dict['expiry'],
                verbosity=args.verbosity,
                category='file',
            )
            # Run the container SAS URL creation
            sas_file.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def folder_sas(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureSAS class for each file
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
        """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'folder', 'expiry', 'output_file']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, folder: $FOLDER...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the sas_file object
            sas_folder = AzureSAS(
                object_name=arg_dict['folder'],
                container_name=arg_dict['container'],
                output_file=arg_dict['output_file'],
                account_name=args.account_name,
                expiry=arg_dict['expiry'],
                verbosity=args.verbosity,
                category='folder',
            )
            # Run the container SAS URL creation
            sas_folder.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def container_copy(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureContainerMove class
    with the copy=True argument for each container
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'target', 'reset_path', 'storage_tier']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, target: $TARGET...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the copy_container object
            copy_container = AzureContainerMove(
                container_name=arg_dict['container'],
                account_name=args.account_name,
                target_container=arg_dict['target'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier'],
                copy=True
            )
            # Run the container copy
            copy_container.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def file_copy(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureMove class for each file
    with the copy=True and rename arguments
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'target', 'file', 'reset_path', 'storage_tier', 'name']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, target: $TARGET...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the copy_file object
            copy_file = AzureMove(
                object_name=arg_dict['file'],
                container_name=arg_dict['container'],
                account_name=args.account_name,
                target_container=arg_dict['target'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier'],
                category='file',
                copy=True,
                name=arg_dict['name']
            )
            # Run the file copy
            copy_file.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def folder_copy(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureMove class for each folder
    with the copy=True argument
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
        """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'target', 'folder', 'reset_path', 'storage_tier']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, target: $TARGET...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the copy_folder object
            copy_folder = AzureMove(
                object_name=arg_dict['folder'],
                container_name=arg_dict['container'],
                account_name=args.account_name,
                target_container=arg_dict['target'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier'],
                category='folder',
                copy=True
            )
            # Run the folder copy
            copy_folder.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def container_move(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureContainerMove class
    for each container
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'target', 'reset_path', 'storage_tier']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, target: $TARGET...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the move_container object
            move_container = AzureContainerMove(
                container_name=arg_dict['container'],
                account_name=args.account_name,
                target_container=arg_dict['target'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier']
            )
            # Run the container move
            move_container.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def file_move(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureMove class for each file
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'target', 'file', 'reset_path', 'storage_tier']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, target: $TARGET...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the move_file object
            move_file = AzureMove(
                object_name=arg_dict['file'],
                container_name=arg_dict['container'],
                account_name=args.account_name,
                target_container=arg_dict['target'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier'],
                category='file'
            )
            # Run the file move
            move_file.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def folder_move(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments to work with code base, run the AzureMove class for each folder
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
        """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(
            batch_file=args.batch_file,
            headers=['container', 'target', 'folder', 'reset_path', 'storage_tier']
        )
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, target: $TARGET...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the move_folder object
            move_folder = AzureMove(
                object_name=arg_dict['folder'],
                container_name=arg_dict['container'],
                account_name=args.account_name,
                target_container=arg_dict['target'],
                path=arg_dict['reset_path'],
                storage_tier=arg_dict['storage_tier'],
                category='folder'
            )
            # Run the folder move
            move_folder.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def container_download(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureContainerDownload class for each container
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'output_path'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, output_path: $OUTPUT_PATH...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the download_container object
            download_container = AzureContainerDownload(
                container_name=arg_dict['container'],
                account_name=args.account_name,
                output_path=arg_dict['output_path']
            )
            # Run the container download
            download_container.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def file_download(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureDownload class for each file
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'file', 'output_path'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, file: $FILE...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the download_file object
            download_file = AzureDownload(
                container_name=arg_dict['container'],
                object_name=arg_dict['file'],
                account_name=args.account_name,
                output_path=arg_dict['output_path'],
                category='file'
            )
            # Run the file download
            download_file.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def folder_download(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureDownload class for each folder
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'folder', 'output_path'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, folder: $FOLDER...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the download_folder object
            download_folder = AzureDownload(
                container_name=arg_dict['container'],
                object_name=arg_dict['folder'],
                account_name=args.account_name,
                output_path=arg_dict['output_path'],
                category='folder'
            )
            # Run the folder download
            download_folder.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def container_tier(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureContainerTier class for each container
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'storage_tier'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, storage_tier: $STORAGE_TIER ...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the tier_container object
            tier_container = AzureContainerTier(
                container_name=arg_dict['container'],
                account_name=args.account_name,
                storage_tier=arg_dict['storage_tier']
            )
            # Run the container tier
            tier_container.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def file_tier(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureTier class for each file
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'file', 'storage_tier'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, file: $FILE ...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the tier_file object
            tier_file = AzureTier(
                container_name=arg_dict['container'],
                object_name=arg_dict['file'],
                account_name=args.account_name,
                storage_tier=arg_dict['storage_tier'],
                category='file'
            )
            # Run the file tier
            tier_file.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def folder_tier(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureTier class for each folder
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'folder', 'storage_tier'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, folder: $FOLDER ...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the tier_folder object
            tier_folder = AzureTier(
                container_name=arg_dict['container'],
                object_name=arg_dict['folder'],
                account_name=args.account_name,
                storage_tier=arg_dict['storage_tier'],
                category='folder'
            )
            # Run the folder tier
            tier_folder.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def container_delete(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureContainerDelete class for each container
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME}, 2: {container_name: $CONTAINER_NAME}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the delete_container object
            delete_container = AzureContainerDelete(
                container_name=arg_dict['container'],
                account_name=args.account_name,
            )
            # Run the container delete
            delete_container.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def file_delete(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureDelete class for each file
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'file', 'retention_time'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, file: $FILE ...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the delete_file object
            delete_file = AzureDelete(
                container_name=arg_dict['container'],
                object_name=arg_dict['file'],
                account_name=args.account_name,
                retention_time=arg_dict['retention_time'],
                category='file'
            )
            # Run the file delete
            delete_file.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def folder_delete(args, batch_dict=None):
    """
    Read in the batch file, clean up the arguments, run the AzureDelete class for each folder
    :param args: type ArgumentParser arguments
    :param batch_dict: type Pandas dataframe.transpose().to_dict()
    """
    # If batch_dict has not been supplied by the batch function, extract the batch information from the file
    if not batch_dict:
        batch_dict = create_batch_dict(batch_file=args.batch_file,
                                       headers=['container', 'folder', 'retention_time'])
    # The format of the dictionary is: {primary key: {header: value, ...}, primary key: {header:value, ...}, ....}
    # e.g. {1 : {container_name: $CONTAINER_NAME, folder: $FOLDER ...}, 2: {container_name: ...}, ...}
    for key, arg_dict in batch_dict.items():
        # Clean up the arguments, as some are optional, or not interpreted correctly
        arg_dict = arg_dict_cleanup(arg_dict=arg_dict)
        try:
            # Create the delete_folder object
            delete_folder = AzureDelete(
                container_name=arg_dict['container'],
                object_name=arg_dict['folder'],
                account_name=args.account_name,
                retention_time=arg_dict['retention_time'],
                category='folder'
            )
            # Run the folder delete
            delete_folder.main()
        # Don't crash on SystemExits
        except SystemExit:
            pass


def batch(args):
    """
    Read in the batch file, and run the appropriate function for each requested command and subcommand combination
    :param args: type ArgumentParser arguments
    """
    # Ensure that the batch file exists
    try:
        assert os.path.isfile(args.batch_file)
    except AssertionError:
        logging.error(f'Could not locate the supplied batch file {args.batch_file}. Please ensure the you entered '
                      f'the name and path correctly')
        raise SystemExit
    # Create a dictionary of all the functions with the corresponding command and subcommands as keys
    function_dict = {
        'upload': {
            'file': file_upload,
            'folder': folder_upload
        },
        'sas': {
            'container': container_sas,
            'file': file_sas,
            'folder': folder_sas
        },
        'copy': {
            'container': container_copy,
            'file': file_copy,
            'folder': folder_copy
        },
        'move': {
            'container': container_move,
            'file': file_move,
            'folder': folder_move
        },
        'download': {
            'container': container_download,
            'file': file_download,
            'folder': folder_download
        },
        'tier': {
            'container': container_tier,
            'file': file_tier,
            'folder': folder_tier
        },
        'delete': {
            'container': container_delete,
            'file': file_delete,
            'folder': folder_delete
        }
    }
    # Read in the batch file
    with open(args.batch_file, 'r') as batch_doc:
        for line in batch_doc:
            # Ignore commented lines
            if not line.startswith('#'):
                # Convert the line to a dictionary with appropriate header: value pairs. Extract the command, and
                # subcommand
                command, subcommand, batch_dict = parse_batch_file(line=line)
                # Run the appropriate function for the supplied command, subcommand combination
                function_dict[command][subcommand](args, batch_dict=batch_dict)


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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields (one entry per line):\n '
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
        help='Tab-separated file with the following fields: \n'
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
             'container name, folder name and path, expiry (optional), output file (optional)'
    )
    sas_url_folder_subparser.set_defaults(func=folder_sas)
    # Copy subparser
    copy = subparsers.add_parser(
        parents=[],
        name='copy',
        description='Copy containers/files/folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Copy containers/files/folders in Azure storage'
    )
    copy_subparsers = copy.add_subparsers(
        title='Copy functionality',
        dest='copy'
    )
    # Container copy subparser
    copy_container_subparser = copy_subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Copy containers in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Copy containers in Azure storage'
    )
    copy_container_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields:\n '
             'container name, target container, destination path (optional), storage tier (optional)'
    )
    copy_container_subparser.set_defaults(func=container_copy)
    # File copy subparser
    copy_file_subparser = copy_subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Copy files in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Copy files in Azure storage'
    )
    copy_file_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields:\n '
             'container name, target container, file name, destination path (optional), storage tier (optional), '
             'renamed file (optional)'
    )
    copy_file_subparser.set_defaults(func=file_copy)
    # Folder copy subparser
    copy_folder_subparser = copy_subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Copy folders in Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Copy folders in Azure storage'
    )
    copy_folder_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file with the following fields:\n '
             'container name, target container, folder name, destination path (optional), storage tier (optional)'
    )
    copy_folder_subparser.set_defaults(func=folder_copy)
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='Tab-separated file with the following fields:\n '
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
        help='File with the following field:\n '
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
        help='Tab-separated file with the following fields:\n '
             'container name, file name, retention time (optional)'
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
        help='Tab-separated file with the following fields:\n '
             'container name, folder name, retention time (optional)'
    )
    delete_folder_subparser.set_defaults(func=folder_delete)
    # Batch subparser
    batch_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='batch',
        description='Perform multiple different operations in batch',
        formatter_class=RawTextHelpFormatter,
        help='Perform multiple different operations in batch'
    )
    batch_subparser.add_argument(
        '-b', '--batch_file',
        required=True,
        type=str,
        help='Tab-separated file in the following format:\n'
             'command, sub-command, arguments\n\n'
             'Below is the complete list of functionalities:\n'
             'upload, file, container name, file name, destination path (optional), storage tier (optional)\n'
             'upload, folder, container name, folder name, destination path (optional), storage tier (optional)\n'
             'sas, container, container name, expiry (optional), output file (optional)\n'
             'sas, file, container name, file name and path, expiry (optional), output file (optional)\n'
             'sas, folder, container name, folder name and path, expiry (optional), output file (optional)\n'
             'copy, container, container name, target container, destination path (optional), storage tier (optional)\n'
             'copy, file, container name, target container, file name, destination path (optional), '
             'storage tier (optional), renamed file (optional)\n'
             'copy, folder, container name, target container, folder name, destination path (optional), '
             'storage tier (optional)\n'
             'move, container, container name, target container, destination path (optional), storage tier (optional)\n'
             'move, file, container name, target container, file name, destination path (optional), '
             'storage tier (optional)\n'
             'move, folder, container name, target container, folder name, destination path (optional), '
             'storage tier (optional)\n'
             'download, container, container name, output path (optional)\n'
             'download, file, container name, file name, output path (optional)\n'
             'download, folder, container name, folder name, output path (optional)\n'
             'tier, container, container name, storage tier\n'
             'tier, file, container name, file name, storage tier\n'
             'tier, folder, container name, folder name, storage tier\n'
             'delete, container, container name\n'
             'delete, file, container name, file name, retention time (optional)\n'
             'delete, folder, container name, folder name, retention time (optional)'
    )
    batch_subparser.set_defaults(func=batch)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Operations complete')
    # Prevent the arguments being printed to the console (they are returned in order for the tests to work)
    sys.stderr = open(os.devnull, 'w')
    return arguments


if __name__ == '__main__':
    cli()
