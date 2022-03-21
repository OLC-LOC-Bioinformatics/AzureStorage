from azure_storage.methods import client_prep, delete_container, delete_file, delete_folder, extract_account_name
from azure_storage.azure_delete import AzureDelete, cli, container_delete, file_delete, \
    folder_delete
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
            self.container_name = '000000container'
            self.account_name = extract_account_name(passphrase=self.passphrase)

    return Variables()


def test_client_prep(variables):
    variables.container_name, variables.connect_str, variables.blob_service_client, variables.container_client = \
        client_prep(container_name=variables.container_name,
                    passphrase=variables.passphrase,
                    account_name=variables.account_name)
    assert variables.connect_str.startswith('DefaultEndpointsProtocol')


@pytest.mark.parametrize('file_name',
                         ['file_1.txt',
                          'container_integration/file_2.txt',
                          'nested_container/nested_folder/nested_folder_2/nested_folder_test_1.txt',
                          'ABC/123/nested_folder_test_1.txt'])
def test_delete_file(variables, file_name):
    delete_file(container_client=variables.container_client,
                object_name=file_name,
                blob_service_client=variables.blob_service_client,
                container_name=variables.container_name)
    blobs = variables.container_client.list_blobs()
    assert file_name not in [blob.name for blob in blobs]


@pytest.mark.parametrize('file_name',
                         ['file_3.txt',
                          'container_integration/file_2.txt',
                          'nested_container/nested_folder/nested_folder_2/nested_folder_test_1.txt',
                          'ABC/123/nested_folder_test_1.txt'])
def test_delete_file_missing(variables, file_name):
    with pytest.raises(SystemExit):
        delete_file(container_client=variables.container_client,
                    object_name=file_name,
                    blob_service_client=variables.blob_service_client,
                    container_name=variables.container_name)


def test_delete_file_invalid_category(variables):
    with pytest.raises(SystemExit):
        del_file = AzureDelete(object_name='file_1.txt',
                               container_name=variables.container_name,
                               account_name=variables.account_name,
                               passphrase=variables.passphrase,
                               retention_time=8,
                               category='container')
        del_file.main()


@patch('argparse.ArgumentParser.parse_args')
def test_delete_file_integration(mock_args, variables):
    file_name = 'nested/file_2.txt'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                file=file_name,
                                                retention_time=1)
    arguments = cli()
    file_delete(arguments)
    blobs = variables.container_client.list_blobs()
    assert os.path.basename(file_name) not in [blob.name for blob in blobs]


@pytest.mark.parametrize('retention_time',
                         [0,
                          1000])
@patch('argparse.ArgumentParser.parse_args')
def test_delete_file_integration_invalid_retention_time(mock_args, variables, retention_time):
    file_name = 'nested/file_2.txt'
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name=variables.container_name,
                                                    verbosity='info',
                                                    file=file_name,
                                                    retention_time=retention_time)
        arguments = cli()
        file_delete(arguments)


@patch('argparse.ArgumentParser.parse_args')
def test_delete_file_integration_missing(mock_args, variables):
    file_name = 'nested/file_2.txt'
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name=variables.container_name,
                                                    verbosity='info',
                                                    file=file_name,
                                                    retention_time=1)
        arguments = cli()
        file_delete(arguments)


@pytest.mark.parametrize('folder_name,check_file',
                         [('container_integration/', 'nested_folder_test_1.txt'),
                          ('nested_container/nested_folder/', 'nested_file_2.txt'),
                          ('ABC/', 'nested_folder_test_1.txt')])
def test_delete_folder(variables, folder_name, check_file):
    delete_folder(container_client=variables.container_client,
                  object_name=folder_name,
                  blob_service_client=variables.blob_service_client,
                  container_name=variables.container_name,
                  account_name=variables.account_name)
    blobs = variables.container_client.list_blobs()
    assert os.path.join(folder_name, check_file) not in [blob.name for blob in blobs]


@pytest.mark.parametrize('folder_name,check_file',
                         [('container_integration/', 'nested_folder_test_1.txt'),
                          ('nested_container/nested_folder/', 'nested_file_2.txt'),
                          ('ABC/', 'nested_folder_test_1.txt')])
def test_delete_folder_missing(variables, folder_name, check_file):
    with pytest.raises(SystemExit):
        delete_folder(container_client=variables.container_client,
                      object_name=folder_name,
                      blob_service_client=variables.blob_service_client,
                      container_name=variables.container_name,
                      account_name=variables.account_name)


@patch('argparse.ArgumentParser.parse_args')
def test_delete_folder_integration(mock_args, variables):
    folder_name = 'nested_folder_3'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                folder=folder_name,
                                                retention_time=1)
    arguments = cli()
    folder_delete(arguments)
    blobs = variables.container_client.list_blobs()
    assert os.path.join(folder_name, 'nested_folder_test_1.txt') not in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_delete_folder_integration_missing(mock_args, variables):
    folder_name = 'nested_folder_3'
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name=variables.container_name,
                                                    verbosity='info',
                                                    folder=folder_name,
                                                    retention_time=1)
        arguments = cli()
        folder_delete(arguments)


def test_delete_container_missing(variables):
    with pytest.raises(SystemExit):
        delete_container(blob_service_client=variables.blob_service_client,
                         container_name='000000000container',
                         account_name=variables.account_name)


@patch('argparse.ArgumentParser.parse_args')
def test_delete_container_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info')
    arguments = cli()
    container_delete(arguments)
    with pytest.raises(azure.core.exceptions.ResourceExistsError):
        variables.blob_service_client.create_container(variables.container_name)
