#!/usr/bin/env python
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas, RetentionPolicy
from argparse import ArgumentParser
from io import StringIO
import pandas as pd
import numpy as np
import coloredlogs
import datetime
import logging
import getpass
import keyring
import pathlib
import pandas
import azure
import time
import os
import re


def create_parent_parser(parser, container=True):
    """
    Create a parent parser with arguments common to multiple scripts
    :param parser: type ArgumentParser object
    :param container: type bool: Boolean on whether the container argument should be added to the parser
    :return: subparsers: type ArgumentParser.add_subparsers
    :return: parent_parser: type ArgumentParser: Populated ArgumentParser object
    """
    subparsers = parser.add_subparsers(title='Available functionality')
    # Create a parental parser that can be inherited by subparsers
    parent_parser = ArgumentParser(add_help=False)
    if container:
        parent_parser.add_argument('-c', '--container_name',
                                   required=True,
                                   type=str,
                                   default=str(),
                                   help='Name of the Azure storage container. Note that container names must be '
                                        'lowercase, between 3 and 63 characters, start with a letter or number, and '
                                        'can contain only letters, numbers, and the dash (-) character. Consecutive '
                                        'dashes are not permitted.')
    parent_parser.add_argument('-a', '--account_name',
                               required=True,
                               type=str,
                               help='Name of the Azure storage account')
    parent_parser.add_argument('-p', '--passphrase',
                               default='AzureStorage',
                               type=str,
                               help='The passphrase to use when encrypting the azure storage-specific connection '
                                    'string to the system keyring. Default is "AzureStorage".')
    parent_parser.add_argument('-v', '--verbosity',
                               choices=['debug', 'info', 'warning', 'error', 'critical'],
                               metavar='VERBOSITY',
                               default='info',
                               help='Set the logging level. Options are debug, info, warning, error, and critical. '
                                    'Default is info.')
    return subparsers, parent_parser


def setup_logging(arguments):
    """
    Set the custom colour scheme and message format to used by coloredlogs
    :param arguments: type parsed ArgumentParser object
    """
    # Set up logging
    coloredlogs.DEFAULT_LEVEL_STYLES = {'debug': {'bold': True, 'color': 'green'},
                                        'info': {'bold': True, 'color': 'blue'},
                                        'warning': {'bold': True, 'color': 'yellow'},
                                        'error': {'bold': True, 'color': 'red'},
                                        'critical': {'bold': True, 'background': 'red'}
                                        }
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
    coloredlogs.install(level=arguments.verbosity.upper())


def setup_arguments(parser):
    """
    Finalise setting up the ArgumentParser arguments into an object, and running subparser functions, or displaying the
    help message
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
    # If the 'func' attribute doesn't exist, display the basic help for the appropriate subparser (if any)
    else:
        try:
            # Determine which subparser was called by extracting it from the arguments. Note that this requires the
            # use of the desc keyword when creating subparsers
            command = list(vars(arguments).keys())[0]
            # If the extracted command exists, use the command-specific subparser help
            if command:
                parser.parse_args([command, '-h'])
            # Otherwise, use the basic help
            else:
                parser.parse_args(['-h'])
        # If the were no subparsers specified (the list of keys in the arguments is empty), use the basic help
        except IndexError:
            parser.parse_args(['-h'])
    return arguments


def set_account_name(passphrase, account_name=None):
    """
    Store the account name in the system keyring
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of the Azure storage account
    """
    # Only prompt the user for the account name if it was not provided
    if account_name is None:
        # Prompt the user for the account name
        account_name = input('Please enter your account name\n').encode('utf-8').decode()
    # Set the account name into the keyring. Treat it as a password, and use the passphrase as both the service ID,
    # and the username
    keyring.set_password(passphrase, passphrase, account_name)
    return account_name


def set_connection_string(passphrase, account_name):
    """
    Prompt the user for the connection string, and store it the system keyring
    Uses logic from https://stackoverflow.com/a/31882203
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of the Azure storage account
    :return: connect_str: String of the connection string
    """
    # Prompt the user for the connection string. Use decode to convert from bytes. Use getpass, so the plain text
    # password isn't printed to the screen
    connect_str = getpass.getpass(prompt='Please enter the connection string for your Azure storage account:\n')\
        .encode('utf-8').decode()
    # Ensure that the account name provided and the account name specified in the connection string match
    confirm_account_match(account_name=account_name,
                          connect_str=connect_str)
    # Set the password in the keyring. Use the passphrase as the service ID, the account name as the username,
    # and the connection string as the password
    keyring.set_password(passphrase, account_name, connect_str)
    logging.info('Successfully entered credentials into keyring')
    return connect_str


def confirm_account_match(account_name, connect_str):
    """
    Ensure that the account name provided matches the account name stored in the connection string
    :param connect_str: type str: Connection string for the Azure storage account
    :param account_name: type str: Name of the Azure storage account
    """
    # Attempt to extract the account name from the connection string
    try:
        connect_str_account_name = connect_str.split(';')[1].split('AccountName=')[-1]
        # Ensure that the account name provided matches the account name found in the connection string
        if account_name != connect_str_account_name:
            logging.error(f'The supplied account name {account_name} does not match the account name stored in the '
                          f'connection string ({connect_str_account_name}). Please ensure that you are providing the '
                          f'appropriate connection string for your account.')
            raise SystemExit
    # If splitting on 'AccountName=' fails, the connection string is either malformed or invalid
    except IndexError:
        logging.error('Could not parse the account key from the connection string in the keyring. Please ensure that '
                      'it has been entered, and the it conforms to the proper format: '
                      'DefaultEndpointsProtocol=https;AccountName=[REDACTED];AccountKey=[REDACTED];'
                      'EndpointSuffix=core.windows.net')
        raise SystemExit
    return True


def extract_connection_string(passphrase, account_name):
    """
    Extract the connection string from the keyring using the account name and passphrase
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of the Azure storage account
    :return: connect_str: String of the connection string
    """
    # Use the passphrase and the account name to extract the connection string from the keyring
    connect_str = keyring.get_password(passphrase,
                                       account_name)
    # If the connection string can't be found in the keyring using the supplied passphrase, prompt the user for
    # the passphrase, and store it
    if not connect_str:
        logging.warning(f'Connection string linked to the provided passphrase {passphrase} and account name '
                        f'{account_name} was not found in the system keyring. You will now be prompted to enter it.')
        connect_str = set_connection_string(passphrase=passphrase,
                                            account_name=account_name)
    # Confirm that the account name provided matches the one found in the connection string
    confirm_account_match(account_name=account_name,
                          connect_str=connect_str)
    return connect_str


def extract_account_name(passphrase):
    """
    Extract the account name from the system keyring
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :return: account_name: Name of the Azure storage account
    """
    # Use the passphrase to extract the account name
    account_name = keyring.get_password(passphrase,
                                        passphrase)
    # If the account name hasn't been entered into the keyring, prompt the user to enter it
    if not account_name:
        logging.warning(f'Account name linked to the provided passphrase {passphrase} was not found in the system '
                        f'keyring. You will now be prompted to enter it.')
        account_name = set_account_name(passphrase=passphrase)
    return account_name


def extract_account_key(connect_str):
    """
    Extract the account key from the connection string. This is necessary for the method that creates the blob SAS,
    as it doesn't accept connection strings
    :param connect_str: type str: Connection string for the Azure storage account
    :return account_key: String of the account key extracted from the connection string
    """
    # Split the connection string on ';', use the entry corresponding to the account key, and strip off the
    # 'AccountKey='
    # DefaultEndpointsProtocol=https;AccountName=[REDACTED];AccountKey=[REDACTED];EndpointSuffix=core.windows.net
    try:
        account_key = connect_str.split(';')[2].split('AccountKey=')[-1]
    except IndexError:
        logging.error(
            'Could not parse the account key from the connection string in the keyring. Please ensure that it has been '
            'entered, and the it conforms to the proper format: '
            'DefaultEndpointsProtocol=https;AccountName=[REDACTED];AccountKey=[REDACTED];'
            'EndpointSuffix=core.windows.net')
        raise SystemExit
    return account_key


def delete_keyring_credentials(passphrase, account_name=None):
    """
    Delete the password associated with the passphrase and account name from the system keyring
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of the Azure storage account
    :return: account_name: Name of the Azure storage account
    """
    if not account_name:
        # Prompt the user for the account name
        account_name = input('Please enter your account name\n').encode('utf-8').decode()
    try:
        # Delete the password from the system keyring
        keyring.delete_password(passphrase, account_name)
    except keyring.errors.PasswordDeleteError:
        logging.error(
            f'Connection string associated with passphrase {passphrase} and account name {account_name} not found in '
            f'system keyring. Please ensure that you supplied the correct arguments.')
        raise SystemExit
    return account_name


def validate_container_name(container_name, object_type='container'):
    """
    Use a regex to check if the supplied name follows the guidelines for Azure nomenclature. If it doesn't, attempt to
    rename the container/object
    :param container_name: type str: Name of the container/object of interest
    :param object_type: type str: Name of the object being validated. Default is container, but target container, and
    target path are other options
    :return: container_name: String of sanitised container name
    """
    if not re.match('^[a-z0-9](?!.*--)[a-z0-9-]{1,61}[a-z0-9]$', container_name):
        logging.warning(
            f'{object_type.capitalize()} name, {container_name} is invalid. {object_type.capitalize()} names must be '
            f'between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and '
            f'the dash (-) character. Every dash (-) character must be immediately preceded and followed by a letter '
            f'or number; consecutive dashes are not permitted in {object_type} names. All letters in a {object_type} '
            f'name must be lowercase.')
        logging.info(f'Attempting to fix the {object_type} name')
        # Swap out dashes for underscores, as they will be removed in the following regex
        container_name = container_name.replace('-', '_')
        # Use re to remove all non-word characters (including dashes)
        container_name = re.sub(r'[^\w]', '', container_name)
        # Replace multiple underscores with a single one. Uses logic from: https://stackoverflow.com/a/46701355
        # Also ensure that the container name is in lowercase
        container_name = re.sub(r'[^\w\s]|(_)(?=\1)', '', container_name).lower()
        # Swap out underscores for dashes
        container_name = container_name.replace('_', '-')
        # Ensure that the container name doesn't start or end with a dash
        container_name = re.sub(r'^-+', '', container_name)
        container_name = re.sub(r'-+$', '', container_name)
    # Ensure that the container name isn't length zero, or the while loop below will be infinite
    if len(container_name) == 0:
        logging.error(
            f'Attempting to fix the {object_type} name left zero valid characters! Please enter a new name.')
        raise SystemExit
    # If the container name is too long, slice it to be 63 characters
    if len(container_name) >= 63:
        logging.warning(
            f'{object_type.capitalize()} name {container_name} was too long. Using {container_name[:62]} instead')
        container_name = container_name[:62]
    # If the container name is too short, keep adding the container name to itself to bump up the length
    while len(container_name) < 3:
        logging.warning(
            f'{object_type.capitalize()} name {container_name} was too short (only {len(container_name)} characters). '
            f'Using {container_name + container_name} instead')
        container_name = container_name + container_name
    # Use the validated container name
    logging.info(f'Using {container_name} as the {object_type} name')
    return container_name


def create_blob_service_client(connect_str):
    """
    Create a blob service client using the connection string
    :param connect_str: type str: Connection string for Azure storage
    :return: blob_service_client: type azure.storage.blob.BlobServiceClient
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        return blob_service_client
    except ValueError:
        logging.error('Your connection string was rejected. Please ensure that you entered it properly, and that it '
                      'is valid')
        raise SystemExit


def create_container(blob_service_client, container_name):
    """
    Create a new container and container-specific client from the blob service client
    :param blob_service_client: type: type azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :return: container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
    logging.getLogger().setLevel(logging.WARNING)
    try:
        container_client = blob_service_client.create_container(container_name)
    except azure.core.exceptions.ResourceExistsError as e:
        if 'The specified container already exists.' in str(e):
            container_client = create_container_client(blob_service_client=blob_service_client,
                                                       container_name=container_name)
        elif 'The specified container is being deleted. Try operation later.' in str(e):
            logging.error(f'Could not create the requested container {container_name}. As it has recently been '
                          f'deleted, please try again in a few moments')
            raise SystemExit
        else:
            logging.error(f'Could not create container {container_name}')
            raise SystemExit
    return container_client


def create_container_client(blob_service_client, container_name, create=True):
    """
    Create a container-specific client from the blob service client
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param create: type bool: Boolean whether to create a container if it doesn't exist
    :return: container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Create the container client from the blob service client with the get container client method
    # and the container name
    container_client = blob_service_client.get_container_client(container_name)
    # Create the container if it does not exist
    if not container_client.exists() and create:
        container_client = create_container(blob_service_client=blob_service_client,
                                            container_name=container_name)
    return container_client


def create_blob_client(blob_service_client, container_name, blob_file):
    """
    Create a blob-specific client
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param blob_file: type iterable from azure.storage.blob.BlobServiceClient.ContainerClient.list_blobs
    :return: blob_client: type azure.storage.blob.BlobServiceClient.BlobClient
    """
    # Create a blob client for the current blob
    blob_client = blob_service_client.get_blob_client(container=container_name,
                                                      blob=blob_file)
    return blob_client


def create_blob_sas(blob_file, account_name, container_name, account_key, expiry, sas_urls):
    """
    Create SAS URL for blob
    :param blob_file: type container_client.list_blobs() object
    :param account_name: type str: Name of Azure storage account
    :param container_name: type str: Name of container in Azure storage in which the file is located
    :param account_key: type str: Account key of Azure storage account
    :param expiry: type int: Number of days that the SAS URL will be valid
    :param sas_urls: type dict: Dictionary of file name: SAS URL (empty)
    :return: populated sas_urls
    """
    # Set the name of file by removing any path information
    file_name = os.path.basename(blob_file.name)
    # Create the blob SAS. Use a start time 15 minutes in the past, and the requested expiry
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_file.name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        start=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(days=expiry))
    # Create the SAS URL, and add it to the dictionary with the file_name as the key
    sas_urls[file_name] = create_sas_url(account_name=account_name,
                                         container_name=container_name,
                                         blob_name=blob_file.name,
                                         sas_token=sas_token)
    return sas_urls


def client_prep(container_name, passphrase, account_name, create=True):
    """
    Validate the container name, and prepare the necessary clients
    :param container_name: type str: Name of the container of interest
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of the Azure storage account
    :param create: type bool: Boolean whether to create a container if it doesn't exist
    :return: container_name: Validated container name
    :return: connect_str: String of the connection string
    :return: blob_service_client: azure.storage.blob.BlobServiceClient
    :return: container_client: azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Validate the container name
    container_name = validate_container_name(container_name=container_name)
    # Extract the connection string from the system keyring
    connect_str = extract_connection_string(passphrase=passphrase,
                                            account_name=account_name)
    # Create the blob service client using the connection string
    blob_service_client = create_blob_service_client(connect_str=connect_str)
    # Create the container client for the desired container with the blob service client
    container_client = create_container_client(blob_service_client=blob_service_client,
                                               container_name=container_name,
                                               create=create)
    return container_name, connect_str, blob_service_client, container_client


def sas_prep(container_name, passphrase, account_name, create=True):
    """
    Validate container names, extract connection strings, and account keys, and create necessary clients for
    SAS URL creation
    :param container_name: type str: Name of the container of interest
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of the Azure storage account
    :param create: type bool: Boolean whether to create a container if it doesn't exist
    :return: container_name: Validated container name
    :return: connect_str: Connection string for Azure storage
    :return: account_key: Account key for Azure storage
    :return: blob_service_client: azure.storage.blob.BlobServiceClient
    :return: container_client: azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Validate the container name
    container_name = validate_container_name(container_name=container_name)
    # Retrieve the connection string from the system keyring
    connect_str = extract_connection_string(passphrase=passphrase,
                                            account_name=account_name)
    # Extract the account key from the connection string
    account_key = extract_account_key(connect_str=connect_str)
    # Create the blob service client
    blob_service_client = create_blob_service_client(connect_str=connect_str)
    # Create the container client from the blob service client
    container_client = create_container_client(blob_service_client=blob_service_client,
                                               container_name=container_name,
                                               create=create)
    return container_name, connect_str, account_key, blob_service_client, container_client


def create_sas_url(account_name, container_name, blob_name, sas_token):
    """
    Create the SAS URL from the required components
    :param account_name: type str: Name of Azure storage account
    :param container_name: type str: Name of the container of interest
    :param blob_name: type str: Name and path of the file of interest
    :param sas_token: type azure.storage.blob.generate_blob_sas
    :return: sas_url: String of the SAS URL
    """
    # Generate the SAS URL using the account name, the domain, the container name, the blob name, and the
    # SAS token in the following format:
    # 'https://' + account_name + '.blob.core.windows.net/' + container_name + '/' + blob_name + '?' + blob
    sas_url = f'https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}'
    return sas_url


def write_sas(output_file, sas_urls):
    """
    Write the SAS URLs to the output file
    :param output_file: type str: Name and path of the file in which the SAS URLs are to be written
    :param sas_urls: type dict: Dictionary of file name: SAS URL
    """
    # Create the output file
    with open(output_file, 'w') as output:
        for file_name, sas_url in sas_urls.items():
            # Write the SAS URL to the output file
            output.write(f'{sas_url}\n')
            # Print the file name and SAS URL to the terminal
            logging.info(f'{file_name}\t{sas_url}')


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
    blob_service_client.set_service_properties(delete_retention_policy=delete_retention_policy)
    return blob_service_client


def move_prep(passphrase, account_name, container_name, target_container):
    """
    Prepare all the necessary clients for moving container/files/folders in Azure storage
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of Azure storage account
    :param container_name: type str: Name of the container of interest
    :param target_container: type str: Name of the new container into which the container/file/folder is to be copied
    :return: blob_service_client: type azure.storage.blob.BlobServiceClient
    :return: source_container_client: type azure.storage.blob.BlobServiceClient.ContainerClient for source container
    :return: target_container_client: type azure.storage.blob.BlobServiceClient.ContainerClient for target container
    """
    # Validate the container names
    container_name = validate_container_name(container_name=container_name)
    target_container = validate_container_name(container_name=target_container,
                                               object_type='target container')
    # Extract the connection string from the system keyring
    connect_str = extract_connection_string(passphrase=passphrase,
                                            account_name=account_name)
    blob_service_client = create_blob_service_client(connect_str=connect_str)
    source_container_client = create_container_client(blob_service_client=blob_service_client,
                                                      container_name=container_name)
    # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
    logging.getLogger().setLevel(logging.WARNING)
    target_container_client = create_container(blob_service_client=blob_service_client,
                                               container_name=target_container)
    return container_name, target_container, blob_service_client, source_container_client, target_container_client


def copy_blob(blob_file, blob_service_client, container_name, target_container, path, storage_tier,
              object_name=None, category=None, common_path=None):
    """
    Copy a blob from one container to another
    :param blob_file: type iterable from azure.storage.blob.BlobServiceClient.ContainerClient.list_blobs
    :param container_name: type str: Name of the container in which the file is located
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param target_container: type str: Name of the new container into which the file is to be copied
    :param path: type str: Path of folders in which the files are to be placed
    :param storage_tier: type str: Storage tier to use for the copied file/folder
    :param object_name: type str: Name and path of file/folder to download from Azure storage
    :param category: type str: Category of object to be copied. Limited to file or folder
    :param common_path: type str: Calculated common path between the specified file/folder and the blob_file.name
    """
    # Create the blob client
    blob_client = create_blob_client(blob_service_client=blob_service_client,
                                     container_name=container_name,
                                     blob_file=blob_file)
    # Extract the folder structure of the blob e.g. 220202-m05722/InterOp
    folder_structure = list(os.path.split(os.path.dirname(blob_file.name)))
    # Add the nested folder to the path as requested
    target_path = os.path.join(path, os.path.join(*folder_structure))
    # Set the name of file by removing any path information
    file_name = os.path.basename(blob_file.name)
    # Finally, set the name and the path of the output file
    if category is None:
        target_file = os.path.join(path, file_name)
    # If a folder is being moved, join the path, the common path between the blob file and the supplied folder name
    # with the file name
    else:
        if object_name is not None:
            target_file = os.path.join(path, common_path, os.path.basename(blob_file.name))
        # If a container is being moved, join the target path and the name of the directory of the blob_file to the
        # file name
        else:
            # Create a pathlib.Path object from the blob file
            file_path = pathlib.Path(blob_file.name)
            # Determine the parental path of the file. If the file is in the root, it will be a dot. This won't work
            # with the joining logic, so change it to ''
            nested_path = file_path.parent if file_path.parent == '.' else ''
            # Join the target path, nested path, and file name
            target_file = os.path.join(target_path, nested_path, file_name)
    # Create a blob client for the target blob
    target_blob_client = blob_service_client.get_blob_client(target_container, target_file)
    # Copy the source file to the target file - allow up to 1000 seconds total
    target_blob_client.start_copy_from_url(blob_client.url)
    # Set the storage tier
    target_blob_client.set_standard_blob_tier(standard_blob_tier=storage_tier)
    # Ensure that the copy is complete before proceeding
    for i in range(100):
        # Extract the properties of the target blob client
        target_blob_properties = target_blob_client.get_blob_properties()
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
    except azure.core.exceptions.ResourceNotFoundError:
        logging.error(f'Could not locate {container_name} in {account_name}. Perhaps it has already been deleted?')
        raise SystemExit


def extract_common_path(object_name, blob_file):
    """
    Extract the common path (if any) between a file in Azure storage, and a user-supplied folder name
    :param object_name: type str: Name and path of file/folder to download from Azure storage
    :param blob_file: type iterable from azure.storage.blob.BlobServiceClient.ContainerClient.list_blobs
    :return: common_path: The calculated common path between the folder and the file in blob storage (can be None)
    """
    # Create the pathlib.Path objects for both the folder and the blob file
    object_path = pathlib.Path(os.path.normpath(object_name))
    blob_path = pathlib.Path(blob_file.name).parent
    # If there is a common path between the folder and the blob file path, then there is a match
    try:
        common_path = blob_path.relative_to(object_path)
        # Change the dot returned by an exact match to the directory with ''
        common_path = common_path if str(common_path) != '.' else ''
    except ValueError:
        common_path = None
    return common_path


def delete_file(container_client, object_name, blob_service_client, container_name):
    """
    Delete a file from Azure storage
    :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
    :param object_name: type str: Name and path of file/folder to download from Azure storage
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
            blob_client = create_blob_client(blob_service_client=blob_service_client,
                                             container_name=container_name,
                                             blob_file=blob_file)
            # Soft delete the blob
            blob_client.delete_blob()
    # Send a warning to the user that the blob could not be found
    if not present:
        logging.error(f'Could not locate the desired file {object_name}')
        raise SystemExit


def delete_folder(container_client, object_name, blob_service_client, container_name, account_name):
    """
    Delete a folder from Azure storage
    :param container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
    :param object_name: type str: Name and path of file/folder to download from Azure storage
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param account_name: type str: Name of the Azure storage account
    """
    # Create a generator containing all the blobs in the container
    generator = container_client.list_blobs()
    # Create a boolean to determine if the blob has been located
    present = False
    for blob_file in generator:
        common_path = extract_common_path(object_name=object_name,
                                          blob_file=blob_file)
        # Only copy the file if there is a common path between the object path and the blob path (they match)
        if common_path is not None:
            # Update the folder presence boolean
            present = True
            # Create the blob client
            blob_client = create_blob_client(blob_service_client=blob_service_client,
                                             container_name=container_name,
                                             blob_file=blob_file)
            # Soft delete the blob
            blob_client.delete_blob()
    # Log an error that the folder could not be found
    if not present:
        logging.error(
            f'There was an error deleting folder {object_name} in container {container_name}, '
            f'in Azure storage account {account_name}. Please ensure that all arguments have been '
            f'entered correctly')
        raise SystemExit


def arg_dict_cleanup(arg_dict):
    """
    Clean up the argument dictionary to be consistent with the format required for the AzureStorage classes
    :param arg_dict: type dict: Dictionary of argument name: value e.g. storage tier: nan
    :return: arg_dict: Cleaned argument dictionary
    """
    try:
        # Double single quotes are not automatically changed into an empty string
        arg_dict['reset_path'] = arg_dict['reset_path'] if arg_dict['reset_path'] != "''" else str()
    except KeyError:
        pass
    # For optional argument, the nan value supplied for empty values will not work with downstream code; find and
    # change them to the appropriate empty/default value
    try:
        arg_dict['reset_path'] = arg_dict['reset_path'] if str(arg_dict['reset_path']) != str(np.nan) else None
    except KeyError:
        pass
    try:
        arg_dict['storage_tier'] = arg_dict['storage_tier'] if str(arg_dict['storage_tier']) != str(np.nan) else 'Hot'
    except KeyError:
        pass
    try:
        arg_dict['output_file'] = arg_dict['output_file'] if str(arg_dict['output_file']) != str(np.nan) \
            else os.path.join(os.getcwd(), 'sas_urls.txt')
    except KeyError:
        pass
    try:
        arg_dict['output_path'] = arg_dict['output_path'] if str(arg_dict['output_path']) != str(np.nan) \
            else os.getcwd()
    except KeyError:
        pass
    try:
        arg_dict['expiry'] = arg_dict['expiry'] if str(arg_dict['expiry']) != str(np.nan) else 10
    except KeyError:
        pass
    try:
        arg_dict['retention_time'] = arg_dict['retention_time'] if str(arg_dict['retention_time']) != str(np.nan) else 8
    except KeyError:
        pass
    # Reading in numerical container names e.g. 220202 returns an integer, so typecast it to string
    arg_dict['container'] = str(arg_dict['container'])
    try:
        arg_dict['target'] = str(arg_dict['target'])
    except KeyError:
        pass
    return arg_dict


def create_batch_dict(batch_file, headers):
    """
    Read in the supplied file of arguments with pandas. Create a dictionary of the arguments from a transposed dataframe
    :param batch_file: type str: Name and path of file containing requested operations
    :param headers: type list: Names of all the headers present in the file
    :return: Pandas dataframe.transpose().to_dict() of header: value extracted from the desired operation
    """
    # Ensure that the batch file exists
    try:
        assert os.path.isfile(batch_file)
    except AssertionError:
        logging.error(f'Could not locate the supplied batch file {batch_file}. Please ensure the you entered '
                      f'the name and path correctly')
        raise SystemExit
    # Read in the batch file using pandas.read_csv. Use tabs as the separator, and provide the header names.
    # Transpose the data, and convert the dataframe to a dictionary
    batch_dict = pd.read_csv(
        batch_file,
        sep='\t',
        names=headers
    ).transpose().to_dict()
    return batch_dict


def parse_batch_file(line):
    """
    Extract the requested command and subcommand from a line from an AzureAutomate batch file. Create a dictionary with
    the appropriate header:value for that command and subcommand combination
    :param line: type str: Individual line of text from batch file detailing requested operations. Format is:
    command;subcommand;operation-specific arguments
    :return: command: type str: Desired command to run e.g. upload, sas, move, download, tier, delete
    :return: subcommand: Subcommand for operation e.g. container, file, folder
    :return: batch_dict: Pandas dataframe.transpose().to_dict() of header: value extracted from the desired operation
    """
    # Create a dictionary of the appropriate headers for each command and subcommand combination
    header_dict = {
        'upload': {
            'file': ['command', 'subcommand', 'container', 'file', 'reset_path', 'storage_tier'],
            'folder': ['command', 'subcommand', 'container', 'folder', 'reset_path', 'storage_tier']
        },
        'sas': {
            'container': ['command', 'subcommand', 'container', 'expiry', 'output_file'],
            'file': ['command', 'subcommand', 'container', 'file', 'expiry', 'output_file'],
            'folder': ['command', 'subcommand', 'container', 'folder', 'expiry', 'output_file']
        },
        'move': {
            'container': ['command', 'subcommand', 'container', 'target', 'reset_path', 'storage_tier'],
            'file': ['command', 'subcommand', 'container', 'target', 'file', 'reset_path', 'storage_tier'],
            'folder': ['command', 'subcommand', 'container', 'target', 'folder', 'reset_path', 'storage_tier']
        },
        'download': {
            'container': ['command', 'subcommand', 'container', 'output_path'],
            'file': ['command', 'subcommand', 'container', 'file', 'output_path'],
            'folder': ['command', 'subcommand', 'container', 'folder', 'output_path']
        },
        'tier': {
            'container': ['command', 'subcommand', 'container', 'storage_tier'],
            'file': ['command', 'subcommand', 'container', 'file', 'storage_tier'],
            'folder': ['command', 'subcommand', 'container', 'folder', 'storage_tier']
        },
        'delete': {
            'container': ['command', 'subcommand', 'container'],
            'file': ['command', 'subcommand', 'container', 'file', 'retention_time'],
            'folder': ['command', 'subcommand', 'container', 'folder', 'retention_time']
        }
    }
    # Extract the command and subcommand from the line. They will be the first two entries
    try:
        command = line.split('\t')[0]
        subcommand = line.split('\t')[1]
    except IndexError:
        logging.error(f'Could not extract the desired command and subcommand from your file. Please review the '
                      f'following line {line}')
        raise SystemExit
    # Use the extracted command and subcommand to determine the appropriate headers
    try:
        headers = header_dict[command][subcommand]
    except KeyError:
        logging.error(f'Could not find the requested command {command} and subcommand {subcommand} in the list of '
                      f'commands. Please ensure that you created your batch file correctly')
        raise SystemExit
    # Use StringIO to convert the string into a format that can be read by pandas.read_csv
    input_string = StringIO(line.rstrip())
    # Read in the line using pandas.read_csv. Use tabs as the separator, and provide the header names.
    # Transpose the data, and convert the dataframe to a dictionary
    try:
        batch_dict = pd.read_csv(
            input_string,
            sep='\t',
            names=headers
        ).transpose().to_dict()
    except pandas.errors.ParserError:
        raise SystemExit
    # Return the command, subcommand, and parsed dictionary
    return command, subcommand, batch_dict
