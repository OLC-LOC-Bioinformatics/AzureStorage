from azure_storage.methods import extract_account_name, setup_logging
from azure_storage import azure_credentials
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
            self.verbosity = 'info'

    return Variables()


def test_setup_logging(variables):
    setup_logging(arguments=variables)

