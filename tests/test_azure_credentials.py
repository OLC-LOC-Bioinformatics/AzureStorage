#!/usr/bin/env python
from azure_storage.methods import set_connection_string, setup_arguments
from azure_storage.azure_credentials import cli, credentials
from unittest.mock import patch
import unittest
import argparse


class TestCredentials(unittest.TestCase):
    @patch("getpass.getpass")
    def test_set_credentials(self, getpass):
        getpass.return_value = "xxx"
        assert set_connection_string(passphrase='12234', account_name='abcd') == 'xxx'

    @patch('argparse.ArgumentParser.parse_args')
    @patch('getpass.getpass')
    def test_credentials_integration(self, getpass, mock_args):
        getpass.return_value = 'fwiuhfw7h2h#@#f'
        mock_args.return_value = argparse.Namespace(passphrase='122346', account_name='abcde')
        cli()


if __name__ == '__main__':
    unittest.main()
