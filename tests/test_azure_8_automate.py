from azure_storage.methods import create_batch_dict, create_blob_service_client, create_container, \
    extract_account_name, extract_connection_string
from azure_storage.azure_automate import file_upload, folder_upload, container_sas, file_sas, folder_sas, \
    container_move, file_move, folder_move, container_download, file_download, folder_download, container_tier, \
    file_tier, folder_tier, container_delete, file_delete, folder_delete, batch, cli
from unittest.mock import patch
import argparse
import pytest
import shutil
import os


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            self.passphrase = 'AzureStorage'
            self.account_name = extract_account_name(passphrase=self.passphrase)
            self.connection_string = extract_connection_string(passphrase=self.passphrase,
                                                               account_name=self.account_name)
            self.blob_service_client = create_blob_service_client(connect_str=self.connection_string)
            self.container_name = '0container'
            self.target_container = '00container'
            self.file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files')
            self.batch_path = os.path.join(self.file_path, 'batch')
            self.sas_path = os.path.join(self.file_path, 'sas')
            self.download_path = os.path.join(self.file_path, 'download')
            os.makedirs(self.download_path, exist_ok=True)
    return Variables()


def create_container_client(variables, container_name):
    container_client = create_container(blob_service_client=variables.blob_service_client,
                                        container_name=container_name)
    return container_client


def read_contents(output_file):
    contents = open(output_file, 'r').readlines()
    return contents


def delete_output_file(output_file):
    os.remove(output_file)
    assert not os.path.isfile(output_file)


@patch('argparse.ArgumentParser.parse_args')
def test_batch_upload_file_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'upload_file.tsv'))
    arguments = cli()
    file_upload(args=arguments)
    variables.container_client = create_container_client(variables=variables,
                                                         container_name=variables.container_name)
    blobs = variables.container_client.list_blobs()
    assert 'upload/file_1.txt' in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_batch_upload_folder_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'upload_folder.tsv'))
    arguments = cli()
    folder_upload(args=arguments)
    blobs = variables.container_client.list_blobs()
    assert 'nested_folder/nested/double_nested_file_1.txt' in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_batch_file_sas_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'sas_file.tsv'))
    arguments = cli()
    file_sas(args=arguments)
    contents = read_contents(output_file=os.path.join(variables.sas_path, 'sas_test.txt'))
    assert contents[0] \
        .startswith(f'https://{variables.account_name}.blob.core.windows.net/{variables.container_name}/')
    delete_output_file(output_file='sas_urls.txt')
    delete_output_file(output_file=os.path.join(variables.sas_path, 'sas_test.txt'))
    delete_output_file(output_file=os.path.join(variables.sas_path, 'sas_test_1.txt'))


@patch('argparse.ArgumentParser.parse_args')
def test_batch_folder_sas_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'sas_folder.tsv'))
    arguments = cli()
    folder_sas(args=arguments)
    contents = read_contents(output_file=os.path.join(variables.sas_path, 'sas_test_1.txt'))
    assert contents[0] \
        .startswith(f'https://{variables.account_name}.blob.core.windows.net/{variables.container_name}/')
    delete_output_file(output_file='sas_test.txt')
    delete_output_file(output_file='sas_urls.txt')
    delete_output_file(output_file=os.path.join(variables.sas_path, 'sas_test_1.txt'))


@patch('argparse.ArgumentParser.parse_args')
def test_batch_container_sas_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'sas_container.tsv'))
    arguments = cli()
    container_sas(args=arguments)
    contents = read_contents(output_file=os.path.join(variables.sas_path, 'sas_test_1.txt'))
    assert contents[0] \
        .startswith(f'https://{variables.account_name}.blob.core.windows.net/{variables.container_name}/')
    delete_output_file(output_file='sas_urls.txt')
    delete_output_file(output_file=os.path.join(variables.sas_path, 'sas_test.txt'))
    delete_output_file(output_file=os.path.join(variables.sas_path, 'sas_test_1.txt'))
    shutil.rmtree(variables.sas_path)


@patch('argparse.ArgumentParser.parse_args')
def test_batch_file_move_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'move_file.tsv'))
    arguments = cli()
    file_move(args=arguments)
    variables.target_client = create_container_client(variables=variables,
                                                      container_name=variables.target_container)
    blobs = variables.target_client.list_blobs()
    assert 'move_files/folder_test_1.txt' in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_batch_folder_move_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'move_folder.tsv'))
    arguments = cli()
    folder_move(args=arguments)
    blobs = variables.target_client.list_blobs()
    assert 'move_folder/file_1.txt' in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_batch_container_move_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'move_container.tsv'))
    arguments = cli()
    container_move(args=arguments)
    blobs = variables.target_client.list_blobs()
    assert 'nested_1/upload/file_1.txt' in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_batch_file_download_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'download_file.tsv'))
    arguments = cli()
    file_download(args=arguments)
    assert os.path.isfile('file_1.txt')
    delete_output_file(output_file='file_1.txt')


@patch('argparse.ArgumentParser.parse_args')
def test_batch_folder_download_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'download_folder.tsv'))
    arguments = cli()
    folder_download(args=arguments)
    assert os.path.isfile(os.path.join('move_folder', 'file_1.txt'))
    shutil.rmtree('move_folder')


@patch('argparse.ArgumentParser.parse_args')
def test_batch_container_download_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'download_container.tsv'))
    arguments = cli()
    container_download(args=arguments)
    assert os.path.isfile(os.path.join(variables.download_path, variables.target_container, 'nested_1', 'file_1.txt'))
    shutil.rmtree(variables.target_container)


@patch('argparse.ArgumentParser.parse_args')
def test_batch_file_tier_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'tier_file.tsv'))
    arguments = cli()
    file_tier(args=arguments)
    blobs = variables.target_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join('nested_1', 'file_1.txt'):
            assert blob.blob_tier == 'Cool'


@patch('argparse.ArgumentParser.parse_args')
def test_batch_folder_tier_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'tier_folder.tsv'))
    arguments = cli()
    folder_tier(args=arguments)
    blobs = variables.target_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join('move_folder', 'file_1.txt'):
            assert blob.blob_tier == 'Cool'


@patch('argparse.ArgumentParser.parse_args')
def test_batch_container_tier_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'tier_container.tsv'))
    arguments = cli()
    container_tier(args=arguments)
    blobs = variables.target_client.list_blobs()
    for blob in blobs:
        if blob.name == os.path.join('nested_1', 'file_1.txt'):
            assert blob.blob_tier == 'Cool'


@patch('argparse.ArgumentParser.parse_args')
def test_batch_file_delete_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'delete_file.tsv'))
    arguments = cli()
    file_delete(args=arguments)
    blobs = variables.target_client.list_blobs()
    assert 'nested_1/renamed/nested/double_nested_file_2.txt' not in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_batch_folder_delete_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'delete_folder.tsv'))
    arguments = cli()
    folder_delete(args=arguments)
    blobs = variables.target_client.list_blobs()
    assert 'move_folder/file_1.txt' not in [blob.name for blob in blobs]


@patch('argparse.ArgumentParser.parse_args')
def test_batch_container_delete_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'delete_container.tsv'))
    arguments = cli()
    container_delete(args=arguments)
    with pytest.raises(SystemExit) as e:
        create_container_client(variables=variables,
                                container_name=variables.target_container)
        assert 'The specified container is being deleted. Try operation later.' in str(e)


@patch('argparse.ArgumentParser.parse_args')
def test_batch(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                verbosity='info',
                                                batch_file=os.path.join(variables.batch_path, 'batch.tsv'))
    arguments = cli()
    batch(args=arguments)
    delete_output_file(output_file='file_1.txt')
    delete_output_file(output_file='sas_test.txt')
    delete_output_file(output_file='sas_urls.txt')
    shutil.rmtree('move_folder')
    shutil.rmtree('0000container')
    shutil.rmtree(variables.download_path)
    shutil.rmtree(variables.sas_path)
    with pytest.raises(SystemExit) as e:
        create_container_client(variables=variables,
                                container_name='0000container')
        assert 'The specified container is being deleted. Try operation later.' in str(e)


@patch('argparse.ArgumentParser.parse_args')
def test_batch_invalid_batch_path(mock_args, variables):
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    verbosity='info',
                                                    batch_file=os.path.join('/invalid', 'batch.tsv'))
        arguments = cli()
        batch(args=arguments)


@patch('argparse.ArgumentParser.parse_args')
def test_batch_invalid_batch_file(mock_args, variables):
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    verbosity='info',
                                                    batch_file=os.path.join(variables.batch_path, 'invalid.tsv'))
        arguments = cli()
        batch(args=arguments)


def test_invalid_batch_file(variables):
    with pytest.raises(SystemExit):
        create_batch_dict(batch_file=os.path.join(variables.batch_path, 'invalid.tsv'),
                          headers=list())


@patch('argparse.ArgumentParser.parse_args')
def test_batch_malformed_batch_file(mock_args, variables):
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    verbosity='info',
                                                    batch_file=os.path.join(variables.batch_path, 'batch_invalid.tsv'))
        arguments = cli()
        batch(args=arguments)


@patch('argparse.ArgumentParser.parse_args')
def test_batch_extra_columns_batch_file(mock_args, variables):
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(
            passphrase=variables.passphrase,
            account_name=variables.account_name,
            verbosity='info',
            batch_file=os.path.join(variables.batch_path, 'batch_invalid_1.tsv'))
        arguments = cli()
        batch(args=arguments)
