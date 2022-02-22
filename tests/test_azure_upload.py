from azure_storage.methods import confirm_account_match, extract_account_name, extract_connection_string, \
    validate_container_name
import pytest
import random
import string

letters = string.ascii_lowercase
long_container = ''.join(random.choice(letters) for i in range(65))


@pytest.fixture(name='credentials', scope='class')
def setup():
    class Credentials:
        def __init__(self):
            self.account_name = extract_account_name(passphrase='AzureStorage')
            self.connection_string = extract_connection_string(passphrase='AzureStorage',
                                                               account_name=self.account_name)
            self.container_name = '00000'
    return Credentials()


def test_account_name(credentials):
    assert credentials.account_name


def test_connection_string(credentials):
    assert credentials.connection_string.startswith('DefaultEndpointsProtocol')


def test_account_match(credentials):
    assert confirm_account_match(account_name=credentials.account_name,
                                 connect_str=credentials.connection_string)


@pytest.mark.parametrize('test_input,expected',
                         [('12345', '12345'),
                          ('123___45', '123-45'),
                          ('--12345---', '12345'),
                          ('0', '0000'),
                          ('ABCD', 'abcd'),
                          ('Abc123-', 'abc123'),
                          ('@#2$5@7#', '257'),
                          (long_container, long_container[:62])])
def test_validate_container_name(test_input, expected):
    assert validate_container_name(container_name=test_input) == expected


@pytest.mark.parametrize('test_input', ['---',
                                        '@#$@#'
                                        ''])
def test_validate_container_name_fail(test_input):
    with pytest.raises(SystemExit):
        validate_container_name(container_name=test_input)
