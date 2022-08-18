#!/usr/bin/env python
from azure_storage.methods import \
    extract_account_key, \
    encrypt_credentials, \
    decrypt_credentials, \
    delete_credentials_files, \
    set_credential_files
from azure_storage.azure_credentials import \
    cli, \
    delete_credentials, \
    store_credentials
from unittest.mock import patch
import argparse
import pytest
import os


connect_str = \
        'DefaultEndpointsProtocol=https;AccountName=testcredentials;AccountKey=xxx;EndpointSuffix=core.windows.net'
account_name = 'testcredentials'
azure_account = 'carlingst01'
credentials_file = str()
credentials_key = str()


@patch('getpass.getpass')
def test_set_credentials_invalid(getpass):
    getpass.return_value = connect_str
    with pytest.raises(SystemExit):
        encrypt_credentials(account_name='credentials')


@patch('getpass.getpass')
def test_set_credentials_malformed_string(getpass):
    getpass.return_value = 'bad_string'
    with pytest.raises(SystemExit):
        encrypt_credentials(account_name=account_name)


def test_extract_account_key_invalid_str():
    con_str = 'bad_key'
    with pytest.raises(SystemExit):
        extract_account_key(connect_str=con_str)


@patch('getpass.getpass')
def test_set_credentials(getpass):
    getpass.return_value = connect_str
    assert encrypt_credentials(account_name=account_name) == connect_str


def test_extract_credentials():
    assert decrypt_credentials(account_name=account_name).startswith('DefaultEndpointsProtocol')


@patch('getpass.getpass')
def test_extract_credentials_new_phrase(getpass):
    getpass.return_value = connect_str
    assert decrypt_credentials(account_name=account_name).startswith('DefaultEndpointsProtocol')


def test_set_credential_files():
    global credentials_file, credentials_key
    credentials_file, credentials_key = set_credential_files(account_name)
    assert os.path.isfile(credentials_file)
    assert os.path.isfile(credentials_key)


def test_delete_credentials():
    delete_credentials_files(account_name=account_name)
    assert not os.path.isfile(credentials_file)
    assert not os.path.isfile(credentials_key)


@patch('getpass.getpass')
def test_extract_credentials_invalid(getpass):
    getpass.return_value = connect_str
    account = 'bogus'
    with pytest.raises(SystemExit):
        encrypt_credentials(account_name=account)


def test_delete_account_name_missing():
    with pytest.raises(SystemExit):
        delete_credentials_files(account_name='nope')


def test_delete_connection_string_missing():
    with pytest.raises(SystemExit):
        delete_credentials_files(account_name=account_name)


@patch('argparse.ArgumentParser.parse_args')
@patch('getpass.getpass')
def test_credentials_store_integration(getpass, mock_args):
    getpass.return_value = connect_str
    mock_args.return_value = argparse.Namespace(account_name=account_name)
    arguments = cli()
    store_credentials(args=arguments)


def test_extract_credentials_integration():
    assert decrypt_credentials(account_name=account_name).startswith('DefaultEndpointsProtocol')


@patch('argparse.ArgumentParser.parse_args')
@patch('getpass.getpass')
def test_credentials_delete_integration(getpass, mock_args):
    getpass.return_value = connect_str
    mock_args.return_value = argparse.Namespace(account_name=account_name)
    arguments = cli()
    delete_credentials(args=arguments)


def test_delete_account_name_integration():
    with pytest.raises(SystemExit):
        delete_credentials_files(account_name='nope')


def test_delete_connection_string_integration():
    with pytest.raises(SystemExit):
        delete_credentials_files(account_name=account_name)


@patch('getpass.getpass')
def test_set_connect_str_from_env_var(getpass):
    connection_string = os.environ.get('AZURE_CONNECTION_STRING')
    if connection_string:
        getpass.return_value = connection_string
        assert encrypt_credentials(account_name=azure_account) == connection_string
