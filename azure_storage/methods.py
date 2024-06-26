#!/usr/bin/env python

"""
Collection of methods for AzureStorage scripts
"""

# Standard imports
from argparse import ArgumentParser
import datetime
import getpass
from io import StringIO
import logging
import os
import pathlib
import re
import time


# Third party imports
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    generate_blob_sas,
    RetentionPolicy
)
import coloredlogs
from cryptography.fernet import Fernet
import pandas as pd
import numpy as np


def create_parent_parser(parser, container=True):
    """
    Create a parent parser with arguments common to multiple scripts
    :param parser: type ArgumentParser object
    :param container: type bool: Boolean on whether the container argument
        should be added to the parser
    :return: subparsers: type ArgumentParser.add_subparsers
    :return: parent_parser: type ArgumentParser: Populated ArgumentParser
        object
    """
    subparsers = parser.add_subparsers(title='Available functionality')
    # Create a parental parser that can be inherited by subparsers
    parent_parser = ArgumentParser(add_help=False)
    if container:
        parent_parser.add_argument(
            '-c', '--container_name', required=True, type=str, default=str(),
            help='Name of the Azure storage container. Note that container '
            'names must be lowercase, between 3 and 63 characters, start with '
            'a letter or number, and can contain only letters, numbers, and '
            'the dash (-) character. Consecutive dashes are not permitted.'
        )
    parent_parser.add_argument(
        '-a', '--account_name',
        required=True,
        type=str,
        help='Name of the Azure storage account'
    )
    parent_parser.add_argument(
        '-v',
        '--verbosity',
        choices=[
            'debug',
            'info',
            'warning',
            'error',
            'critical'],
        metavar='VERBOSITY',
        default='info',
        help='Set the logging level. Options are debug, info, warning, error, '
        'and critical. Default is info.'
    )
    return subparsers, parent_parser


def setup_logging(arguments):
    """
    Set the custom colour scheme and message format to used by coloredlogs
    :param arguments: type parsed ArgumentParser object
    """
    # Set up logging
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        'debug': {
            'bold': True, 'color': 'green'},
        'info': {
            'bold': True, 'color': 'blue'},
        'warning': {
            'bold': True, 'color': 'yellow'},
        'error': {
            'bold': True, 'color': 'red'},
        'critical': {
            'bold': True, 'background': 'red'}

    }
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
    coloredlogs.install(level=arguments.verbosity.upper())


def setup_arguments(parser):
    """
    Finalise setting up the ArgumentParser arguments into an object, and
    running subparser functions, or displaying the help message
    :param parser: type: ArgumentParser object
    :return: parsed ArgumentParser object
    """
    # Get the arguments into an object
    arguments = parser.parse_args()
    # Run the appropriate function for each sub-parser.
    if hasattr(arguments, 'func'):
        # Set up logging
        setup_logging(arguments=arguments)
        arguments.func(arguments)
    # If the 'func' attribute doesn't exist, display the basic help for the
    # appropriate subparser (if any)
    else:
        try:
            # Determine which subparser was called by extracting it from the
            # arguments. Note that this requires the use of the desc keyword
            # when creating subparsers
            command = list(vars(arguments).keys())[0]
            # If the extracted command exists, use the command-specific
            # subparser help
            if command:
                parser.parse_args([command, '-h'])
            # Otherwise, use the basic help
            else:
                parser.parse_args(['-h'])
        # If there were no subparsers specified (the list of keys in the
        # arguments is empty), use the basic help
        except IndexError:
            parser.parse_args(['-h'])
    return arguments


def confirm_account_match(account_name, connect_str):
    """
    Ensure that the account name provided matches the account name stored in
    the connection string
    :param connect_str: type str: Connection string for the Azure
        storage account
    :param account_name: type str: Name of the Azure storage account
    """
    # Attempt to extract the account name from the connection string
    try:
        connect_str_account_name = connect_str.split(
            ';')[1].split('AccountName=')[-1]
        # Ensure that the account name provided matches the account name found
        # in the connection string
        if account_name != connect_str_account_name:
            logging.error(
                'The supplied account name %s does not match the account name '
                'stored in the connection string (%s). Please ensure that you '
                'are providing the appropriate connection string for your '
                'account.',
                account_name, connect_str_account_name
            )
            raise SystemExit
    # If splitting on 'AccountName=' fails, the connection string is either
    # malformed or invalid
    except IndexError as exc:
        logging.error(
            'Could not parse the account key from the connection string. '
            'Please ensure that it has been entered, and the it conforms to '
            'the proper format: DefaultEndpointsProtocol=https;'
            'AccountName=[REDACTED];AccountKey=[REDACTED];'
            'EndpointSuffix=core.windows.net')
        raise SystemExit from exc
    return True


def extract_account_key(connect_str):
    """
    Extract the account key from the connection string. This is necessary for
    the method that creates the blob SAS,
    as it doesn't accept connection strings
    :param connect_str: type str: Connection string for the Azure storage
        account
    :return account_key: String of the account key extracted from the
        connection string
    """
    # Split the connection string on ';', use the entry corresponding to the
    # account key, and strip off the
    # 'AccountKey='
    # DefaultEndpointsProtocol=https;AccountName=[REDACTED];AccountKey=
    # [REDACTED];EndpointSuffix=core.windows.net
    try:
        account_key = connect_str.split(';')[2].split('AccountKey=')[-1]
    except IndexError as exc:
        logging.error(
            'Could not parse the account key from the connection string. '
            'Please ensure that it has been entered, and the it conforms to '
            'the proper format: DefaultEndpointsProtocol=https;'
            'AccountName=[REDACTED];AccountKey=[REDACTED];'
            'EndpointSuffix=core.windows.net')
        raise SystemExit from exc
    return account_key


def create_encryption_key_file(credentials_key):
    """
    Use Fernet to generate an encryption key to be used to encrypt Azure
    connection string
    :param credentials_key: Name and path of the file in which the encryption
        key will be stored
    """
    # Key generation
    key = Fernet.generate_key()
    # Store the key in a file
    with open(credentials_key, 'wb') as file_key:
        file_key.write(key)


def read_encryption_key(credentials_key):
    """
    Read in encryption key from file, and process it with Fernet
    :param credentials_key: Name and path of the file in which the encryption
        key will be stored
    :return: fernet: type cryptography.fernet.Fernet: Encryption key
    """
    # Open the key file
    with open(credentials_key, 'rb') as file_key:
        key = file_key.read()
    # Use the generated key
    fernet = Fernet(key)
    return fernet


def set_credential_files(account_name):
    """
    Determine the local path of this file, and use it to set the path of the
    files to store the encrypted Azure credentials and the key to decrypt
    the file
    :return: credentials_file: type str: Name and path of the file in which
        encrypted credentials are to be stored
    :return: credentials_key: type str: Name and path of the file in which the
        encryption key is to be stored
    """
    # Extract the local path of the methods.py file, so the credentials files
    # can be created in the same location
    file_path = os.path.dirname(os.path.realpath(__file__))
    # Set the names of the credentials storing file and the key file
    credentials_file = os.path.join(
        file_path, f'{account_name}_credentials.txt')
    credentials_key = os.path.join(
        file_path, f'{account_name}_credentials.key')
    return credentials_file, credentials_key


def encrypt_credentials(account_name):
    """
    Prompt user for Azure connection string. Store string in Fernet
    encrypted file
    :return: connect_str: type str: Decrypted connection string
    """
    connect_str = getpass.getpass(
        prompt=f'Please enter the connection string for your Azure storage '
        f'account {account_name}\n').encode('utf-8').decode()
    # Confirm that the account name provided matches the one found in the
    # connection string
    confirm_account_match(
        account_name=account_name,
        connect_str=connect_str
    )
    # Set the names of the credentials storing file and the key file
    credentials_file, credentials_key = set_credential_files(account_name)
    # Write the credentials to file
    with open(credentials_file, 'w', encoding='utf-8') as credentials:
        credentials.write(f'{connect_str}')
    # Create an encryption key to encrypt the file
    create_encryption_key_file(credentials_key=credentials_key)
    fernet = read_encryption_key(credentials_key=credentials_key)
    # Open the original file to encrypt
    with open(credentials_file, 'rb') as file:
        original = file.read()
    # Encrypt the file
    encrypted = fernet.encrypt(original)
    # Open the file in write mode and write the encrypted data
    with open(credentials_file, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)
    return connect_str


def decrypt_credentials(account_name):
    """
    Decrypt the credentials from file
    :return: connect_str: type str: Decrypted connection string
    """
    # Set the names of the credentials storing file and the key file
    credentials_file, credentials_key = set_credential_files(
        account_name=account_name)
    if not os.path.isfile(credentials_file):
        logging.warning(
            'Credentials for the provided account name %s could not be '
            'located. You will now be prompted to enter your connection '
            'string.',
            account_name
        )
        encrypt_credentials(account_name=account_name)
    # Read in and decrypt the encryption key
    fernet = read_encryption_key(credentials_key=credentials_key)
    # Open the encrypted file
    with open(credentials_file, 'rb') as enc_file:
        encrypted = enc_file.read()
    # Decrypt the file to extract the connection string
    connect_str = fernet.decrypt(encrypted).decode()
    # Confirm that the account name provided matches the one found in the
    # connection string
    confirm_account_match(
        account_name=account_name,
        connect_str=connect_str
    )
    return connect_str


def delete_credentials_files(account_name):
    """
    Delete the credentials key and the encrypted credentials files
    """
    # Set the names of the credentials storing file and the key file
    credentials_file, credentials_key = set_credential_files(
        account_name=account_name)
    # Ensure that the file exists before trying to delete
    if os.path.isfile(credentials_file):
        os.remove(credentials_file)
    else:
        logging.error(
            'Could not located credentials files associated with account %s',
            account_name
        )
        raise SystemExit
    if os.path.isfile(credentials_key):
        os.remove(credentials_key)


def validate_container_name(container_name, object_type='container'):
    """
    Use a regex to check if the supplied name follows the guidelines for Azure
    nomenclature. If it doesn't, attempt to rename the container/object
    :param container_name: type str: Name of the container/object of interest
    :param object_type: type str: Name of the object being validated.
        Default is container, but target container, and target path are
        other options
    :return: container_name: String of sanitised container name
    """
    if not re.match(
        '^[a-z0-9](?!.*--)[a-z0-9-]{1,61}[a-z0-9]$',
            container_name):
        logging.warning(
            '%s name, %s is invalid. {object_type.capitalize()} names must be '
            'between 3 and 63 characters, start with a letter or number, and '
            'can contain only letters, numbers, and the dash (-) character. '
            'Every dash (-) character must be immediately preceded and '
            'followed by a letter or number; consecutive dashes are not '
            'permitted in %s names. All letters in a %s name must be '
            'lowercase.',
            object_type.capitalize(), container_name, object_type, object_type
        )
        logging.info('Attempting to fix the %s name', object_type)
        # Swap out dashes for underscores, as they will be removed in the
        # following regex
        container_name = container_name.replace('-', '_')
        # Use re to remove all non-word characters (including dashes)
        container_name = re.sub(r'\W', '', container_name)
        # Replace multiple underscores with a single one. Uses logic from:
        # https://stackoverflow.com/a/46701355
        # Also ensure that the container name is in lowercase
        container_name = re.sub(
            r'[^\w\s]|(_)(?=\1)', '', container_name).lower()
        # Swap out underscores for dashes
        container_name = container_name.replace('_', '-')
        # Ensure that the container name doesn't start or end with a dash
        container_name = re.sub(r'^-+', '', container_name)
        container_name = re.sub(r'-+$', '', container_name)
    # Ensure that the container name isn't length zero, or the while loop
    # below will be infinite
    if len(container_name) == 0:
        logging.error(
            'Attempting to fix the %s name left zero valid characters! '
            'Please enter a new name.',
            object_type
        )
        raise SystemExit
    # If the container name is too long, slice it to be 63 characters
    if len(container_name) >= 63:
        logging.warning(
            '%s name %s was too long. Using %s instead',
            object_type.capitalize(), container_name, container_name[:62]
        )
        container_name = container_name[:62]
    # If the container name is too short, keep adding the container name to
    # itself to bump up the length
    while len(container_name) < 3:
        logging.warning(
            '%s name {container_name} was too short (only %s characters). '
            'Using %s instead',
            container_name,
            len(container_name),
            container_name + container_name
        )
        container_name = container_name + container_name
    # Use the validated container name
    logging.info('Using %s as the %s name', container_name, object_type)
    return container_name


def create_blob_service_client(connect_str):
    """
    Create a blob service client using the connection string
    :param connect_str: type str: Connection string for Azure storage
    :return: blob_service_client: type azure.storage.blob.BlobServiceClient
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)
        return blob_service_client
    except ValueError as exc:
        logging.error(
            'Your connection string was rejected. Please ensure that you '
            'entered it properly, and that it is valid'
        )
        raise SystemExit from exc


def create_container(blob_service_client, container_name):
    """
    Create a new container and container-specific client from the blob
    service client
    :param blob_service_client: type: type azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :return: container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Hide the INFO-level messages sent to the logger from Azure by increasing
    # the logging level to WARNING
    logging.getLogger().setLevel(logging.WARNING)
    try:
        container_client = blob_service_client.create_container(container_name)
    except ResourceExistsError as exc:
        if 'The specified container already exists.' in str(exc):
            container_client = create_container_client(
                blob_service_client=blob_service_client,
                container_name=container_name
            )
        elif 'The specified container is being deleted. Try operation later.' \
                in str(exc):
            logging.error(
                'Could not create the requested container %s. As it has '
                'recently been deleted, please try again in a few moments',
                container_name
            )
            raise SystemExit from exc
        else:
            logging.error('Could not create container %s', container_name)
            raise SystemExit from exc
    return container_client


def create_container_client(blob_service_client, container_name, create=True):
    """
    Create a container-specific client from the blob service client
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param create: type bool: Boolean whether to create a container if it
        doesn't exist
    :return: container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Create the container client from the blob service client with the get
    # container client method and the container name
    container_client = blob_service_client.get_container_client(container_name)
    # Create the container if it does not exist
    if not container_client.exists() and create:
        container_client = create_container(
            blob_service_client=blob_service_client,
            container_name=container_name
        )
    return container_client


def create_blob_client(blob_service_client, container_name, blob_file):
    """
    Create a blob-specific client
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param blob_file: type iterable from
        azure.storage.blob.BlobServiceClient.ContainerClient.list_blobs
    :return: blob_client: type azure.storage.blob.BlobServiceClient.BlobClient
    """
    # Create a blob client for the current blob
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_file
    )
    return blob_client


def create_blob_sas(
        blob_file,
        account_name,
        container_name,
        account_key,
        expiry,
        sas_urls):
    """
    Create SAS URL for blob
    :param blob_file: type container_client.list_blobs() object
    :param account_name: type str: Name of Azure storage account
    :param container_name: type str: Name of container in Azure storage in
        which the file is located
    :param account_key: type str: Account key of Azure storage account
    :param expiry: type int: Number of days that the SAS URL will be valid
    :param sas_urls: type dict: Dictionary of file name: SAS URL (empty)
    :return: populated sas_urls
    """
    # Set the name of file by removing any path information
    file_name = os.path.basename(blob_file.name)
    # Create the blob SAS. Use a start time 15 minutes in the past, and the
    # requested expiry
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_file.name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        start=datetime.datetime.now(datetime.timezone.utc) -
        datetime.timedelta(minutes=15),
        expiry=datetime.datetime.now(datetime.timezone.utc) +
        datetime.timedelta(days=expiry)
    )
    # Create the SAS URL, and add it to the dictionary with the file_name as
    # the key
    sas_urls[file_name] = create_sas_url(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_file.name,
        sas_token=sas_token
    )
    return sas_urls


def client_prep(container_name, account_name, create=True):
    """
    Validate the container name, and prepare the necessary clients
    :param container_name: type str: Name of the container of interest
    :param account_name: type str: Name of the Azure storage account
    :param create: type bool: Boolean whether to create a container if it
        doesn't exist
    :return: container_name: Validated container name
    :return: connect_str: String of the connection string
    :return: blob_service_client: azure.storage.blob.BlobServiceClient
    :return: container_client:
        azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Validate the container name
    container_name = validate_container_name(container_name=container_name)
    # Extract the connection string
    connect_str = decrypt_credentials(account_name=account_name)
    # Create the blob service client using the connection string
    blob_service_client = create_blob_service_client(connect_str=connect_str)
    # Create the container client for the desired container with the blob
    # service client
    container_client = create_container_client(
        blob_service_client=blob_service_client,
        container_name=container_name,
        create=create
    )
    return container_name, connect_str, blob_service_client, container_client


def sas_prep(container_name, account_name, create=True):
    """
    Validate container names, extract connection strings, and account keys,
    and create necessary clients for SAS URL creation
    :param container_name: type str: Name of the container of interest
    :param account_name: type str: Name of the Azure storage account
    :param create: type bool: Boolean whether to create a container if it
        doesn't exist
    :return: container_name: Validated container name
    :return: connect_str: Connection string for Azure storage
    :return: account_key: Account key for Azure storage
    :return: blob_service_client: azure.storage.blob.BlobServiceClient
    :return: container_client:
        azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Validate the container name
    container_name = validate_container_name(container_name=container_name)
    # Retrieve the connection string
    connect_str = decrypt_credentials(account_name=account_name)
    # Extract the account key from the connection string
    account_key = extract_account_key(connect_str=connect_str)
    # Create the blob service client
    blob_service_client = create_blob_service_client(connect_str=connect_str)
    # Create the container client from the blob service client
    container_client = create_container_client(
        blob_service_client=blob_service_client,
        container_name=container_name,
        create=create
    )
    return container_name, connect_str, account_key, blob_service_client, \
        container_client


def create_sas_url(account_name, container_name, blob_name, sas_token):
    """
    Create the SAS URL from the required components
    :param account_name: type str: Name of Azure storage account
    :param container_name: type str: Name of the container of interest
    :param blob_name: type str: Name and path of the file of interest
    :param sas_token: type azure.storage.blob.generate_blob_sas
    :return: sas_url: String of the SAS URL
    """
    # Generate the SAS URL using the account name, the domain, the container
    # name, the blob name, and the SAS token in the following format:
    # 'https://' + account_name + '.blob.core.windows.net/' + container_name
    # + '/' + blob_name + '?' + blob
    sas_url = f'https://{account_name}.blob.core.windows.net/' \
              f'{container_name}/{blob_name}?{sas_token}'
    return sas_url


def write_sas(output_file, sas_urls):
    """
    Write the SAS URLs to the output file
    :param output_file: type str: Name and path of the file in which the SAS
        URLs are to be written
    :param sas_urls: type dict: Dictionary of file name: SAS URL
    """
    # Create the output file
    with open(output_file, 'w', encoding='utf-8') as output:
        for file_name, sas_url in sas_urls.items():
            # Write the SAS URL to the output file
            output.write(f'{sas_url}\n')
            # Print the file name and SAS URL to the terminal
            logging.info('%s\t%s', file_name, sas_url)


def set_blob_retention_policy(blob_service_client, days=8):
    """
    Set the retention policy for a blob
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param days: type int: Number of days to retain deleted blobs. Default is 8
    :return: blob_service_client: Client with the retention policy implemented
    """
    # Create a retention policy to retain deleted blobs
    delete_retention_policy = RetentionPolicy(enabled=True, days=days)
    # Set the retention policy on the service
    blob_service_client.set_service_properties(
        delete_retention_policy=delete_retention_policy)
    return blob_service_client


def move_prep(account_name, container_name, target_container):
    """
    Prepare all the necessary clients for moving container/files/folders in
    Azure storage
    :param account_name: type str: Name of Azure storage account
    :param container_name: type str: Name of the container of interest
    :param target_container: type str: Name of the new container into which
        the container/file/folder is to be copied
    :return: blob_service_client: type azure.storage.blob.BlobServiceClient
    :return: source_container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient for
        source container
    :return: target_container_client:
        type azure.storage.blob.BlobServiceClient.ContainerClient for
        target container
    """
    # Validate the container names
    container_name = validate_container_name(container_name=container_name)
    target_container = validate_container_name(
        container_name=target_container,
        object_type='target container'
    )
    # Retrieve the connection string
    connect_str = decrypt_credentials(account_name=account_name)
    blob_service_client = create_blob_service_client(connect_str=connect_str)
    source_container_client = create_container_client(
        blob_service_client=blob_service_client,
        container_name=container_name
    )
    # Hide the INFO-level messages sent to the logger from Azure by increasing
    # the logging level to WARNING
    logging.getLogger().setLevel(logging.WARNING)
    target_container_client = create_container(
        blob_service_client=blob_service_client,
        container_name=target_container
    )
    return container_name, target_container, blob_service_client, \
        source_container_client, target_container_client


def copy_blob(
        blob_file,
        blob_service_client,
        container_name,
        target_container,
        path,
        storage_tier,
        object_name=None,
        category=None,
        common_path=None,
        rename=None):
    """
    Copy a blob from one container to another
    :param blob_file: type iterable from
        azure.storage.blob.BlobServiceClient.ContainerClient.list_blobs
    :param container_name: type str: Name of the container in which the file
        is located
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param target_container: type str: Name of the new container into which
        the file is to be copied
    :param path: type str: Path of folders in which the files are to be placed
    :param storage_tier: type str: Storage tier to use for the copied
        file/folder
    :param object_name: type str: Name and path of file/folder to download
        from Azure storage
    :param category: type str: Category of object to be copied. Limited to
        file or folder
    :param common_path: type str: Calculated common path between the specified
        file/folder and the blob_file.name
    :param rename: type str: Desired string to use to rename the file
    """
    # Create the blob client
    blob_client = create_blob_client(
        blob_service_client=blob_service_client,
        container_name=container_name,
        blob_file=blob_file
    )
    # Extract the folder structure of the blob e.g. 220202-m05722/InterOp
    folder_structure = list(os.path.split(os.path.dirname(blob_file.name)))
    # Add the nested folder to the path as requested
    if path is not None:
        if category != 'container':
            target_path = path
        else:
            target_path = os.path.join(path, *folder_structure)
    else:
        target_path = os.path.join(*folder_structure)

    # Set the name of file by removing any path information
    file_name = os.path.basename(blob_file.name)
    # Finally, set the name and the path of the output file
    if category is None:
        if rename and not isinstance(rename, float):
            target_file = os.path.join(target_path, rename)
        else:
            target_file = os.path.join(target_path, file_name)
    # If a folder is being moved, join the path, the common path between the
    # blob file and the supplied folder name with the file name
    else:
        if object_name is not None:
            if path is not None:
                target_file = os.path.join(
                    path, common_path, os.path.basename(
                        blob_file.name))
            else:
                target_file = os.path.join(common_path, blob_file.name)
        # If a container is being moved, join the target path and the name of
        # the directory of the blob_file to the file name
        else:
            # Create a pathlib.Path object from the blob file
            file_path = pathlib.Path(blob_file.name)
            # Determine the parental path of the file. If the file is in the
            # root, it will be a dot. This won't work with the joining logic,
            # so change it to ''
            nested_path = file_path.parent if file_path.parent == '.' else ''
            # Join the target path, nested path, and file name
            target_file = os.path.join(target_path, nested_path, file_name)
    # Create a blob client for the target blob
    target_blob_client = blob_service_client.get_blob_client(
        target_container, target_file)
    # Copy the source file to the target file - allow up to 1000 seconds total
    target_blob_client.start_copy_from_url(blob_client.url)
    # Set the storage tier
    target_blob_client.set_standard_blob_tier(standard_blob_tier=storage_tier)
    # Ensure that the copy is complete before proceeding
    for _ in range(100):
        # Extract the properties of the target blob client
        target_blob_properties = target_blob_client.get_blob_properties()
        logging.debug(
            'Copy status of %s from %s to %s as %s: %s',
            blob_file.name,
            container_name,
            target_container,
            target_file,
            target_blob_properties.copy.status
        )
        # Break when the status is set to 'success'. The copy is successful
        if target_blob_properties.copy.status == 'success':
            # Copy finished
            break
        # Sleep for 10 seconds
        time.sleep(10)


def delete_container(blob_service_client, container_name, account_name):
    """
    Delete a container in Azure storage
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param account_name: type str: Name of the Azure storage account
    """
    # Delete container if it exists
    try:
        blob_service_client.delete_container(container_name)
    except ResourceNotFoundError as exc:
        logging.error(
            'Could not locate %s in %s. Perhaps it has already been deleted?',
            container_name, account_name)
        raise SystemExit from exc


def extract_common_path(object_name, blob_file):
    """
    Extract the common path (if any) between a file in Azure storage, and a
    user-supplied folder name
    :param object_name: type str: Name and path of file/folder to download
        from Azure storage
    :param blob_file: type iterable from
        azure.storage.blob.BlobServiceClient.ContainerClient.list_blobs
    :return: common_path: The calculated common path between the folder and
        the file in blob storage (can be None)
    """
    # Create the pathlib.Path objects for both the folder and the blob file
    object_path = pathlib.Path(os.path.normpath(object_name))
    blob_path = pathlib.Path(blob_file.name).parent
    # If there is a common path between the folder and the blob file path,
    # then there is a match
    try:
        common_path = blob_path.relative_to(object_path)
        # Change the dot returned by an exact match to the directory with ''
        common_path = common_path if str(common_path) != '.' else ''
    except ValueError:
        common_path = None
    return common_path


def delete_file(
        container_client,
        object_name,
        blob_service_client,
        container_name):
    """
    Delete a file from Azure storage
    :param container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
    :param object_name: type str: Name and path of file/folder to download
        from Azure storage
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    """
    # Create a generator containing all the blobs in the container
    generator = container_client.list_blobs()
    # Create a boolean to determine if the blob has been located
    present = False
    for blob_file in generator:
        # Filter for the blob name
        if os.path.join(blob_file.name) == object_name:
            # Update the blob presence variable
            present = True
            # Create the blob client
            blob_client = create_blob_client(
                blob_service_client=blob_service_client,
                container_name=container_name,
                blob_file=blob_file
            )
            # Soft delete the blob
            blob_client.delete_blob()
    # Send a warning to the user that the blob could not be found
    if not present:
        logging.error(
            'Could not locate the desired file %s',
            object_name
        )
        raise SystemExit


def delete_folder(
        container_client,
        object_name,
        blob_service_client,
        container_name,
        account_name):
    """
    Delete a folder from Azure storage
    :param container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
    :param object_name: type str: Name and path of file/folder to download
        from Azure storage
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param account_name: type str: Name of the Azure storage account
    """
    # Create a generator containing all the blobs in the container
    generator = container_client.list_blobs()
    # Create a boolean to determine if the blob has been located
    present = False
    for blob_file in generator:
        common_path = extract_common_path(
            object_name=object_name,
            blob_file=blob_file
        )
        # Only copy the file if there is a common path between the object path
        # and the blob path (they match)
        if common_path is not None:
            # Update the folder presence boolean
            present = True
            # Create the blob client
            blob_client = create_blob_client(
                blob_service_client=blob_service_client,
                container_name=container_name,
                blob_file=blob_file
            )
            # Soft delete the blob
            blob_client.delete_blob()
    # Log an error that the folder could not be found
    if not present:
        logging.error(
            'There was an error deleting folder %s in container %s, '
            'in Azure storage account %s. Please ensure that all arguments '
            'have been entered correctly',
            object_name, container_name, account_name
        )
        raise SystemExit


def arg_dict_cleanup(arg_dict):
    """
    Clean up the argument dictionary to be consistent with the format required
    for the AzureStorage classes
    :param arg_dict: type dict: Dictionary of argument name: value e.g.
        storage tier: nan
    :return: arg_dict: Cleaned argument dictionary
    """
    try:
        # Double single quotes are not automatically changed into an empty
        # string
        arg_dict['reset_path'] = arg_dict['reset_path'] if \
            arg_dict['reset_path'] != "''" else str()
    except KeyError:
        pass
    # For optional argument, the nan value supplied for empty values will not
    # work with downstream code; find and change them to the appropriate
    # empty/default value
    try:
        arg_dict['reset_path'] = arg_dict['reset_path'] if str(
            arg_dict['reset_path']) != str(np.nan) else None
    except KeyError:
        pass
    try:
        arg_dict['storage_tier'] = arg_dict['storage_tier'] if str(
            arg_dict['storage_tier']) != str(np.nan) else 'Hot'
    except KeyError:
        pass
    try:
        arg_dict['output_file'] = arg_dict['output_file'] if str(
            arg_dict['output_file']) != str(
            np.nan) else os.path.join(
            os.getcwd(),
            'sas_urls.txt')
    except KeyError:
        pass
    try:
        arg_dict['output_path'] = arg_dict['output_path'] if str(
            arg_dict['output_path']) != str(np.nan) else os.getcwd()
    except KeyError:
        pass
    try:
        arg_dict['expiry'] = arg_dict['expiry'] if str(
            arg_dict['expiry']) != str(np.nan) else 10
    except KeyError:
        pass
    try:
        arg_dict['retention_time'] = arg_dict['retention_time'] if str(
            arg_dict['retention_time']) != str(np.nan) else 8
    except KeyError:
        pass
    # Reading in numerical container names e.g. 220202 returns an integer, so
    # typecast it to string
    arg_dict['container'] = str(arg_dict['container'])
    try:
        arg_dict['target'] = str(arg_dict['target'])
    except KeyError:
        pass
    return arg_dict


def create_batch_dict(batch_file, headers):
    """
    Read in the supplied file of arguments with pandas. Create a dictionary of
    the arguments from a transposed dataframe
    :param batch_file: type str: Name and path of file containing requested
        operations
    :param headers: type list: Names of all the headers present in the file
    :return: Pandas dataframe.transpose().to_dict() of header: value extracted
        from the desired operation
    """
    # Ensure that the batch file exists
    try:
        assert os.path.isfile(batch_file)
    except AssertionError as exc:
        logging.error(
            'Could not locate the supplied batch file %s. Please ensure the '
            'you entered the name and path correctly',
            batch_file
        )
        raise SystemExit from exc
    # Read in the batch file using pandas.read_csv. Use tabs as the separator,
    # and provide the header names. Transpose the data, and convert the
    # dataframe to a dictionary
    batch_dict = pd.read_csv(
        batch_file,
        sep='\t',
        names=headers
    ).transpose().to_dict()
    return batch_dict


def parse_batch_file(line):
    """
    Extract the requested command and subcommand from a line from an
    AzureAutomate batch file. Create a dictionary with the appropriate
    header:value for that command and subcommand combination
    :param line: type str: Individual line of text from batch file detailing
        requested operations. Format is:
        command;subcommand;operation-specific arguments
    :return: command: type str: Desired command to run e.g. upload, sas, move,
        download, tier, delete
    :return: subcommand: Subcommand for operation e.g. container, file, folder
    :return: batch_dict: Pandas dataframe.transpose().to_dict() of
        header: value extracted from the desired operation
    """
    # Create a dictionary of the appropriate headers for each command and
    # subcommand combination
    header_dict = {
        'upload': {
            'file': [
                'command',
                'subcommand',
                'container',
                'file',
                'reset_path',
                'storage_tier'
            ],
            'folder': [
                'command',
                'subcommand',
                'container',
                'folder',
                'reset_path',
                'storage_tier'
            ]
        },
        'sas': {
            'container': [
                'command',
                'subcommand',
                'container',
                'expiry',
                'output_file'
            ],
            'file': [
                'command',
                'subcommand',
                'container',
                'file',
                'expiry',
                'output_file'
            ],
            'folder': [
                'command',
                'subcommand',
                'container',
                'folder',
                'expiry',
                'output_file'
            ]
        },
        'copy': {
            'container': [
                'command',
                'subcommand',
                'container',
                'target',
                'reset_path',
                'storage_tier'
            ],
            'file': [
                'command',
                'subcommand',
                'container',
                'target',
                'file',
                'reset_path',
                'storage_tier',
                'name'
            ],
            'folder': [
                'command',
                'subcommand',
                'container',
                'target',
                'folder',
                'reset_path',
                'storage_tier'
            ]
        },
        'move': {
            'container': [
                'command',
                'subcommand',
                'container',
                'target',
                'reset_path',
                'storage_tier'
            ],
            'file': [
                'command',
                'subcommand',
                'container',
                'target',
                'file',
                'reset_path',
                'storage_tier'
            ],
            'folder': [
                'command',
                'subcommand',
                'container',
                'target',
                'folder',
                'reset_path',
                'storage_tier'
            ]
        },
        'download': {
            'container': [
                'command',
                'subcommand',
                'container',
                'output_path'
            ],
            'file': [
                'command',
                'subcommand',
                'container',
                'file',
                'output_path'
            ],
            'folder': [
                'command',
                'subcommand',
                'container',
                'folder',
                'output_path'
            ]
        },
        'tier': {
            'container': [
                'command',
                'subcommand',
                'container',
                'storage_tier'
            ],
            'file': [
                'command',
                'subcommand',
                'container',
                'file',
                'storage_tier'
            ],
            'folder': [
                'command',
                'subcommand',
                'container',
                'folder',
                'storage_tier'
            ]
        },
        'delete': {
            'container': [
                'command',
                'subcommand',
                'container'
            ],
            'file': [
                'command',
                'subcommand',
                'container',
                'file',
                'retention_time'
            ],
            'folder': [
                'command',
                'subcommand',
                'container',
                'folder',
                'retention_time'
            ]
        }
    }
    # Extract the command and subcommand from the line. They will be the first
    # two entries
    try:
        command = line.split('\t')[0]
        subcommand = line.split('\t')[1]
    except IndexError as exc:
        logging.error(
            'Could not extract the desired command and subcommand from your '
            'file. Please review the following line %s',
            line
        )
        raise SystemExit from exc
    # Use the extracted command and subcommand to determine the appropriate
    # headers
    try:
        headers = header_dict[command][subcommand]
    except KeyError as exc:
        logging.error(
            'Could not find the requested command %s and subcommand %s in '
            'the list of commands. Please ensure that you created your batch '
            'file correctly',
            command, subcommand
        )
        raise SystemExit from exc
    # Use StringIO to convert the string into a format that can be read by
    # pandas.read_csv
    input_string = StringIO(line.rstrip())
    # Read in the line using pandas.read_csv. Use tabs as the separator, and
    # provide the header names. Transpose the data, and convert the dataframe
    # o a dictionary
    try:
        batch_dict = pd.read_csv(
            input_string,
            sep='\t',
            names=headers
        ).transpose().to_dict()
    except pd.errors.ParserError as exc:
        logging.error('Pandas error parsing data: %s', exc)
        raise SystemExit from exc
    # Return the command, subcommand, and parsed dictionary
    return command, subcommand, batch_dict
