## AzureTier

Set the storage tier (`Hot`, `Cool`, or `Archive`) for containers, files, or folders in your Azure storage account

Choose either the [`container`](#azuretier-container), [`file`](#azuretier-file), or  [`folder`](#azuretier-folder) functionality

#### General usage

```
usage: AzureTier [-h] {container,file,folder} ...

Set the storage tier of containers/files/folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Available functionality:
  {container,file,folder}
    container           Change the storage tier of a container in Azure storage
    file                Change the storage tier of a file in Azure storage
    folder              Change the storage tier of a folder in Azure storage
```

### AzureTier container

Set the storage tier of a container in your Azure storage account

#### Required arguments:
- container name
- account name
- storage tier

#### Optional arguments:
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example command:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To change the storage tier of a container to `Cool`

`AzureTier -a account_name -c container-name -s Cool`

#### Usage

```
usage: AzureTier container [-h] -c CONTAINER_NAME -a ACCOUNT_NAME
                           [-v VERBOSITY] -s STORAGE_TIER

Change the storage tier of a container in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for a container/file/folder. Options are "Hot", "Cool", and "Archive"
```

### AzureTier file

Set the storage tier of a file in your Azure storage account

#### Required arguments:
- container name
- account name
- file name
- storage tier

#### Optional arguments:
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example command:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To change the storage tier of the file `file_name.gz` to `Archive`

`AzureTier -a account_name -c container-name -f file_name.gz -s Archive`

#### Usage

```
usage: AzureTier file [-h] -c CONTAINER_NAME -a ACCOUNT_NAME
                      [-v VERBOSITY] -s STORAGE_TIER -f FILE

Change the storage tier of a file in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for a container/file/folder. Options are "Hot", "Cool", and "Archive"
  -f FILE, --file FILE  Name of file in Azure storage that will have its storage tier sete.g. 220202-m05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz
```

### AzureTier folder

Set the storage tier of a folder in your Azure storage account

#### Required arguments:
- container name
- account name
- folder name
- storage tier

#### Optional arguments:
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Example command:

These commands will use `container-name` as the name of the container and `account_name` as the name of the storage account

To change the storage tier of the folder `results/folder_name` to `Hot`

`AzureTier -a account_name -c container-name -f results/folder_name -s Hot`

#### Usage

```
usage: AzureTier folder [-h] -c CONTAINER_NAME -a ACCOUNT_NAME
                        [-v VERBOSITY] -s STORAGE_TIER -f FOLDER

Change the storage tier of a folder in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for a container/file/folder. Options are "Hot", "Cool", and "Archive"
  -f FOLDER, --folder FOLDER
                        Name of the folder in Azure storage that will have its storage tier set e.g. InterOp
```