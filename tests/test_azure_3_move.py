from azure_storage.methods import extract_account_name, move_prep
from azure_storage.azure_move import AzureContainerMove, AzureMove, cli, container_move, file_move, folder_move
from unittest.mock import patch
import argparse
import pytest
import azure
import os


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            # Extract the account name and connection string from the system keyring prior to running tests
            self.passphrase = 'AzureStorage'
            self.account_name = extract_account_name(passphrase=self.passphrase)
            self.container_name = '00000container'
            self.target_container = '000000container'

    return Variables()


def test_move_prep(variables):
    variables.container_name, variables.target_container, variables.blob_service_client, \
        variables.source_container_client, variables.target_container_client = move_prep(
            passphrase=variables.passphrase,
            account_name=variables.account_name,
            container_name=variables.container_name,
            target_container=variables.target_container)
    assert type(variables.source_container_client) is azure.storage.blob._container_client.ContainerClient


@pytest.mark.parametrize('file_name,path',
                         [('file_1.txt', ''),
                          ('file_2.txt', 'nested'),
                          ('nested_folder/folder_test_1.txt', ''),
                          ('nested_folder/nested_folder_2/nested_folder_test_1.txt', 'ABC'),
                          ('nested_folder/nested_folder_2/nested_folder_test_1.txt', 'ABC/123'),
                          ('nested/file_2.txt', 'nested_folder_2')])
def test_move_file(variables, file_name, path):
    AzureMove.move_file(source_container_client=variables.source_container_client,
                        object_name=file_name,
                        blob_service_client=variables.blob_service_client,
                        container_name=variables.container_name,
                        target_container=variables.target_container,
                        path=path)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, os.path.basename(file_name)) in [blob.name for blob in blobs]


@pytest.mark.parametrize('file_name,path',
                         [('file_7.txt', ''),
                          ('nonexistent/file_2.txt', 'nested_2'),
                          ('nested/file_3.txt', 'nested_folder_2')])
def test_move_file_invalid(variables, file_name, path):
    with pytest.raises(SystemExit):
        AzureMove.move_file(source_container_client=variables.source_container_client,
                            object_name=file_name,
                            blob_service_client=variables.blob_service_client,
                            container_name=variables.container_name,
                            target_container=variables.target_container,
                            path=path)


@pytest.mark.parametrize('folder_name,path,check_file',
                         [('single_nested', '', 'triple_nested_file.txt'),
                          ('nested_folder/nested_folder_2', 'nested_folder_3', 'nested_folder_test_1.txt'),
                          ('nested_folder/nested_folder_2', '', 'nested_folder_test_1.txt')])
def test_move_folder(variables, folder_name, path, check_file):
    AzureMove.move_folder(source_container_client=variables.source_container_client,
                          object_name=folder_name,
                          blob_service_client=variables.blob_service_client,
                          container_name=variables.container_name,
                          target_container=variables.target_container,
                          path=path,
                          category='folder')
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, os.path.basename(check_file)) in [blob.name for blob in blobs]


@pytest.mark.parametrize('folder_name,path',
                         [('nested_folder_6', ''),
                          ('nested_folder_2/nested_folder_2', 'nested_folder'),
                          ('nested_folder/nested_folder_3', '')])
def test_move_folder_invalid(variables, folder_name, path):
    with pytest.raises(SystemExit):
        AzureMove.move_folder(source_container_client=variables.source_container_client,
                              object_name=folder_name,
                              blob_service_client=variables.blob_service_client,
                              container_name=variables.container_name,
                              target_container=variables.target_container,
                              path=path,
                              category='folder')


def test_move_container(variables):
    path = 'nested_container'
    AzureContainerMove.move_container(source_container_client=variables.source_container_client,
                                      blob_service_client=variables.blob_service_client,
                                      container_name=variables.container_name,
                                      target_container=variables.target_container,
                                      path=path)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, 'file_2.txt') in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_move_file_integration(mock_args, variables):
    file_name = 'file_1.txt'
    reset_path = 'file_integration'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                target_container=variables.target_container,
                                                reset_path=reset_path,
                                                verbosity='info',
                                                file=file_name)
    arguments = cli()
    file_move(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, file_name) in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_move_folder_integration(mock_args, variables):
    folder_name = 'nested_folder_5'
    reset_path = 'folder_integration'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                target_container=variables.target_container,
                                                reset_path=reset_path,
                                                verbosity='info',
                                                folder=folder_name)
    arguments = cli()
    folder_move(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, 'nested_folder_test_1.txt') in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_move_container_integration(mock_args, variables):
    reset_path = 'container_integration'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                target_container=variables.target_container,
                                                reset_path=reset_path,
                                                verbosity='info')
    arguments = cli()
    container_move(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, 'nested_file_1.txt') in [blob.name for blob in blobs]
