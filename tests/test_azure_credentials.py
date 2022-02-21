#!/usr/bin/env python
from azure_storage.methods import extract_account_name, extract_connection_string, delete_keyring_credentials, \
    set_account_name, set_connection_string, setup_arguments
from azure_storage.azure_credentials import cli
from unittest.mock import patch
import unittest
import argparse


class TestCredentials(unittest.TestCase):

    def setUp(self) -> None:
        self.connect_str = \
            'DefaultEndpointsProtocol=https;AccountName=testcredentials;AccountKey=xxx;EndpointSuffix=core.windows.net'
        self.passphrase = '12234'
        self.account_name = 'testcredentials'

    @patch('getpass.getpass')
    def test_set_credentials_invalid(self, getpass):
        getpass.return_value = self.connect_str
        with self.assertRaises(SystemExit):
            set_connection_string(passphrase=self.passphrase,
                                  account_name='credentials')

    def test_extract_account_name(self):
        assert set_account_name(passphrase=self.passphrase, account_name=self.account_name) == self.account_name
        assert extract_account_name(passphrase=self.passphrase) == self.account_name

    @patch('getpass.getpass')
    def test_extract_credentials(self, getpass):
        getpass.return_value = self.connect_str
        assert set_connection_string(passphrase=self.passphrase, account_name=self.account_name) == self.connect_str
        assert extract_connection_string(passphrase=self.passphrase, account_name=self.account_name)\
            .startswith('DefaultEndpointsProtocol')

    def test_delete_account_name(self):
        assert delete_keyring_credentials(passphrase=self.passphrase, account_name=self.passphrase) == self.passphrase
        with self.assertRaises(SystemExit):
            delete_keyring_credentials(passphrase=self.passphrase, account_name=self.passphrase)

    def test_delete_connection_string(self):
        assert delete_keyring_credentials(passphrase=self.passphrase,
                                          account_name=self.account_name) == self.account_name
        with self.assertRaises(SystemExit):
            delete_keyring_credentials(passphrase=self.passphrase,
                                       account_name=self.account_name)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('getpass.getpass')
    def test_credentials_integration(self, getpass, mock_args):
        getpass.return_value = self.connect_str
        mock_args.return_value = argparse.Namespace(passphrase=self.passphrase, account_name=self.account_name)
        cli()


if __name__ == '__main__':
    unittest.main()
