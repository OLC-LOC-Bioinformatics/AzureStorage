#!/usr/bin/env python
import coloredlogs
import logging
# Communication string storing imports
import getpass
import keyring

# Azure-related imports
from azure.storage.blob import BlobServiceClient
import azure


def setup_logging(arguments):
    # Set up logging
    coloredlogs.DEFAULT_LEVEL_STYLES = {'debug': {'bold': True, 'color': 'green'},
                                        'info': {'bold': True, 'color': 'blue'},
                                        'warning': {'bold': True, 'color': 'yellow'},
                                        'error': {'bold': True, 'color': 'red'},
                                        'critical': {'bold': True, 'background': 'red'}
                                        }
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
    coloredlogs.install(level=arguments.verbosity.upper())


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
