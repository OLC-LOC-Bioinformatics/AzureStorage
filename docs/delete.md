## AzureDelete

Delete containers, files, or folders from your Azure storage account

Choose either the [`container`](#azuredelete-container), [`file`](#azuredelete-file), or  [`folder`](#azuredelete-folder) functionality

#### General usage

```
usage: AzureDelete [-h] {container,file,folder} ...

Move and/or delete containers, files, or folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Available functionality:
  {container,file,folder}
    container           Delete a container in Azure storage
    file                Delete a file in Azure storage
    folder              Delete a folder in Azure storage
```

### AzureDelete container

Delete a container from your Azure storage account

#### Required arguments:
- container name
- account name

#### Optional arguments:
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example command:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To delete a container from your Azure storage account

`AzureDelete container -a account_name -c container-name`

#### Usage

```
usage: AzureDelete container [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-v VERBOSITY]

Delete a container in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
```

### AzureDelete file

Delete a file from your Azure storage account

#### Required arguments:
- container name
- account name
- file name

#### Optional arguments:
- retention time: time to retain deleted files. Default is 8 days
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To delete the file `file_name.gz` from your Azure storage account

`AzureDelete file -a account_name -c container-name -f file_name.gz`

To delete the file `file_name.gz` nested in folder outputs from your Azure storage account, and retain it for 10 days

`AzureDelete file -a account_name -c container-name -f outputs/file_name.gz -r 10`

#### Usage

```
usage: AzureDelete file [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-v VERBOSITY] -f FILE [-r RETENTION_TIME]

Delete a file in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -f FILE, --file FILE  Name of blob file to delete in Azure storage. e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz
  -r RETENTION_TIME, --retention_time RETENTION_TIME
                        Retention time for deleted files. Default is 8 days. Must be between 1 and 365
```

### AzureDelete folder

Delete a folder from your Azure storage account

#### Required arguments:
- container name
- account name
- folder name

#### Optional arguments:
- retention time: time to retain deleted files in the folder. Default is 8 days
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example commands:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To delete the folder `folder_name` from your Azure storage account

`AzureDelete folder -a account_name -c container-name -f folder_name`

To delete the folder `folder_name` nested in folder outputs from your Azure storage account, and retain it for 10 days

`AzureDelete folder -a account_name -c container-name -f outputs/folder_name -r 10`

#### Usage

```
usage: AzureDelete folder [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-v VERBOSITY] -f FOLDER [-r RETENTION_TIME]

Delete a folder in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -f FOLDER, --folder FOLDER
                        Name of folder to delete in Azure storage. e.g. InterOp
  -r RETENTION_TIME, --retention_time RETENTION_TIME
                        Retention time for deleted files. Default is 8 days
```