from azure_storage.methods import \
    move_prep, \
    delete_container
from azure_storage.azure_move import \
    AzureContainerMove, \
    AzureMove
from azure_storage.azure_copy import \
    cli, \
    container_copy, \
    file_copy, \
    folder_copy
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
            self.target_container = '0000000000container'
            self.storage_tier = 'Hot'

    return Variables()


def run_copy_prep(variables):
    variables.container_name, variables.target_container, variables.blob_service_client, \
        variables.source_container_client, variables.target_container_client = move_prep(
            account_name=variables.account_name,
            container_name=variables.container_name,
            target_container=variables.target_container
        )


def test_copy_prep(variables):
    run_copy_prep(variables=variables)
    assert type(variables.source_container_client) is azure.storage.blob._container_client.ContainerClient


def test_copy_prep_target_exists(variables):
    run_copy_prep(variables=variables)
    assert type(variables.target_container_client) is azure.storage.blob._container_client.ContainerClient


@pytest.mark.parametrize('file_name,path,rename',
                         [('file_1.txt', '', 'file_1_copy.txt'),
                          ('file_1', '', 'file_1_copy'),
                          ('file_1.gz', '', 'file_1_copy.gz'),
                          ('file_2.txt', 'nested', 'file_2_copy.txt'),
                          ('nested_folder/folder_test_1.txt', 'folder_test_1_copy.txt', 'folder_test_1_copy.txt'),
                          ('nested_folder/nested_folder_2/nested_folder_test_1.txt', 'ABC',
                           'nested_folder_test_1_copy.txt'),
                          ('nested_folder/nested_folder_2/nested_folder_test_1.txt', 'ABC/123',
                           'nested_folder_test_1_copy.txt'),
                          ('nested/file_2.txt', 'nested_folder_2', 'file_2_copy.txt')])
def test_copy_file(variables, file_name, path, rename):
    AzureMove.move_file(
        source_container_client=variables.source_container_client,
        object_name=file_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier,
        rename=rename
    )
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, os.path.basename(rename)) in [blob.name for blob in blobs]


@pytest.mark.parametrize('file_name,path,rename',
                         [('file_7.txt', '', 'file_7_copy.txt'),
                          ('nonexistent/file_2.txt', 'nested_2', 'file_2_copy.txt'),
                          ('nested/file_3.txt', 'nested_folder_2', 'file_3_copy.txt')])
def test_copy_file_invalid(variables, file_name, path, rename):
    with pytest.raises(SystemExit):
        AzureMove.move_file(
            source_container_client=variables.source_container_client,
            object_name=file_name,
            blob_service_client=variables.blob_service_client,
            container_name=variables.container_name,
            target_container=variables.target_container,
            path=path,
            storage_tier=variables.storage_tier,
            rename=rename
        )


@pytest.mark.parametrize('file_name,path,rename',
                         [('nested_file_1.txt', '', 'nested_file_1_copy.txt'),
                          ('nested_folder/nested_file_2.txt', 'nested', 'nested_file_2_copy.txt')])
def test_copy_file_cool(variables, file_name, path, rename):
    storage_tier = 'Cool'
    AzureMove.move_file(
        source_container_client=variables.source_container_client,
        object_name=file_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=storage_tier,
        rename=rename
    )
    blobs = variables.target_container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(path, rename):
            assert blob.blob_tier == storage_tier


@pytest.mark.parametrize('folder_name,path,check_file',
                         [('single_nested', '', 'triple_nested_file.txt'),
                          ('nested_folder/nested_folder_2', 'nested_folder_3', 'nested_folder_test_1.txt'),
                          ('nested_folder/nested_folder_2', '', 'nested_folder_test_1.txt')])
def test_copy_folder(variables, folder_name, path, check_file):
    AzureMove.move_folder(
        source_container_client=variables.source_container_client,
        object_name=folder_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier,
        category='folder',
    )
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, os.path.basename(check_file)) in [blob.name for blob in blobs]
    original_blobs = variables.source_container_client.list_blobs()
    assert folder_name in [os.path.dirname(blob.name) for blob in original_blobs]


@pytest.mark.parametrize('folder_name,path,check_file',
                         [('cool/nested_folder_2', '', 'nested_folder_test_1.txt'),
                          ('cool_nested_folder_5', 'hot', 'nested_folder_test_1.txt')])
def test_copy_folder_cool(variables, folder_name, path, check_file):
    AzureMove.move_folder(
        source_container_client=variables.source_container_client,
        object_name=folder_name,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier,
        category='folder',
    )
    blobs = variables.target_container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(path, check_file):
            assert blob.blob_tier == variables.storage_tier
    original_blobs = variables.source_container_client.list_blobs()
    assert folder_name in [os.path.dirname(blob.name) for blob in original_blobs]


def test_copy_container(variables):
    path = 'nested_container'
    AzureContainerMove.move_container(
        source_container_client=variables.source_container_client,
        blob_service_client=variables.blob_service_client,
        container_name=variables.container_name,
        target_container=variables.target_container,
        path=path,
        storage_tier=variables.storage_tier,
    )
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(path, 'file_2.txt') in [blob.name for blob in blobs]
    original_blobs = variables.source_container_client.list_blobs()
    assert original_blobs


@patch('argparse.ArgumentParser.parse_args')
def test_copy_file_integration(mock_args, variables):
    file_name = 'file_1.txt'
    reset_path = 'file_integration'
    rename = 'file_1_copy.txt'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        file=file_name,
        storage_tier=variables.storage_tier,
        name=rename,
        copy=True,
    )
    arguments = cli()
    file_copy(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, rename) in [blob.name for blob in blobs]


@pytest.mark.parametrize('file_name,path,rename',
                         [('file_1.txt', '', ''),
                          ('nested_folder/folder_test_1.txt', 'nested_folder', 'folder_test_1.txt'),
                          ('nested_folder/folder_test_1.txt', 'nested_folder', ''),
                          ('file_1.txt', None, '')])
@patch('argparse.ArgumentParser.parse_args')
def test_copy_file_duplicate_integration(mock_args, variables, file_name, path, rename):
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(
            account_name=variables.account_name,
            container_name=variables.container_name,
            target_container=variables.container_name,
            reset_path=path,
            verbosity='info',
            file=file_name,
            storage_tier=variables.storage_tier,
            name=rename,
            copy=True,
        )
        arguments = cli()
        file_copy(arguments)


@patch('argparse.ArgumentParser.parse_args')
def test_copy_file_integration_cool(mock_args, variables):
    file_name = 'nested_file_1.txt'
    reset_path = 'cool_file_integration'
    storage_tier = 'Cool'
    rename = 'nested_file_1_copy.txt'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        file=file_name,
        storage_tier=storage_tier,
        name=rename,
        copy=True,
    )
    arguments = cli()
    file_copy(arguments)
    blobs = variables.target_container_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join(reset_path, rename):
            assert blob.blob_tier == storage_tier


@patch('argparse.ArgumentParser.parse_args')
def test_copy_folder_integration(mock_args, variables):
    folder_name = 'nested_folder_5'
    reset_path = 'folder_integration'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        folder=folder_name,
        storage_tier=variables.storage_tier,
        copy=True,
    )
    arguments = cli()
    folder_copy(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, 'nested_folder_test_1.txt') in [blob.name for blob in blobs]
    original_blobs = variables.source_container_client.list_blobs()
    assert folder_name in [os.path.dirname(blob.name) for blob in original_blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_copy_container_integration(mock_args, variables):
    reset_path = 'container_integration'
    mock_args.return_value = argparse.Namespace(
        account_name=variables.account_name,
        container_name=variables.container_name,
        target_container=variables.target_container,
        reset_path=reset_path,
        verbosity='info',
        storage_tier=variables.storage_tier,
        copy=True,
    )
    arguments = cli()
    container_copy(arguments)
    blobs = variables.target_container_client.list_blobs()
    assert os.path.join(reset_path, 'double_nested_file_1.txt') in [blob.name for blob in blobs]
    original_blobs = variables.source_container_client.list_blobs()
    assert original_blobs
