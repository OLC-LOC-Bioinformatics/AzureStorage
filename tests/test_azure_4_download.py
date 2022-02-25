from azure_storage.methods import client_prep, create_blob_service_client, create_container_client, \
    extract_account_name, extract_connection_string
from azure_storage.azure_download import AzureContainerDownload, AzureDownload, cli, container_download, \
    file_download, folder_download
from unittest.mock import patch
import argparse
import pytest
import shutil
import azure
import os


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            # Extract the account name and connection string from the system keyring prior to running tests
            self.passphrase = 'AzureStorage'
            self.account_name = extract_account_name(passphrase=self.passphrase)
            self.container_name = '000000container'
            self.test_path = os.path.abspath(os.path.dirname(__file__))
            self.file_path = os.path.join(self.test_path, 'files')
            self.output_path = os.path.join(self.file_path, 'downloads')

    return Variables()


def test_client_prep(variables):
    variables.container_name, variables.connect_str, variables.blob_service_client, variables.container_client = \
        client_prep(container_name=variables.container_name,
                    passphrase=variables.passphrase,
                    account_name=variables.account_name)
    assert type(variables.container_client) is azure.storage.blob._container_client.ContainerClient


@pytest.mark.parametrize('file_name',
                         ['file_1.txt',
                          'container_integration/file_2.txt',
                          'nested_container/nested_folder/nested_folder_2/nested_folder_test_1.txt',
                          'ABC/123/nested_folder_test_1.txt'])
def test_download_file(variables, file_name):
    output_path = os.path.join(variables.output_path, 'files')
    os.makedirs(output_path, exist_ok=True)
    AzureDownload.download_file(container_client=variables.container_client,
                                blob_service_client=variables.blob_service_client,
                                container_name=variables.container_name,
                                object_name=file_name,
                                output_path=output_path)
    assert os.path.isfile(os.path.join(output_path, os.path.basename(file_name)))


@pytest.mark.parametrize('file_name',
                         ['file_2.txt',
                          'container_integration_1/file_2.txt',
                          'nested_container/nested_folder/nested_folder_2/nested_folder_test_1.zip',
                          'ABC/1234/nested_folder_test_1.txt'])
def test_download_file_invalid(variables, file_name):
    output_path = os.path.join(variables.output_path, 'files')
    with pytest.raises(SystemExit):
        AzureDownload.download_file(container_client=variables.container_client,
                                    blob_service_client=variables.blob_service_client,
                                    container_name=variables.container_name,
                                    object_name=file_name,
                                    output_path=output_path)


@patch('argparse.ArgumentParser.parse_args')
def test_download_file_integration(mock_args, variables):
    output_path = os.path.join(variables.output_path, 'files_integration')
    file_name = 'nested/file_2.txt'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                output_path=output_path,
                                                verbosity='info',
                                                file=file_name)
    arguments = cli()
    file_download(arguments)
    assert os.path.isfile(os.path.join(output_path, os.path.basename(file_name)))


@patch('argparse.ArgumentParser.parse_args')
def test_download_file_integration_missing(mock_args, variables):
    output_path = os.path.join(variables.output_path, 'files_integration')
    file_name = 'nested/file_3.txt'
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name=variables.container_name,
                                                    output_path=output_path,
                                                    verbosity='info',
                                                    file=file_name)
        arguments = cli()
        file_download(arguments)


def test_remove_downloads(variables):
    shutil.rmtree(variables.output_path)
    assert not os.path.isdir(variables.output_path)
