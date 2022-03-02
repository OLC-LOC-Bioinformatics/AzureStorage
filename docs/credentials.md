## AzureCredentials

AzureCredentials allows you to store, modify, or delete your Azure account name and connection string in the system keyring

Choose either the [`store`](#azure-credentials-store) or [`delete`](#azure-credentials-delete) functionality

[Find your connection string](https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string#:~:text=You%20can%20find%20your%20storage,primary%20and%20secondary%20access%20keys.)

[Find your account key](https://www.zenko.io/blog/how-to-find-keys-and-account-info-for-aws-azure-and-google/#:~:text=Azure%20Account%20Name%C2%A0%3D%20the%20name%20of%20your%20Azure%20storage%20account%20located%20on%20the%20top%20of%20the%20Azure%20Portal%20(screenshot%20below%20%E2%80%93%20%E2%80%9Cscalitydemo%E2%80%9D%20is%20Azure%20Account%20Name).)


#### General Usage

```
usage: AzureCredentials [-h] {store,delete} ...

Set, modify, or delete Azure storage credentials in the system keyring

optional arguments:
  -h, --help      show this help message and exit

Available functionality:
  {store,delete}
    store         Store or update Azure storage credentials in the system keyring
    delete        Delete Azure storage credentials in the system keyring

```

### Azure credentials store

Store or modify your account name and connection string in the system keyring

#### Required arguments:
- account name

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example command:

To store the account name `account_name` and your connection string in the system keyring

`AzureCredentials store -a account_name`

You will be prompted to enter your connection string by the script. Note that, as a security precaution, you will not see the text you entered. 

#### Usage
```
usage: AzureCredentials store [-h] -a ACCOUNT_NAME [-p PASSPHRASE]
                              [-v {debug,info,warning,error,critical}]

Store or update Azure storage credentials in the system keyring

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v {debug,info,warning,error,critical}, --verbosity {debug,info,warning,error,critical}
                        Set the logging level. Default is info.

```

### Azure credentials delete

Delete your account name and connection string from the system keyring

#### Required arguments:
- account name

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example command:

To delete the account name `account_name` and your connection string from the system keyring

`AzureCredentials delete -a account_name`

You will be prompted to enter your connection string by the script. Note that, as a security precaution, you will not see the text you entered.

#### Usage

```
usage: AzureCredentials delete [-h] -a ACCOUNT_NAME [-p PASSPHRASE]
                               [-v {debug,info,warning,error,critical}]

Delete Azure storage credentials in the system keyring

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v {debug,info,warning,error,critical}, --verbosity {debug,info,warning,error,critical}
                        Set the logging level. Default is info.

```