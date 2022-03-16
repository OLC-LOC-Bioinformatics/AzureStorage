## AzureList

List and optionally filter containers and/or files in your Azure storage account

Choose either the [`container`](#azurelist-container), or the [`search`](#azurelist-search) functionality

This script allows you to filter using regular expressions, so make sure you [know what you're doing](https://docs.python.org/3/howto/regex.html), [check out a tutorial](https://docs.python.org/3/howto/regex.html), [look at a cheatsheet](https://www.dataquest.io/blog/regex-cheatsheet/), and/or [test your expressions](https://pythex.org/)

**Important:** since the regular expressions are being entered on the command line, you will need to escape certain characters e.g. ! should be \!

#### General Usage

```
usage: AzureList [-h] {container,search} ...

Explore your Azure storage account

optional arguments:
  -h, --help          show this help message and exit

Available functionality:
  {container,search}
    container         Filter and list containers in your Azure storage account
    search            Search files in a container (or containers) in Azure storage
```

### AzureList container

List and optionally filter containers in your Azure storage account

#### AzureList container required arguments
- account name

#### AzureList container optional arguments
- expression: expression to use to filter the containers. Regular expressions are supported. Note that since the regular expression is being entered on the command line, you may need to escape certain characters e.g. ! should be \\!
- output_file: name and path of file in which the outputs are to be saved.
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### AzureList container example commands

These commands will use `account_name` as the name of the storage account

To list all containers in your Azure storage account

`AzureList container -a account_name`

To confirm the container `191216-dar` is present in your account

`AzureList container -a account_name 191216-dar`

To filter the list of containers to those starting with `19`

`AzureList container -a account_name 19*`

To filter the list of container to those starting with `19` and four additional digits followed by a dash

`AzureList container -a account_name 19d{4}-*`

To filter the list of containers to those starting with six digits, a dash, and three digits

`AzureList container -a account_name \\d{6}-\\D{3}`

To filter the list of containers to those ending with `outputs`

`AzureList container -a account_name *outputs\$`

To filter the list of containers to those that start with `19` and four additional digits, followed by a dash, three letters, and does not contain the word `outputs`

`AzureList container -a account_name 1912\\d{2}-\\D{3}\(\?\!*output\)`

#### AzureList container usage

```
usage: AzureList container [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-o OUTPUT_FILE]
                           [expression]

Filter and list containers in your Azure storage account

positional arguments:
  expression            Expression to search. This command supports regular expressions. e.g. 1912* will return all containers starting with 1912, including 191216-dar Note that since the regular expression is being entered on the command line, you may need to escape certain characters e.g. ! should be \!

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Optionally provide the name and path of file in which the outputs are to be saved.
```

### AzureList search

Filter files in a container (or containers) in Azure storage

#### AzureList search required arguments
- account name

#### AzureList search optional arguments
- container_name: name of the Azure storage container. Regular expressions are supported. Note that since the regular expression is being entered on the command line, you may need to escape certain characters e.g. ! should be \\!
- expression: expression to use to filter the containers. Regular expressions are supported. Note that since the regular expression is being entered on the command line, you may need to escape certain characters e.g. ! should be \\!
- output_file: name and path of file in which the outputs are to be saved.
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### AzureList search example commands

These commands will use `account_name` as the name of the storage account. Note that all the regex examples used in [`AzureList container`](#azurelist-container-example-commands) can be used here

To list all files in all containers in your storage account

`AzureList search -a account_name`

To list all files in all containers ending with `.gz`

`AzureList search -a account_name *.gz`

To list all files in the container `container-name`

`AzureList search -a account_name -c container_name`

To list all files in the container `container-name` starting with `reports`

`AzureList search -a account_name -c container_name reports*`

To list all files in the container `container-name` ending with `.gz`

`AzureList search -a account_name -c container-name *.gz`

To list all files in the container `container-name` that contain `.gz` 

`AzureList search -a account_name -c container-name *.gz*`

To list all files in the container `container-name` that contain `.gz` (but not at the end)

`AzureList search -a account_name -c container-name *.gz.+`

#### AzureList search usage

```
usage: AzureList search [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-o OUTPUT_FILE]
                        [-c [CONTAINER_NAME]]
                        [expression]

Filter files in a container (or containers) in Azure storage

positional arguments:
  expression            Expression to search. This command supports regular expressions. e.g. 1912* will return all containers starting with 1912, including 191216-dar Note that since the regular expression is being entered on the command line, you may need to escape certain characters e.g. ! should be \!

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Optionally provide the name and path of file in which the outputs are to be saved.
  -c [CONTAINER_NAME], --container_name [CONTAINER_NAME]
                        Name of the Azure storage container. This command supports regular expressions e.g. 1912* will return all containers starting with 1912.Note that since the regular expression is being entered on the command line, you may need to escape certain characters e.g. ! should be \! You can make your queries as complex as you wish: 1912\d{2}-\D{3}\(\?\!*output\) will only return containers that start with 1912, and have two additional digits. If the word output is present, any matches are ignored. There also have to be exactly three letters following a dash and the first six numbers e.g. 191216-dar and 191227-dar will be returned but not 191216-dar-outputs 191202-test, 191216dar, 1912162-dar, 191203-m05722, 191114-gta, or 200105-dar (and many others)
```