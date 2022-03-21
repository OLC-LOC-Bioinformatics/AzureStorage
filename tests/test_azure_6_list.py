from azure_storage.methods import client_prep, create_blob_service_client, extract_account_name, \
    extract_connection_string
from azure_storage.azure_list import AzureContainerList, AzureList, azure_search, cli, container_search
from unittest.mock import patch
import argparse
import pathlib
import pytest
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


def parse_file_outputs(check_file, contents):
    hit = False
    for entry in contents:
        if check_file in [os.path.basename(component) for component in entry.split('\t')]:
            hit = True
    return hit


def test_client_prep(variables):
    variables.container_name, variables.connect_str, variables.blob_service_client, variables.container_client = \
        client_prep(container_name=variables.container_name,
                    passphrase=variables.passphrase,
                    account_name=variables.account_name)
    assert variables.connect_str.startswith('DefaultEndpointsProtocol')


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


def test_list_container_tilde(variables):
    path_obj = pathlib.Path(variables.file_path)
    path = f'~{os.sep}{path_obj.relative_to(pathlib.Path.home())}'
    list_containers = AzureContainerList(
        expression=variables.container_name,
        account_name=variables.account_name,
        output_file=os.path.join(path, 'search_outputs.txt'),
        passphrase=variables.passphrase
    )
    list_containers.main()
    contents = read_output_file(output_file=variables.output_file)
    assert variables.container_name in contents
    delete_output_file(output_file=variables.output_file)


def test_list_container_invalid_path(variables):
    output_file = os.path.join('/var', 'search_outputs.txt')
    with pytest.raises(SystemExit):
        AzureContainerList(
            expression=variables.container_name,
            account_name=variables.account_name,
            output_file=output_file,
            passphrase=variables.passphrase
        )


def test_list_container_directory_provided(variables):
    with pytest.raises(SystemExit):
        AzureContainerList(
            expression=variables.container_name,
            account_name=variables.account_name,
            output_file=variables.file_path,
            passphrase=variables.passphrase
        )


def test_list_container_no_output_file(variables):
    list_containers = AzureContainerList(
        expression=variables.container_name,
        account_name=variables.account_name,
        output_file=str(),
        passphrase=variables.passphrase
    )
    list_containers.main()
    assert not os.path.isfile(variables.output_file)


@patch('argparse.ArgumentParser.parse_args')
def test_list_container_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                expression='0*',
                                                verbosity='info',
                                                output_file=variables.output_file)
    arguments = cli()
    container_search(arguments)
    contents = read_output_file(output_file=variables.output_file)
    assert variables.container_name in contents
    delete_output_file(output_file=variables.output_file)


@pytest.mark.parametrize('container,expression,check_file',
                         [('000000container', 'file_1', 'file_1'),
                          ('000000container', 'file_1.gz', 'file_1.gz'),
                          ('000000container', 'container_integration/*_5/*.txt', 'nested_folder_test_1.txt'),
                          ('000000container', '*.txt', 'file_2.txt'),
                          ('000000container', '\\D{14}3/*_1.txt', 'nested_folder_test_1.txt'),
                          ('000000container', 'h\\D{2}/nes*', 'nested_folder_test_1.txt')])
def test_list_file(variables, container, expression, check_file):
    AzureList.list_files(container_client=variables.container_client,
                         expression=expression,
                         output_file=variables.output_file,
                         container_name=container)
    contents = read_output_file(output_file=variables.output_file)
    hit = parse_file_outputs(check_file=check_file,
                             contents=contents)
    assert hit
    delete_output_file(output_file=variables.output_file)


def test_list_file_tilde(variables):
    path_obj = pathlib.Path(variables.file_path)
    path = f'~{os.sep}{path_obj.relative_to(pathlib.Path.home())}'
    output_file = os.path.join(path, 'search_outputs.txt')
    check_file = 'triple_nested_file.txt'
    list_files = AzureList(
        container_name=variables.container_name,
        expression=check_file,
        account_name=variables.account_name,
        output_file=output_file,
        passphrase=variables.passphrase
    )
    list_files.main()
    contents = read_output_file(output_file=variables.output_file)
    hit = parse_file_outputs(check_file=check_file,
                             contents=contents)
    assert hit
    delete_output_file(output_file=variables.output_file)


def test_list_file_invalid_path(variables):
    output_file = os.path.join('/var', 'search_outputs.txt')
    with pytest.raises(SystemExit):
        AzureList(
            container_name=variables.container_name,
            expression=None,
            account_name=variables.account_name,
            output_file=output_file,
            passphrase=variables.passphrase
        )


def test_list_file_directory_provided(variables):
    with pytest.raises(SystemExit):
        AzureList(
            container_name=variables.container_name,
            expression=None,
            account_name=variables.account_name,
            output_file=variables.file_path,
            passphrase=variables.passphrase
        )


def test_list_file_no_output_file(variables):
    list_files = AzureList(
        container_name=variables.container_name,
        expression=None,
        account_name=variables.account_name,
        output_file=str(),
        passphrase=variables.passphrase
    )
    list_files.main()
    assert not os.path.isfile(variables.output_file)


@patch('argparse.ArgumentParser.parse_args')
def test_list_file_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name=variables.container_name,
                                                expression='con*/c*/triple*file.txt',
                                                verbosity='info',
                                                output_file=variables.output_file)
    arguments = cli()
    azure_search(arguments)
    contents = read_output_file(output_file=variables.output_file)
    hit = False
    for entry in contents:
        if 'triple_nested_file.txt' in [os.path.basename(component) for component in entry.split('\t')]:
            hit = True
    assert hit
    delete_output_file(output_file=variables.output_file)


@patch('argparse.ArgumentParser.parse_args')
def test_list_file_container_expression_integration(mock_args, variables):
    mock_args.return_value = argparse.Namespace(passphrase=variables.passphrase,
                                                account_name=variables.account_name,
                                                container_name='0*',
                                                expression='nested_c*/double*file_1.txt',
                                                verbosity='info',
                                                output_file=variables.output_file)
    arguments = cli()
    azure_search(arguments)
    contents = read_output_file(output_file=variables.output_file)
    hit = False
    for entry in contents:
        if 'double_nested_file_1.txt' in [os.path.basename(component) for component in entry.split('\t')]:
            hit = True
    assert hit
    delete_output_file(output_file=variables.output_file)
