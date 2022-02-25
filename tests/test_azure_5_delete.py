from azure_storage.methods import create_blob_service_client, create_container_client, delete_container, \
    extract_account_name, extract_connection_string
import pytest
import os


@pytest.fixture(name='variables', scope='module')
def setup():
    class Variables:
        def __init__(self):
            # Extract the account name and connection string from the system keyring prior to running tests
            self.passphrase = 'AzureStorage'
            self.account_name = extract_account_name(passphrase=self.passphrase)
            self.connection_string = extract_connection_string(passphrase=self.passphrase,
                                                               account_name=self.account_name)
            self.container_name = '000000container'
            self.blob_service_client = create_blob_service_client(connect_str=self.connection_string)
            self.test_path = os.path.abspath(os.path.dirname(__file__))
            self.file_path = os.path.join(self.test_path, 'files')

    return Variables()


def test_delete_container(variables):
    delete_container(blob_service_client=variables.blob_service_client,
                     container_name=variables.container_name,
                     account_name=variables.account_name)
