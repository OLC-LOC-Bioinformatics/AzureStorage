#!/usr/bin/env python
from azure_storage.methods import extract_account_name, extract_connection_string, delete_keyring_credentials, \
    set_account_name, set_connection_string, setup_arguments
from azure_storage.azure_credentials import cli, delete_credentials, store_credentials
from unittest.mock import patch
import pytest
import argparse


connect_str = \
        'DefaultEndpointsProtocol=https;AccountName=testcredentials;AccountKey=xxx;EndpointSuffix=core.windows.net'
passphrase = '12234'
account_name = 'testcredentials'


@patch('getpass.getpass')
def test_set_credentials_invalid(getpass):
    getpass.return_value = connect_str
    with pytest.raises(SystemExit):
        set_connection_string(passphrase=passphrase,
                              account_name='credentials')


def test_set_account_name():
    assert set_account_name(passphrase=passphrase, account_name=account_name) == account_name


def test_extract_account_name():
    assert extract_account_name(passphrase=passphrase) == account_name


@patch('getpass.getpass')
def test_set_credentials(getpass):
    getpass.return_value = connect_str
    assert set_connection_string(passphrase=passphrase, account_name=account_name) == connect_str


def test_extract_credentials():
    assert extract_connection_string(passphrase=passphrase, account_name=account_name) \
        .startswith('DefaultEndpointsProtocol')


def test_delete_account_name():
    assert delete_keyring_credentials(passphrase=passphrase, account_name=passphrase) == passphrase


def test_delete_account_name_missing():
    with pytest.raises(SystemExit):
        delete_keyring_credentials(passphrase=passphrase, account_name=passphrase)


def test_delete_connection_string():
    assert delete_keyring_credentials(passphrase=passphrase,
                                      account_name=account_name) == account_name


def test_delete_connection_string_missing():
    with pytest.raises(SystemExit):
        delete_keyring_credentials(passphrase=passphrase,
                                   account_name=account_name)


@patch('argparse.ArgumentParser.parse_args')
@patch('getpass.getpass')
def test_credentials_store_integration(getpass, mock_args):
    getpass.return_value = connect_str
    mock_args.return_value = argparse.Namespace(passphrase=passphrase, account_name=account_name)
    arguments = cli()
    store_credentials(args=arguments)


def test_extract_account_name_integration():
    assert extract_account_name(passphrase=passphrase) == account_name


def test_extract_credentials_integration():
    assert extract_connection_string(passphrase=passphrase, account_name=account_name) \
        .startswith('DefaultEndpointsProtocol')


@patch('argparse.ArgumentParser.parse_args')
@patch('getpass.getpass')
def test_credentials_delete_integration(getpass, mock_args):
    getpass.return_value = connect_str
    mock_args.return_value = argparse.Namespace(passphrase=passphrase, account_name=account_name)
    arguments = cli()
    delete_credentials(args=arguments)


def test_delete_account_name_integration():
    with pytest.raises(SystemExit):
        delete_keyring_credentials(passphrase=passphrase, account_name=passphrase)


def test_delete_connection_string_integration():
    with pytest.raises(SystemExit):
        delete_keyring_credentials(passphrase=passphrase,
                                   account_name=account_name)
