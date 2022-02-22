from azure_storage.methods import extract_account_name, extract_connection_string
import unittest


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.account_name = extract_account_name(passphrase='AzureStorage')
        self.connection_string = extract_connection_string(passphrase='AzureStorage',
                                                           account_name=self.account_name)

    def test_account_name(self):
        print(self.account_name)
        print(self.connection_string)
        assert self.account_name


if __name__ == '__main__':
    unittest.main()
