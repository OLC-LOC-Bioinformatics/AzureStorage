from azure_storage.methods import client_prep, extract_account_name
from azure_storage.azure_tier import AzureContainerTier, AzureTier, cli, container_tier, file_tier, folder_tier
from unittest.mock import patch
import argparse
import pytest
import azure
import os


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            self.passphrase = 'AzureStorage'
            self.account_name = extract_account_name(passphrase=self.passphrase)
            self.container_name = '000000container'
            self.storage_tier = 'Cool'

    return Variables()


def test_tier_client_prep(variables):
    variables.container_name, variables.connect_str, variables.blob_service_client, variables.container_client = \
        client_prep(container_name=variables.container_name,
                    passphrase=variables.passphrase,
                    account_name=variables.account_name)
    assert type(variables.blob_service_client) == azure.storage.blob._blob_service_client.BlobServiceClient


@pytest.mark.parametrize('file_name',
                         ['file_1.txt',
                          'file_1.txt',
                          'container_integration/file_2.txt',
                          'nested_container/nested_folder/nested_folder_2/nested_folder_test_1.txt',
                          'ABC/123/nested_folder_test_1.txt'])
def test_file_tier_cool(variables, file_name):
    AzureTier.file_tier(container_client=variables.container_client,
                        object_name=file_name,
                        blob_service_client=variables.blob_service_client,
                        container_name=variables.container_name,
                        storage_tier=variables.storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == file_name:
            assert blob.blob_tier == variables.storage_tier


@pytest.mark.parametrize('file_name',
                         ['file_1.txt',
                          'file_1.txt',
                          'container_integration/file_2.txt',
                          'nested_container/nested_folder/nested_folder_2/nested_folder_test_1.txt',
                          'ABC/123/nested_folder_test_1.txt'])
def test_file_tier_hot(variables, file_name):
    storage_tier = 'Hot'
    AzureTier.file_tier(container_client=variables.container_client,
                        object_name=file_name,
                        blob_service_client=variables.blob_service_client,
                        container_name=variables.container_name,
                        storage_tier=storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == file_name:
            assert blob.blob_tier == storage_tier


@pytest.mark.parametrize('file_name',
                         ['file_3.txt',
                          'container_integration_2/file_2.txt',
                          'nested_container/nested_folder/nested_folder_2/nested_folder_test_14.txt',
                          'ABC/321/nested_folder_test_1.txt'])
def test_file_tier_missing(variables, file_name):
    with pytest.raises(SystemExit):
        AzureTier.file_tier(container_client=variables.container_client,
                            object_name=file_name,
                            blob_service_client=variables.blob_service_client,
                            container_name=variables.container_name,
                            storage_tier=variables.storage_tier)


def test_file_tier_invalid_category(variables):
    with pytest.raises(SystemExit):
        file_tier_set = AzureTier(container_name=variables.container_name,
                                  object_name='file_1.txt',
                                  account_name=variables.account_name,
                                  passphrase=variables.passphrase,
                                  storage_tier=variables.storage_tier,
                                  category='container')
        file_tier_set.main()


def test_file_tier_invalid_container(variables):
    with pytest.raises(SystemExit):
        file_tier_set = AzureTier(container_name='000000000container',
                                  object_name='file_1.txt',
                                  account_name=variables.account_name,
                                  passphrase=variables.passphrase,
                                  storage_tier=variables.storage_tier,
                                  category='file')
        file_tier_set.main()


@patch('argparse.ArgumentParser.parse_args')
def test_file_tier_integration(mock_args, variables):
    file_name = 'container_integration/file_2.txt'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                file=file_name,
                                                storage_tier=variables.storage_tier)
    arguments = cli()
    file_tier(arguments)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == file_name:
            assert blob.blob_tier == variables.storage_tier


@pytest.mark.parametrize('folder_name,check_file',
                         [('container_integration/', 'nested_folder_test_1.txt'),
                          ('container_integration/', 'nested_folder_test_1.txt'),
                          ('nested_container/nested_folder', 'nested_file_2.txt'),
                          ('ABC/', 'nested_folder_test_1.txt')])
def test_folder_tier_cool(variables, folder_name, check_file):
    AzureTier.folder_tier(container_client=variables.container_client,
                          object_name=folder_name,
                          blob_service_client=variables.blob_service_client,
                          container_name=variables.container_name,
                          storage_tier=variables.storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(folder_name, check_file):
            assert blob.blob_tier == variables.storage_tier


@pytest.mark.parametrize('folder_name,check_file',
                         [('container_integration/', 'nested_folder_test_1.txt'),
                          ('container_integration/', 'nested_folder_test_1.txt'),
                          ('nested_container/nested_folder/', 'nested_file_2.txt'),
                          ('ABC/', 'nested_folder_test_1.txt')])
def test_folder_tier_hot(variables, folder_name, check_file):
    storage_tier = 'Hot'
    AzureTier.folder_tier(container_client=variables.container_client,
                          object_name=folder_name,
                          blob_service_client=variables.blob_service_client,
                          container_name=variables.container_name,
                          storage_tier=storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(folder_name, check_file):
            assert blob.blob_tier == storage_tier


@pytest.mark.parametrize('folder_name',
                         ['container_integration_4/',
                          'nested_container_13/nested_folder/',
                          '123/ABC/'])
def test_folder_tier_missing(variables, folder_name):
    with pytest.raises(SystemExit):
        AzureTier.folder_tier(container_client=variables.container_client,
                              object_name=folder_name,
                              blob_service_client=variables.blob_service_client,
                              container_name=variables.container_name,
                              storage_tier=variables.storage_tier)


def test_folder_tier_invalid_container(variables):
    with pytest.raises(SystemExit):
        file_tier_set = AzureTier(container_name='000000000container',
                                  object_name='container_integration',
                                  account_name=variables.account_name,
                                  passphrase=variables.passphrase,
                                  storage_tier=variables.storage_tier,
                                  category='folder')
        file_tier_set.main()


@patch('argparse.ArgumentParser.parse_args')
def test_folder_tier_integration_cool(mock_args, variables):
    folder_name = 'container_integration/'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                folder=folder_name,
                                                storage_tier=variables.storage_tier)
    arguments = cli()
    folder_tier(arguments)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(folder_name, 'nested_folder_test_1.txt'):
            assert blob.blob_tier == variables.storage_tier


@patch('argparse.ArgumentParser.parse_args')
def test_folder_tier_integration_hot(mock_args, variables):
    folder_name = 'container_integration/'
    storage_tier = 'Hot'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                folder=folder_name,
                                                storage_tier=storage_tier)
    arguments = cli()
    folder_tier(arguments)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(folder_name, 'nested_folder_test_1.txt'):
            assert blob.blob_tier == storage_tier


def test_container_tier_cool(variables):
    AzureContainerTier.container_tier(container_client=variables.container_client,
                                      blob_service_client=variables.blob_service_client,
                                      container_name=variables.container_name,
                                      storage_tier=variables.storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == 'file_1.txt':
            assert blob.blob_tier == variables.storage_tier


def test_container_tier_hot(variables):
    storage_tier = 'Hot'
    AzureContainerTier.container_tier(container_client=variables.container_client,
                                      blob_service_client=variables.blob_service_client,
                                      container_name=variables.container_name,
                                      storage_tier=storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == 'file_1.txt':
            assert blob.blob_tier == storage_tier


@patch('argparse.ArgumentParser.parse_args')
def test_container_tier_integration_cool(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                storage_tier=variables.storage_tier)
    arguments = cli()
    container_tier(arguments)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join('container_integration', 'nested_folder_test_1.txt'):
            assert blob.blob_tier == variables.storage_tier


@patch('argparse.ArgumentParser.parse_args')
def test_container_tier_integration_hot(mock_args, variables):
    storage_tier = 'Hot'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                storage_tier=storage_tier)
    arguments = cli()
    container_tier(arguments)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join('container_integration', 'nested_folder_test_1.txt'):
            assert blob.blob_tier == storage_tier


@patch('argparse.ArgumentParser.parse_args')
def test_container_tier_integration_missing(mock_args, variables):
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name='00000container',
                                                    verbosity='info',
                                                    storage_tier=variables.storage_tier)
        arguments = cli()
        container_tier(arguments)


def test_cli():
    os.system('AzureTier -h')
