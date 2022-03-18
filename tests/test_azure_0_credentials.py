#!/usr/bin/env python
from azure_storage.methods import extract_account_name, extract_account_key, extract_connection_string, \
    delete_keyring_credentials, set_account_name, set_connection_string, setup_arguments
from azure_storage.azure_credentials import cli, delete_credentials, store_credentials
from unittest.mock import patch
import argparse
import pytest


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


@patch('getpass.getpass')
def test_set_credentials_malformed_string(getpass):
    getpass.return_value = 'bad_string'
    with pytest.raises(SystemExit):
        set_connection_string(passphrase=passphrase,
                              account_name=account_name)


def test_set_account_name():
    assert set_account_name(passphrase=passphrase, account_name=account_name) == account_name


def test_extract_account_name():
    assert extract_account_name(passphrase=passphrase) == account_name


def test_extract_account_key_invalid_str():
    con_str = 'bad_key'
    with pytest.raises(SystemExit):
        extract_account_key(connect_str=con_str)


@patch('getpass.getpass')
def test_set_credentials(getpass):
    getpass.return_value = connect_str
    assert set_connection_string(passphrase=passphrase, account_name=account_name) == connect_str


def test_extract_credentials():
    assert extract_connection_string(passphrase=passphrase, account_name=account_name) \
        .startswith('DefaultEndpointsProtocol')


@patch('getpass.getpass')
def test_extract_credentials_new_phrase(getpass):
    getpass.return_value = connect_str
    assert extract_connection_string(passphrase='fake', account_name=account_name) \
        .startswith('DefaultEndpointsProtocol')


def test_delete_credentials():
    phrase = 'fake'
    assert delete_keyring_credentials(passphrase=phrase, account_name=account_name) == account_name


@patch('getpass.getpass')
def test_extract_credentials_invalid(getpass):
    getpass.return_value = connect_str
    phrase = 'fake'
    account = 'bogus'
    with pytest.raises(SystemExit):
        set_connection_string(passphrase=phrase, account_name=account)


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


def test_extract_account_name_new(monkeypatch):
    new_account = 'account'
    monkeypatch.setattr('builtins.input', lambda _: new_account)
    assert extract_account_name(passphrase='fake') == new_account


def test_delete_account_name_new():
    phrase = 'fake'
    assert delete_keyring_credentials(passphrase=phrase, account_name=phrase) == phrase


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
