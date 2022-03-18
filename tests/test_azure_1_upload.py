from azure_storage.methods import confirm_account_match, create_blob_service_client, create_container_client, \
    create_container, extract_account_name, extract_connection_string, \
    validate_container_name
from azure_storage.azure_upload import AzureUpload, cli, file_upload, folder_upload
from unittest.mock import patch
import argparse
import pytest
import random
import string
import azure
import os

letters = string.ascii_lowercase
long_container = ''.join(random.choice(letters) for i in range(65))


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            # Extract the account name and connection string from the system keyring prior to running tests
            self.passphrase = 'AzureStorage'
            self.account_name = extract_account_name(passphrase=self.passphrase)
            self.connection_string = extract_connection_string(passphrase=self.passphrase,
                                                               account_name=self.account_name)
            self.container_name = '00000container'
            self.test_path = os.path.abspath(os.path.dirname(__file__))
            self.file_path = os.path.join(self.test_path, 'files')
            self.storage_tier = 'Hot'

    return Variables()


def test_account_name(variables):
    assert variables.account_name


def test_connection_string(variables):
    assert variables.connection_string.startswith('DefaultEndpointsProtocol')


def test_account_match(variables):
    assert confirm_account_match(account_name=variables.account_name,
                                 connect_str=variables.connection_string)


@pytest.mark.parametrize('test_input,expected',
                         [('12345', '12345'),
                          ('123___45', '123-45'),
                          ('--12345---', '12345'),
                          ('0', '0000'),
                          ('ABCD', 'abcd'),
                          ('Abc123-', 'abc123'),
                          ('@#2$5@7#', '257'),
                          (long_container, long_container[:62])])
def test_validate_container_name(test_input, expected):
    assert validate_container_name(container_name=test_input) == expected


@pytest.mark.parametrize('test_input', ['---',
                                        '@#$@#'
                                        ''])
def test_validate_container_name_fail(test_input):
    with pytest.raises(SystemExit):
        validate_container_name(container_name=test_input)


def test_create_blob_service_client_invalid_connection_str():
    with pytest.raises(SystemExit):
        create_blob_service_client(connect_str='invalid_connection_string')


def test_create_blob_service_client_valid(variables):
    variables.blob_service_client = create_blob_service_client(connect_str=variables.connection_string)
    assert type(variables.blob_service_client) == azure.storage.blob._blob_service_client.BlobServiceClient


def test_missing_container(variables):
    containers = variables.blob_service_client.list_containers(include_metadata=True)
    assert variables.container_name not in [container['name'] for container in containers]


def test_upload_file_nonexistent_container(variables):
    with pytest.raises(SystemExit):
        AzureUpload.upload_file(object_name=os.path.join(variables.file_path, 'file_1.txt'),
                                blob_service_client=variables.blob_service_client,
                                container_name=variables.container_name,
                                account_name=variables.account_name,
                                path=None,
                                storage_tier=variables.storage_tier)


def test_create_container(variables):
    variables.container_client = create_container(blob_service_client=variables.blob_service_client,
                                                  container_name=variables.container_name)


def test_container_presence(variables):
    containers = variables.blob_service_client.list_containers()
    assert variables.container_name in [container['name'] for container in containers]


@pytest.mark.parametrize('file_name,path',
                         [('file_1.txt', ''),
                          ('file_2.txt', 'nested'),
                          ('folder/nested_file_1.txt', ''),
                          ('folder/nested_file_2.txt', 'nested_folder')])
def test_upload_file(variables, file_name, path):
    AzureUpload.upload_file(object_name=os.path.join(variables.file_path, file_name),
                            blob_service_client=variables.blob_service_client,
                            container_name=variables.container_name,
                            account_name=variables.account_name,
                            path=path,
                            storage_tier=variables.storage_tier)
    blobs = variables.container_client.list_blobs()
    assert os.path.join(path, os.path.basename(file_name)) in [blob.name for blob in blobs]


@pytest.mark.parametrize('file_name,path',
                         [('file_1.txt', ''),
                          ('file_2.txt', 'nested'),
                          ('folder/nested_file_1.txt', ''),
                          ('folder/nested_file_2.txt', 'nested_folder')])
def test_upload_file_exists(variables, file_name, path):
    with pytest.raises(SystemExit):
        AzureUpload.upload_file(object_name=os.path.join(variables.file_path, file_name),
                                blob_service_client=variables.blob_service_client,
                                container_name=variables.container_name,
                                account_name=variables.account_name,
                                path=path,
                                storage_tier=variables.storage_tier)


def test_upload_file_nonexistent(variables):
    with pytest.raises(SystemExit):
        AzureUpload.upload_file(object_name=os.path.join(variables.file_path, 'file_3.txt'),
                                blob_service_client=variables.blob_service_client,
                                container_name=variables.container_name,
                                account_name=variables.account_name,
                                path='',
                                storage_tier=variables.storage_tier)


def test_upload_file_none_path(variables):
    file_name = os.path.join(variables.file_path, 'folder/nested_file_2.txt')
    AzureUpload.upload_file(object_name=file_name,
                            blob_service_client=variables.blob_service_client,
                            container_name=variables.container_name,
                            account_name=variables.account_name,
                            path=None,
                            storage_tier=variables.storage_tier)
    blobs = variables.container_client.list_blobs()
    assert os.path.basename(file_name) in [blob.name for blob in blobs]


@pytest.mark.parametrize('file_name,path',
                         [('file_1.txt', 'cool'),
                          ('file_1', ''),
                          ('file_1.gz', ''),
                          ('file_2.txt', 'cool/nested'),
                          ('folder/nested/double_nested_file_1.txt', ''),
                          ('folder/nested/double_nested/triple_nested_file.txt', 'cool/nested')])
def test_upload_file_cool(variables, file_name, path):
    storage_tier = 'Cool'
    AzureUpload.upload_file(object_name=os.path.join(variables.file_path, file_name),
                            blob_service_client=variables.blob_service_client,
                            container_name=variables.container_name,
                            account_name=variables.account_name,
                            path=path,
                            storage_tier=storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(path, file_name):
            assert blob.blob_tier == storage_tier


def test_upload_file_invalid_category(variables):
    with pytest.raises(SystemExit):
        file_uploader = AzureUpload(object_name=os.path.join(variables.file_path, 'file_1.txt'),
                                    account_name=variables.account_name,
                                    container_name=variables.container_name,
                                    passphrase=variables.passphrase,
                                    path='cool',
                                    storage_tier=variables.storage_tier,
                                    category='container')
        file_uploader.main()


@patch('argparse.ArgumentParser.parse_args')
def test_upload_file_integration(mock_args, variables):
    file_name = 'file_2.txt'
    path = str()
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                file=os.path.join(variables.file_path, file_name),
                                                reset_path=path,
                                                storage_tier=variables.storage_tier)
    arguments = cli()
    file_upload(args=arguments)
    blobs = variables.container_client.list_blobs()
    assert os.path.join(path, os.path.basename(file_name)) in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_upload_file_integration_invalid_file(mock_args, variables):
    with pytest.raises(SystemExit):
        file_name = 'file_5.txt'
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name=variables.container_name,
                                                    verbosity='info',
                                                    file=os.path.join(variables.file_path, file_name),
                                                    reset_path='',
                                                    storage_tier=variables.storage_tier)
        arguments = cli()
        file_upload(args=arguments)


@pytest.mark.parametrize('folder_name,path,check_file',
                         [('folder_2', '', 'folder_test_1.txt'),
                          ('folder_2', 'nested_folder', 'folder_test_1.txt'),
                          ('folder_2/nested_folder_2', '', 'nested_folder_test_1.txt'),
                          ('folder_2/nested_folder_2', 'nested_folder_5', 'nested_folder_test_1.txt')])
def test_upload_folder(variables, folder_name, path, check_file):
    AzureUpload.upload_folder(object_name=os.path.join(variables.file_path, folder_name),
                              blob_service_client=variables.blob_service_client,
                              container_name=variables.container_name,
                              account_name=variables.account_name,
                              path=path,
                              storage_tier=variables.storage_tier)
    blobs = variables.container_client.list_blobs()
    assert os.path.join(path, os.path.basename(check_file)) in [blob.name for blob in blobs]


@pytest.mark.parametrize('folder_name,path,check_file',
                         [('folder_2', 'cool', 'folder_test_1.txt'),
                          ('folder/nested/double_nested', '', 'double_nested_file_2'),
                          ('folder_2/nested_folder_2', 'cool/nested', 'nested_folder_test_1.txt'),
                          ('folder_2/nested_folder_2', 'cool_nested_folder_5', 'nested_folder_test_1.txt')])
def test_upload_folder_cool(variables, folder_name, path, check_file):
    storage_tier = 'Cool'
    AzureUpload.upload_folder(object_name=os.path.join(variables.file_path, folder_name),
                              blob_service_client=variables.blob_service_client,
                              container_name=variables.container_name,
                              account_name=variables.account_name,
                              path=path,
                              storage_tier=storage_tier)
    blobs = variables.container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(path, check_file):
            assert blob.blob_tier == storage_tier


@pytest.mark.parametrize('folder_name,check_file',
                         [('folder_2/nested_folder_2', 'nested_folder_test_1.txt'),
                          ('folder_2/nested_folder_2', 'nested_folder_test_1.txt')])
def test_upload_folder_none_path(variables, folder_name, check_file):
    AzureUpload.upload_folder(object_name=os.path.join(variables.file_path, folder_name),
                              blob_service_client=variables.blob_service_client,
                              container_name=variables.container_name,
                              account_name=variables.account_name,
                              path=None,
                              storage_tier=variables.storage_tier)
    blobs = variables.container_client.list_blobs()
    assert check_file in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_upload_folder_integration(mock_args, variables):
    folder_name = 'folder/nested/double_nested'
    path = 'single_nested'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                folder=os.path.join(variables.file_path, folder_name),
                                                reset_path=path,
                                                storage_tier=variables.storage_tier)
    arguments = cli()
    folder_upload(args=arguments)
    blobs = variables.container_client.list_blobs()
    assert os.path.join(path, 'triple_nested_file.txt') in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_upload_folder_integration_invalid(mock_args, variables):
    with pytest.raises(SystemExit):
        folder_name = 'folder/nested/double_nested/triple_nested'
        path = 'triple_nested'
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name=variables.container_name,
                                                    verbosity='info',
                                                    folder=os.path.join(variables.file_path, folder_name),
                                                    reset_path=path,
                                                    storage_tier=variables.storage_tier)
        arguments = cli()
        folder_upload(args=arguments)
