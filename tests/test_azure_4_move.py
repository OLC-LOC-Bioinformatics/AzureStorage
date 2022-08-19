from azure_storage.methods import move_prep
from azure_storage.azure_move import \
    AzureContainerMove, \
    AzureMove, \
    cli, \
    container_move, \
    file_move, \
    folder_move
from unittest.mock import patch
import argparse
import pytest
import azure
import os


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            self.account_name = 'carlingst01'
            self.container_name = '00000container'
            self.target_container = '000000container'
            self.storage_tier = 'Hot'

    return Variables()


def run_move_prep(variables):
    variables.container_name, variables.target_container, variables.blob_service_client, \
        variables.source_container_client, variables.target_container_client = move_prep(
            account_name=variables.account_name,
            container_name=variables.container_name,
            target_container=variables.target_container
        )


def test_move_prep(variables):
    run_move_prep(variables=variables)
    assert type(variables.source_container_client) is azure.storage.blob._container_client.ContainerClient


def test_move_prep_target_exists(variables):
    run_move_prep(variables=variables)
    assert type(variables.target_container_client) is azure.storage.blob._container_client.ContainerClient


@pytest.mark.parametrize('file_name,path',
                         [('file_1.txt', ''),
                          ('file_1', ''),
                          ('file_1.gz', ''),
                          ('file_2.txt', 'nested'),
                          ('nested_folder/folder_test_1.txt', ''),
                          ('nested_folder/nested_folder_2/nested_folder_test_1.txt', 'ABC'),
                          ('nested_folder/nested_folder_2/nested_folder_test_1.txt', 'ABC/123'),
                          ('nested/file_2.txt', 'nested_folder_2')])
def test_move_file(variables, file_name, path):
    AzureMove.move_file(
        source_container_client=variables.source_container_client,
        object_name=file_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier
    )
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, os.path.basename(file_name)) in [blob.name for blob in blobs]


@pytest.mark.parametrize('file_name,path',
                         [('file_7.txt', ''),
                          ('nonexistent/file_2.txt', 'nested_2'),
                          ('nested/file_3.txt', 'nested_folder_2')])
def test_move_file_invalid(variables, file_name, path):
    with pytest.raises(SystemExit):
        AzureMove.move_file(
            source_container_client=variables.source_container_client,
            object_name=file_name,
            blob_service_client=variables.blob_service_client,
            container_name=variables.container_name,
            target_container=variables.target_container,
            path=path,
            storage_tier=variables.storage_tier
        )


@pytest.mark.parametrize('file_name,path',
                         [('nested_file_1.txt', ''),
                          ('nested_folder/nested_file_2.txt', 'nested')])
def test_move_file_cool(variables, file_name, path):
    storage_tier = 'Cool'
    AzureMove.move_file(
        source_container_client=variables.source_container_client,
        object_name=file_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=storage_tier
    )
    blobs = variables.target_container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(path, file_name):
            assert blob.blob_tier == storage_tier


@pytest.mark.parametrize('folder_name,path,check_file',
                         [('single_nested', '', 'triple_nested_file.txt'),
                          ('nested_folder/nested_folder_2', 'nested_folder_3', 'nested_folder_test_1.txt'),
                          ('nested_folder/nested_folder_2', '', 'nested_folder_test_1.txt')])
def test_move_folder(variables, folder_name, path, check_file):
    AzureMove.move_folder(
        source_container_client=variables.source_container_client,
        object_name=folder_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier,
        category='folder'
    )
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, os.path.basename(check_file)) in [blob.name for blob in blobs]


@pytest.mark.parametrize('folder_name,path,check_file',
                         [('cool/nested_folder_2', '', 'nested_folder_test_1.txt'),
                          ('cool_nested_folder_5', 'hot', 'nested_folder_test_1.txt')])
def test_move_folder_cool(variables, folder_name, path, check_file):
    AzureMove.move_folder(
        source_container_client=variables.source_container_client,
        object_name=folder_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier,
        category='folder'
    )
    blobs = variables.target_container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(path, check_file):
            assert blob.blob_tier == variables.storage_tier


@pytest.mark.parametrize('folder_name,path',
                         [('nested_folder_6', ''),
                          ('nested_folder_2/nested_folder_2', 'nested_folder'),
                          ('nested_folder/nested_folder_3', '')])
def test_move_folder_invalid(variables, folder_name, path):
    with pytest.raises(SystemExit):
        AzureMove.move_folder(
            source_container_client=variables.source_container_client,
            object_name=folder_name,
            blob_service_client=variables.blob_service_client,
            container_name=variables.container_name,
            target_container=variables.target_container,
            path=path,
            storage_tier=variables.storage_tier,
            category='folder'
        )


def test_move_folder_invalid_category(variables):
    with pytest.raises(SystemExit):
        move_folder = AzureMove(
            object_name='cool/nested_folder_2',
            container_name=variables.container_name,
            account_name=variables.account_name,
            target_container=variables.target_container,
            path=None,
            storage_tier=variables.storage_tier,
            category='container'
        )
        move_folder.main()


def test_move_container(variables):
    path = 'nested_container'
    AzureContainerMove.move_container(
        source_container_client=variables.source_container_client,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier
    )
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, 'file_2.txt') in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_move_file_integration(mock_args, variables):
    file_name = 'file_1.txt'
    reset_path = 'file_integration'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        file=file_name,
        storage_tier=variables.storage_tier
    )
    arguments = cli()
    file_move(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, file_name) in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_move_file_integration_cool(mock_args, variables):
    file_name = 'nested_file_1.txt'
    reset_path = 'cool_file_integration'
    storage_tier = 'Cool'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        file=file_name,
        storage_tier=storage_tier
    )
    arguments = cli()
    file_move(arguments)
    blobs = variables.target_container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(reset_path, file_name):
            assert blob.blob_tier == storage_tier


@patch('argparse.ArgumentParser.parse_args')
def test_move_folder_integration(mock_args, variables):
    folder_name = 'nested_folder_5'
    reset_path = 'folder_integration'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        folder=folder_name,
        storage_tier=variables.storage_tier
    )
    arguments = cli()
    folder_move(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, 'nested_folder_test_1.txt') in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_move_container_integration(mock_args, variables):
    reset_path = 'container_integration'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        storage_tier=variables.storage_tier)
    arguments = cli()
    container_move(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, 'double_nested_file_1.txt') in [blob.name for blob in blobs]
