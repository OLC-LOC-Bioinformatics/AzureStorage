#!/usr/bin/env python
import coloredlogs
import datetime
import logging
# Communication string storing imports
import getpass
import keyring
import os

# Azure-related imports
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas


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
    # Set the password in the keyring. Use the passphrase as the service ID, the account name as the username,
    # and the connection string as the password
    keyring.set_password(passphrase, account_name, connect_str)
    logging.info('Successfully entered credentials into keyring')
    return connect_str


def extract_connection_string(passphrase, account_name):
    """
    Extract the connection string from the keyring using the account name and passphrase
    :param passphrase: type str: Simple passphrase to use to store the connection string in the system keyring
    :param account_name: type str: Name of the Azure storage account
    connect_str: String of the connection string
    """
    # Use the passphrase and the account name to extract the connection string from the keyring
    connect_str = keyring.get_password(passphrase,
                                       account_name)
    # If the connection string can't be found in the keyring using the supplied passphrase, prompt the user for
    # the passphrase, and store it
    if not connect_str:
        logging.warning(f'Connection string linked to the provided passphrase: {passphrase} and account name: '
                        f'{account_name} not found in the system keyring. You will now be prompted to enter it.')
        connect_str = set_connection_string(passphrase=passphrase,
                                            account_name=account_name)
    return connect_str


def extract_account_key(connect_str):
    """
    Extract the account key from the connection string. This is necessary for the method that creates the blob SAS,
    as it doesn't accept connection strings
    :param connect_str: type str: Connection string for the Azure storage account
    :return account_key: String of the account key extracted from the connection string
    """
    # Split the connection string on ';', use the entry corresponding to the account key, and strip off the
    # 'AccountKey='
    # DefaultEndpointsProtocol=https;AccountName=carlingst01;AccountKey=[REDACTED];EndpointSuffix=core.windows.net
    account_key = connect_str.split(';')[2].split('AccountKey=')[-1]
    return account_key


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


def create_blob_service_client(connect_str):
    """
    Create a blob service client using the connection string
    :param connect_str: type str: Connection string for Azure storage
    :return: blob_service_client: type BlobServiceClient
    """
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    return blob_service_client


def create_container(blob_service_client, container_name):
    """
    Create a new container and container-specific client from the blob service client
    :param blob_service_client: type: BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :return: container_client: type BlobServiceClient.ContainerClient
    """
    container_client = blob_service_client.create_container(container_name)
    return container_client


def create_container_client(blob_service_client, container_name):
    """
    Create a container-specific client from the blob service client
    :param blob_service_client: type: BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :return: container_client: type BlobServiceClient.ContainerClient
    """
    # Create the container client from the blob service client with the get container client method
    # and the container name
    container_client = blob_service_client.get_container_client(container_name)
    return container_client


def create_blob_client(blob_service_client, container_name, blob_file):
    """
    Create a blob-specific client
    :param blob_service_client: type: BlobServiceClient
    :param container_name: type str: Name of the container of interest
    :param blob_file: type iterable from BlobServiceClient.ContainerClient.list_blobs
    :return: blob_client: type BlobServiceClient.BlobClient
    """
    # Create a blob client for the current blob
    blob_client = blob_service_client.get_blob_client(container=container_name,
                                                      blob=blob_file)
    return blob_client


def creat_blob_sas(blob_file, account_name, container_name, account_key, expiry, sas_urls):
    """

    :param blob_file:
    :param account_name:
    :param container_name:
    :param account_key:
    :param expiry:
    :param sas_urls:
    :return:
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
    # Generate the SAS URL using the account name, the domain, the container name, the blob name, and the
    # SAS token in the following format:
    # 'https://' + account_name + '.blob.core.windows.net/' + container_name + '/' + blob_name + '?' + blob
    sas_urls[file_name] = \
        f'https://{account_name}.blob.core.windows.net/{container_name}/' \
        f'{blob_file.name}?{sas_token}'
    return sas_urls


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
