from azure_storage.methods import create_blob_service_client, extract_account_name, extract_connection_string
from azure_storage.azure_list import AzureContainerList, AzureList, azure_search, cli, container_search
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
            self.test_path = os.path.abspath(os.path.dirname(__file__))
            self.file_path = os.path.join(self.test_path, 'files')
            self.output_file = os.path.join(self.file_path, 'search_outputs.txt')
            self.connection_string = extract_connection_string(passphrase=self.passphrase,
                                                               account_name=self.account_name)
            self.blob_service_client = create_blob_service_client(connect_str=self.connection_string)

    return Variables()


def read_output_file(output_file):
    contents = list()
    with open(output_file, 'r') as output:
        for line in output:
            contents.append(line.rstrip())
    return contents


def delete_output_file(output_file):
    os.remove(output_file)


@pytest.mark.parametrize('expression',
                         ['000000container',
                          '0000\\d{2}container',
                          '0000\\d{2}\\D{9}',
                          '0000*',
                          '*container'])
def test_list_containers(variables, expression):
    AzureContainerList.list_containers(
        blob_service_client=variables.blob_service_client,
        expression=expression,
        print_container=False,
        output_file=variables.output_file)
    contents = read_output_file(output_file=variables.output_file)
    assert variables.container_name in contents
    delete_output_file(output_file=variables.output_file)


@pytest.mark.parametrize('expression',
                         ['000000container1',
                          '0000\\d{3}container',
                          '0000\\d{2}\\D{10}'
                          '100000*',
                          '*containers'])
def test_list_containers_invalid(variables, expression):
    with pytest.raises(FileNotFoundError):
        AzureContainerList.list_containers(
            blob_service_client=variables.blob_service_client,
            expression=expression,
            print_container=False,
            output_file=variables.output_file)
        read_output_file(output_file=variables.output_file)
