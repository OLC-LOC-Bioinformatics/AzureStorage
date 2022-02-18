#!/usr/bin/env python
from azure_storage.methods import set_connection_string, setup_arguments
from azure_storage.azure_credentials import cli, credentials
from unittest.mock import patch
import unittest
import argparse


class TestCredentials(unittest.TestCase):

    def setUp(self) -> None:
        self.connect_str = \
            'DefaultEndpointsProtocol=https;AccountName=testcredentials;AccountKey=xxx;EndpointSuffix=core.windows.net'

    @patch('getpass.getpass')
    def test_set_credentials_invalid(self, getpass):
        getpass.return_value = self.connect_str
        with self.assertRaises(SystemExit):
            set_connection_string(passphrase='12234', account_name='credentials')

    @patch('getpass.getpass')
    def test_set_credentials_valid(self, getpass):
        getpass.return_value = self.connect_str
        assert set_connection_string(passphrase='12234', account_name='testcredentials') == self.connect_str

    @patch('argparse.ArgumentParser.parse_args')
    @patch('getpass.getpass')
    def test_credentials_integration(self, getpass, mock_args):
        getpass.return_value = self.connect_str
        mock_args.return_value = argparse.Namespace(passphrase='122346', account_name='abcde')
        cli()


if __name__ == '__main__':
    unittest.main()
