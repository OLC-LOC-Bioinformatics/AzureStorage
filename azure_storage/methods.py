#!/usr/bin/env python
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas, RetentionPolicy
from argparse import ArgumentParser
import coloredlogs
import datetime
import logging
import getpass
import keyring
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
                                   help='Name of the Azure storage container')
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
                               default='info',
                               help='Set the logging level. Default is info.')
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
    # If the 'func' attribute doesn't exist, display the basic help
    else:
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
        logging.error('Could not parse the account key from the connection string in the keyring. Please ensure that '
                      'it has been entered, and the it conforms to the proper format: '
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
        logging.error(f'Connection string associated with passphrase {passphrase} and account name {account_name} '
                      f'not found in system keyring. Please ensure that you supplied the correct arguments.')
        raise SystemExit
    return account_name


def extract_container_name(object_name):
    """
    Extract the name of the container in which the blob is to be downloaded
    :param object_name: type str: Name and path of file/folder to download from Azure storage
    :return: container_name: String of the container name extracted from the object name
    """
    # Split the container name from the file name (and possibly path). Use the first entry.
    # For a blob: 220202-m05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz yields 220202-m05722
    # For a folder: 220202-m05722/InterOp yields 220202-m05722
    container_name = object_name.split('/')[0]
    return container_name


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
        logging.warning(f'{object_type.capitalize()} name, {container_name} is invalid. {object_type.capitalize()} '
                        f'names must be between 3 and 63 characters, start with a letter or number, and can contain '
                        f'only letters, numbers, and the dash (-) character. Every dash (-) character must be '
                        f'immediately preceded and followed by a letter or number; consecutive dashes are not '
                        f'permitted in {object_type} names. All letters in a {object_type} name must be lowercase.')
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
        logging.error(f'Attempting to fix the {object_type} name left zero valid characters! '
                      'Please enter a new name.')
        raise SystemExit
    # If the container name is too long, slice it to be 63 characters
    if len(container_name) >= 63:
        logging.warning(f'{object_type.capitalize()} name {container_name} was too long. Using {container_name[:62]} '
                        f'instead')
        container_name = container_name[:62]
    # If the container name is too short, keep adding the container name to itself to bump up the length
    while len(container_name) < 3:
        logging.warning(f'{object_type.capitalize()} name {container_name} was too short (only {len(container_name)} '
                        f'characters). Using {container_name + container_name} instead')
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
    container_client = blob_service_client.create_container(container_name)
    return container_client


def create_container_client(blob_service_client, container_name):
    """
    Create a container-specific client from the blob service client
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :return: container_client: type azure.storage.blob.BlobServiceClient.ContainerClient
    """
    # Create the container client from the blob service client with the get container client method
    # and the container name
    container_client = blob_service_client.get_container_client(container_name)
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


def write_sas(verbosity, output_file, sas_urls):
    """
    Write the SAS URLs to the output file
    :param verbosity: type str: Desired logging level
    :param output_file: type str: Name and path of the file in which the SAS URLs are to be written
    :param sas_urls: type dict: Dictionary of file name: SAS URL
    """
    # Return to the requested logging level, as it has been increased to WARNING to suppress the log being
    # filled with information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=verbosity.upper())
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
    # Extract the connection string from the system keyring
    connect_str = extract_connection_string(passphrase=passphrase,
                                            account_name=account_name)
    blob_service_client = create_blob_service_client(connect_str=connect_str)
    source_container_client = create_container_client(blob_service_client=blob_service_client,
                                                      container_name=container_name)
    # Hide the INFO-level messages sent to the logger from Azure by increasing the logging level to WARNING
    logging.getLogger().setLevel(logging.WARNING)
    try:
        target_container_client = create_container(blob_service_client=blob_service_client,
                                                   container_name=target_container)
    except azure.core.exceptions.ResourceExistsError:
        target_container_client = create_container_client(blob_service_client=blob_service_client,
                                                          container_name=target_container)
    return blob_service_client, source_container_client, target_container_client


def copy_blob(blob_file, blob_service_client, container_name, target_container, path, object_name=None, category=None):
    """
    Copy a blob from one container to another
    :param blob_file: type iterable from azure.storage.blob.BlobServiceClient.ContainerClient.list_blobs
    :param container_name: type str: Name of the container in which the file is located
    :param blob_service_client: type: azure.storage.blob.BlobServiceClient
    :param target_container: type str: Name of the new container into which the file is to be copied
    :param path: type str: Path of folders in which the files are to be placed
    :param object_name: type str: Name and path of file/folder to download from Azure storage
    :param category: type str: Category of object to be copied. Limited to file or folder
    """
    # Create the blob client
    blob_client = create_blob_client(blob_service_client=blob_service_client,
                                     container_name=container_name,
                                     blob_file=blob_file)
    # Extract the folder structure of the blob e.g. 220202-m05722/InterOp
    folder_structure = list(os.path.split(os.path.dirname(blob_file.name)))
    # Add the nested folder to the path as requested
    if path is None:
        # Determine the path to output the file. Join the name of the container and the joined (splatted)
        # folder structure. Logic: https://stackoverflow.com/a/14826889
        target_path = os.path.join(os.path.join(*folder_structure))
    else:
        target_path = path
    # Set the name of file by removing any path information
    file_name = os.path.basename(blob_file.name)
    # Finally, set the name and the path of the output file
    if category is None:
        target_file = os.path.join(target_path, file_name)
    # If a folder is being moved, extract the common path between the blob file and the supplied folder name. Find the
    # relative path between the blob file and the common path. Uses logic from https://stackoverflow.com/a/7288019
    else:
        target_file = os.path.join(target_path,
                                   os.path.relpath(blob_file.name,
                                                   os.path.commonpath([blob_file.name, object_name])))
    # Create a blob client for the target blob
    target_blob_client = blob_service_client.get_blob_client(target_container,
                                                             target_file)
    # Copy the source file to the target file - allow up to 1000 seconds total
    target_blob_client.start_copy_from_url(blob_client.url)
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

    test_containers = blob_service_client.list_containers(name_starts_with=container_name)
    if not test_containers:
        logging.error(f'Could not locate container {container_name} in {account_name}. Please ensure that you '
                      f'correctly entered all the information.')
        raise SystemExit
    # Delete container if it exists
    try:
        blob_service_client.delete_container(container_name)
    except azure.core.exceptions.ResourceNotFoundError:
        logging.error(f'Could not locate {container_name} in {account_name}. Perhaps it has already been deleted?')
        raise SystemExit


def delete_file(container_client, object_name, blob_service_client, container_name, account_name):
    """
    Delete a file from Azure storage
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
    try:
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
    except azure.core.exceptions.HttpResponseError:
        logging.error(f'There was an error deleting file {object_name} in container {container_name} '
                      f'in Azure storage account {account_name}. Please ensure that all arguments have been '
                      f'entered correctly')
        raise SystemExit
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
    try:
        for blob_file in generator:
            # Create the path of the file by extracting the path of the file
            blob_path = os.path.join(os.path.split(blob_file.name)[0])
            # Ensure that the supplied folder path is present in the blob path
            if os.path.normpath(object_name) in os.path.normpath(blob_path):
                # Update the folder presence boolean
                present = True
                # Create the blob client
                blob_client = create_blob_client(blob_service_client=blob_service_client,
                                                 container_name=container_name,
                                                 blob_file=blob_file)
                # Soft delete the blob
                blob_client.delete_blob()
    except azure.core.exceptions.HttpResponseError:
        logging.error(f'There was an error deleting folder {object_name} in container {container_name} '
                      f'in Azure storage account {account_name}. Please ensure that all arguments have been '
                      f'entered correctly')
        raise SystemExit
    # Send a warning to the user that the blob could not be found
    if not present:
        logging.error(
            f'There was an error deleting folder {object_name} in container {container_name}, '
            f'in Azure storage account {account_name}. Please ensure that all arguments have been '
            f'entered correctly')
        raise SystemExit
