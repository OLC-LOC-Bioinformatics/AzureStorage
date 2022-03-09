## AzureSAS

Create shared access signatures (SAS) URLs for containers, files, folders in your Azure storage account.

Note that each file in a container/folder has to be downloaded separately, so if there are 1000 files in the container, 1000 SAS URLs will be provided

Choose either the [`container`](#azuresas-container), [`file`](#azuresas-file), or  [`folder`](#azuresas-folder) functionality

#### General usage

```
usage: AzureSAS [-h] {container,file,folder} ...

Create shared access signatures (SAS) for containers/files/folders from Azure storage.
Note that each file in the container/folder has to be downloaded separately, so if
there are 1000 files in the container, 1000 SAS will be provided

optional arguments:
  -h, --help            show this help message and exit

Available functionality:
  {container,file,folder}
    container           Create SAS for all files in a container in Azure storage
    file                Create a SAS for a file in Azure storage
    folder              Create SAS for all files in a folder in Azure storage
```

### AzureSAS container

Create SAS URLs for all files in a container in your Azure storage account

#### Required arguments:
- container name
- account name

#### Optional arguments:
- output file: file in which the SAS URLs are to be written. Default is `sas.txt` in your current working directory
- expiry: the number of days the SAS URL with be valid. Minimum is 1, maximum is 365. Default is 10
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container, and `account_name` as the name of the storage account

To create SAS URLs with default settings:

`Azure SAS container -a account_name -c container-name`

To create SAS URLs with an expiry of 15 days:

`Azure SAS container -a account_name -c container-name -e 15`

To create SAS URLs, and save them to the file `sas_urls.txt` in your current working directory:

`Azure SAS container -a account_name -c container-name -o sas_urls.txt`

To create SAS URLs, and save them to the file `sas_urls.txt` nested in folder `outputs` in your current working directory:

`Azure SAS container -a account_name -c container-name -o outputs/sas_urls.txt`

#### Usage
```
usage: AzureSAS container [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-e EXPIRY] [-o OUTPUT_FILE]

Create SAS URLs for all files in a container in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -e EXPIRY, --expiry EXPIRY
                        The number of days that the SAS URL will be valid. The minimum is 1, and the maximum is 365. The default is 10.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Name and path of file in which the SAS URLs are to be saved. Default is $CWD/sas.txt
```

### AzureSAS file

Create a SAS URL for a file in a container in your Azure storage account

#### Required arguments:
- container name
- account name
- file name

#### Optional arguments:
- output file: file in which the SAS URLs are to be written. Default is `sas.txt` in your current working directory
- expiry: the number of days the SAS URL with be valid. Minimum is 1, maximum is 365. Default is 10
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container, and `account_name` as the name of the storage account

To create a SAS URL for file `file_name.gz` with default settings:

`Azure SAS file -a account_name -c container-name -f file_name.gz`

To create a SAS URL for file `file_name.gz` nested in folder `outputs` with default settings:

`Azure SAS file -a account_name -c container-name -f outputs/file_name.gz`

To create a SAS URL for file `file_name.gz` with an expiry of 15 days:

`Azure SAS file -a account_name -c container-name f file_name.gz -e 15`

To create a SAS URL for file `file_name.gz`, and save it to the file `sas_urls.txt` in your current working directory:

`Azure SAS file -a account_name -c container-name -f file_name.gz -o sas_urls.txt`

To create a SAS URL for file `file_name.gz`, and save it to the file `sas_urls.txt` nested in folder `outputs` in your current working directory:

`Azure SAS file -a account_name -c container-name -f file_name.gz -o outputs/sas_urls.txt`

#### Usage

```
usage: AzureSAS file [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-e EXPIRY] [-o OUTPUT_FILE] -f FILE

Create a SAS URL for a file in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -e EXPIRY, --expiry EXPIRY
                        The number of days that the SAS URL will be valid. The minimum is 1, and the maximum is 365. The default is 10.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Name and path of file in which the SAS URLs are to be saved. Default is $CWD/sas.txt
  -f FILE, --file FILE  Path of file in Azure storage from which a SAS URL is to be created. e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz
```

### AzureSAS folder

Create SAS URLs for all files in a folder in your Azure storage account

#### Required arguments:
- container name
- account name
- folder name

#### Optional arguments:
- output file: file in which the SAS URLs are to be written. Default is `sas.txt` in your current working directory
- expiry: the number of days the SAS URL with be valid. Minimum is 1, maximum is 365. Default is 10
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container, and `account_name` as the name of the storage account

To create SAS URLs for all files in folder `folder_name` with default settings:

`Azure SAS folder -a account_name -c container-name -f folder_name`

To create SAS URLs for all files in folder `folder_name` nested in folder `outputs` with default settings:

`Azure SAS folder -a account_name -c container-name -f outputs/folder_name`

To create SAS URLs for all files in folder `folder_name` with an expiry of 15 days:

`Azure SAS folder -a account_name -c container-name f folder_name -e 15`

To create SAS URLs for all files in folder `folder_name`, and save them to the file `sas_urls.txt` in your current working directory:

`Azure SAS folder -a account_name -c container-name -f folder_name -o sas_urls.txt`

To create SAS URLs for all files in folder `folder_name`, and save them to the file `sas_urls.txt` nested in folder `outputs` in your current working directory:

`Azure SAS folder -a account_name -c container-name -f folder_name -o outputs/sas_urls.txt`


#### Usage

```
usage: AzureSAS folder [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-e EXPIRY] [-o OUTPUT_FILE] -f FOLDER

Create SAS URLs for all files in a folder in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -e EXPIRY, --expiry EXPIRY
                        The number of days that the SAS URL will be valid. The minimum is 1, and the maximum is 365. The default is 10.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Name and path of file in which the SAS URLs are to be saved. Default is $CWD/sas.txt
  -f FOLDER, --folder FOLDER
                        Name of the folder for which SAS URLs are to be created for all files. e.g. InterOp
```