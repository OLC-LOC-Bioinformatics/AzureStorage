from azure_storage.methods import create_container_client, create_blob_sas, create_blob_service_client, \
    extract_account_name, extract_connection_string, sas_prep, write_sas
from azure_storage.azure_sas import AzureContainerSAS, AzureSAS, cli, container_sas, file_sas, folder_sas
from unittest.mock import patch
import argparse
import pytest
import os


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            # Extract the account name and connection string from the system keyring prior to running tests
            self.passphrase = 'AzureStorage'
            self.account_name = extract_account_name(passphrase=self.passphrase)
            self.container_name = '00000container'
            self.test_path = os.path.abspath(os.path.dirname(__file__))
            self.file_path = os.path.join(self.test_path, 'files')
            self.output_file = os.path.join(self.file_path, 'sas_urls.txt')

    return Variables()


def delete_output_file(output_file):
    os.remove(output_file)
    assert not os.path.isfile(output_file)


def test_sas_prep(variables):
    variables.container_name, variables.connection_string, variables.account_key, \
        variables.blob_service_client, variables.container_client = \
        sas_prep(container_name=variables.container_name,
                 passphrase=variables.passphrase,
                 account_name=variables.account_name)
    assert variables.connection_string.startswith('DefaultEndpointsProtocol')


@pytest.mark.parametrize('file_name',
                         ['file_1.txt',
                          'nested_folder/nested_file_2.txt',
                          'nested_folder/nested_folder_2/nested_folder_test_1.txt'])
def test_file_sas(variables, file_name):
    variables.sas_urls = AzureSAS.file_sas(container_client=variables.container_client,
                                           account_name=variables.account_name,
                                           container_name=variables.container_name,
                                           object_name=file_name,
                                           account_key=variables.account_key,
                                           expiry=10,
                                           sas_urls=dict())
    assert variables.sas_urls[os.path.basename(file_name)]\
        .startswith(f'https://{variables.account_name}.blob.core.windows.net/{variables.container_name}/{file_name}?')


@pytest.mark.parametrize('file_name',
                         ['file_3.txt',
                          'nested_folder/nested_file_1.txt',
                          'nested_folder_3/nested_folder_2/nested_folder_test_1.txt'])
def test_file_sas_invalid(variables, file_name):
    with pytest.raises(SystemExit):
        AzureSAS.file_sas(container_client=variables.container_client,
                          account_name=variables.account_name,
                          container_name=variables.container_name,
                          object_name=file_name,
                          account_key=variables.account_key,
                          expiry=10,
                          sas_urls=dict())


def test_sas_urls_output_exists(variables):
    write_sas(output_file=variables.output_file,
              sas_urls=variables.sas_urls)
    assert os.path.isfile(variables.output_file)


def test_sas_urls_output_contents(variables):
    contents = open(variables.output_file, 'r').readlines()
    assert contents[0]\
        .startswith(f'https://{variables.account_name}.blob.core.windows.net/{variables.container_name}/')


@pytest.mark.parametrize('output_file,expiry',
                         [('sas_urls.txt', 0),
                          ('sas_urls.txt', 500),
                          ('', 1),
                          ('folder/', 1),
                          ('protected_folder/sas_urls.txt', 1),
                          ('protected_folder/nested_folder/sas_urls.txt', 1)])
@patch('argparse.ArgumentParser.parse_args')
def test_file_sas_integration_invalid(mock_args, output_file, expiry, variables):
    file_name = 'file_1.txt'
    output_file = os.path.join(variables.file_path, output_file)
    with pytest.raises(SystemExit):
        mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                    account_name=variables.account_name,
                                                    container_name=variables.container_name,
                                                    verbosity='info',
                                                    file=file_name,
                                                    output_file=output_file,
                                                    expiry=expiry)
        arguments = cli()
        file_sas(args=arguments)


@patch('argparse.ArgumentParser.parse_args')
def test_file_sas_integration(mock_args, variables):
    delete_output_file(output_file=variables.output_file)
    file_name = 'file_1.txt'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                file=file_name,
                                                output_file=variables.output_file,
                                                expiry=1)
    arguments = cli()
    file_sas(args=arguments)


def test_file_sas_urls_integration_output_contents(variables):
    contents = open(variables.output_file, 'r').readlines()
    assert contents[0]\
        .startswith(f'https://{variables.account_name}.blob.core.windows.net/{variables.container_name}/')


@pytest.mark.parametrize('folder_name,expected_dictionary_length',
                         [('nested_folder', 3),
                          ('nested_folder/nested_folder_2/', 1)])
def test_folder_sas(variables, folder_name, expected_dictionary_length):
    variables.sas_urls = AzureSAS.folder_sas(container_client=variables.container_client,
                                             account_name=variables.account_name,
                                             container_name=variables.container_name,
                                             object_name=folder_name,
                                             account_key=variables.account_key,
                                             expiry=10,
                                             sas_urls=dict())
    assert len(variables.sas_urls) == expected_dictionary_length


@pytest.mark.parametrize('folder_name',
                         ['nested3',
                          '',
                          'nested_folder/nested_folder_2/nested_folder_test_1.txt'
                          'nested_folder/nested_folder_1/',
                          'nested_folder/nested_folder_2/nested_folder_3'])
def test_folder_sas_invalid(variables, folder_name):
    with pytest.raises(SystemExit):
        variables.sas_urls = AzureSAS.folder_sas(container_client=variables.container_client,
                                                 account_name=variables.account_name,
                                                 container_name=variables.container_name,
                                                 object_name=folder_name,
                                                 account_key=variables.account_key,
                                                 expiry=10,
                                                 sas_urls=dict())


@patch('argparse.ArgumentParser.parse_args')
def test_folder_sas_integration(mock_args, variables):
    delete_output_file(output_file=variables.output_file)
    folder_name = 'nested_folder'
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                verbosity='info',
                                                folder=folder_name,
                                                output_file=variables.output_file,
                                                expiry=1)
    arguments = cli()
    folder_sas(args=arguments)


def test_folder_sas_urls_integration_output_contents(variables):
    contents = open(variables.output_file, 'r').readlines()
    assert contents[0]\
        .startswith(f'https://{variables.account_name}.blob.core.windows.net/{variables.container_name}/')


def test_delete_output_file(variables):
    os.remove(variables.output_file)
    assert not os.path.isfile(variables.output_file)
