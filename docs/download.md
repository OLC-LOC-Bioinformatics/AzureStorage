## AzureDownload

Download containers, files, or folder from your Azure storage account

Choose either the [`container`](#azuredownload-container), [`file`](#azuredownload-file), or  [`folder`](#azuredownload-folder) functionality

#### General usage

```
usage: AzureDownload [-h] {container,file,folder} ...

Download containers/files/folders from Azure storage

optional arguments:
  -h, --help            show this help message and exit

Available functionality:
  {container,file,folder}
    container           Download a container from Azure storage
    file                Download a file from Azure storage
    folder              Download a folder from Azure storage
```


### AzureDownload container

Download a container from your Azure storage account

#### Required arguments:
- container name
- account name

#### Optional arguments:
- output path: local path where container is to be saved. Default is your current working directory
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To perform a basic container download (download to your current working directory)

`AzureDownload container -a account name -c container-name`

To download a container to the folder `outputs` in your current working directory

`AzureDownload container -a account name -c container-name -o outputs`

To download a container to the folder `/home/users/outputs` 

`AzureDownload container -a account name -c container-name -o /home/users/outputs`

#### Usage

```
usage: AzureDownload container [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-o OUTPUT_PATH]

Download a container from Azure storage

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
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Name and path of directory in which the outputs are to be saved. Default is your $CWD
```

### AzureDownload file

Download a file from your Azure storage account

#### Required arguments:
- container name
- account name
- file name

#### Optional arguments:
- output path: local path where container is to be saved. Default is your current working directory
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To download the file `file_name.gz` to your current working directory

`AzureDownload file -a account name -c container-name -f file_name.gz`

To download the file `file_name.gz` nested in the `outputs` folder to your current working directory

`AzureDownload file -a account name -c container-name -f outputs/file_name.gz`

To download the file `file_name.gz` nested in the `outputs` folder to the folder `files` in your current working directory

`AzureDownload file -a account name -c container-name -f outputs/file_name.gz -o files`

To download the file `file_name.gz` to the folder `/home/users/outputs` 

`AzureDownload file -a account name -c container-name -f file_name.gz -o /home/users/outputs`


#### Usage

```
usage: AzureDownload file [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-o OUTPUT_PATH] -f FILE

Download a file from Azure storage

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
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Name and path of directory in which the outputs are to be saved. Default is your $CWD
  -f FILE, --file FILE  Name of file to download from Azure storage.e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz
```

### AzureDownload folder

Download a folder from your Azure storage account

#### Required arguments:
- container name
- account name
- folder name

#### Optional arguments:
- output path: local path where container is to be saved. Default is your current working directory
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To download the folder `folder_name` to your current working directory

`AzureDownload folder -a account name -c container-name -f folder_name`

To download the folder `folder_name` nested in the `outputs` folder to your current working directory

`AzureDownload folder -a account name -c container-name -f outputs/folder_name`

To download the folder `folder_name` nested in the `outputs` folder to the folder `folders` in your current working directory

`AzureDownload folder -a account name -c container-name -f outputs/folder_name -o folders`

To download the folder `folder_name` to the folder `/home/users/outputs` 

`AzureDownload folder -a account name -c container-name -f folder_name -o /home/users/outputs`

#### Usage 

```
usage: AzureDownload folder [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] [-o OUTPUT_PATH] -f FOLDER

Download a folder from Azure storage

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
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Name and path of directory in which the outputs are to be saved. Default is your $CWD
  -f FOLDER, --folder FOLDER
                        Name of the folder to download from Azure storage e.g. InterOp
```