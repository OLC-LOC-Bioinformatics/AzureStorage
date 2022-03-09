## AzureMove

Move containers, files, or folders within your Azure storage account.

Choose either the [`container`](#azuremove-container), [`file`](#azuremove-file), or  [`folder`](#azuremove-folder) functionality

#### General usage

```
usage: AzureMove [-h] {container,file,folder} ...

Move containers, files, or folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Available functionality:
  {container,file,folder}
    container           Move a container in Azure storage
    file                Move a file within Azure storage 
    folder              Move a folder within Azure storage

```

### AzureMove container

Move a container within your Azure storage account

#### Required arguments:
- container name
- account name

#### Optional arguments:
- target container: name of the container into which the container is to be moved
- path to store the container: nest the container within the target container
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot

#### Example commands:

These commands will use `container-name` as the name of the container, `target-container` as the name of the target container, and `account_name` as the name of the storage account

To perform a basic move (this also renames a container):

`AzureMove container -a account_name -c container-name -t target-container`

To move a container, and set the storage tier to `Cool`

`AzureMove container -a account_name -c container-name -t target-container -s Cool`

To move a container and nest it into folder `outputs`:

`AzureMove container -a account_name -c container-name -t target-container -r outputs`


#### Usage

```
usage: AzureMove container [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -t TARGET_CONTAINER [-r RESET_PATH]
                           [-s STORAGE_TIER]

Move a container in Azure storage

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
  -t TARGET_CONTAINER, --target_container TARGET_CONTAINER
                        The target container to which the container/file/folder is to be moved (this can be the same as the container_name if you want to move a file/folder within a container
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the container/file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use or ''
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for the container/file/folder to be moved. Options are "Hot", "Cool", and "Archive". Default is Hot
```

### AzureMove file

Move a file within your Azure storage account

#### Required arguments:
- container name
- account name
- file name

#### Optional arguments:
- target container: name of the container into which the container is to be moved
- path to store the container: nest the container within the target container
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot

#### Example commands:

These commands will use `container-name` as the name of the container, `target-container` as the name of the target container, and `account_name` as the name of the storage account

To move the file `file_name.gz`

`AzureMove file -a account_name -c container-name -t target-container -f file_name.gz`

To move the file `file_name.gz`, and set the storage tier to `Cool`

`AzureMove file -a account_name -c container-name -t target-container -f file_name.gz -s Cool`

To move the file `file_name.gz` nested in folder `outputs`

`AzureMove file -a account_name -c container-name -t target-container -f outputs/file_name.gz`

To move the file `file_name.gz` nested in folder `outputs` to the root of the source container

`AzureMove file -a account_name -c container-name -t container-name -f outputs/file_name.gz -r ""`

To move the file `file_name.gz` nested in folder `outputs` to folder `results` in the source container

`AzureMove file -a account_name -c container-name -t container-name -f outputs/file_name.gz -r results`

To move the file `file_name.gz` nested in folder `outputs` to the root of the target container

`AzureMove file -a account_name -c container-name -t target-container -f outputs/file_name.gz -r ""`

To move the file `file_name.gz` nested in folder `outputs` to folder `results` in the target container

`AzureMove file -a account_name -c container-name -t target-container -f outputs/file_name.gz -r results`

#### Usage

```
usage: AzureMove file [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -t TARGET_CONTAINER [-r RESET_PATH]
                      [-s STORAGE_TIER] -f FILE

Move a file within Azure storage

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
  -t TARGET_CONTAINER, --target_container TARGET_CONTAINER
                        The target container to which the container/file/folder is to be moved (this can be the same as the container_name if you want to move a file/folder within a container
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the container/file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use or ''
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for the container/file/folder to be moved. Options are "Hot", "Cool", and "Archive". Default is Hot
  -f FILE, --file FILE  Name of blob file to move in Azure storage. e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz
```

### AzureMove folder

Move a folder within your Azure storage account

#### Required arguments:
- container name
- account name
- folder name

#### Optional arguments:
- target container: name of the container into which the container is to be moved
- path to store the container: nest the container within the target container
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot

#### Example commands:

These commands will use `container-name` as the name of the container, `target-container` as the name of the target container, and `account_name` as the name of the storage account

To move the folder `folder_name`

`AzureMove folder -a account_name -c container-name -t target-container -f folder_name`

To move the folder `folder_name`, and set the storage tier to `Cool`

`AzureMove folder -a account_name -c container-name -t target-container -f folder_name -s Cool`

To move the folder `folder_name` nested in folder `outputs`

`AzureMove folder -a account_name -c container-name -t target-container -f outputs/folder_name`

To move the folder `folder_name` nested in folder `outputs` to the root of the source container

`AzureMove folder -a account_name -c container-name -t container-name -f outputs/folder_name -r ""`

To move the folder `folder_name` nested in folder `outputs` to folder `results` in the source container

`AzureMove folder -a account_name -c container-name -t container-name -f outputs/folder_name -r results`

To move the folder `folder_name` nested in folder `outputs` to the root of the target container

`AzureMove folder -a account_name -c container-name -t target-container -f outputs/folder_name -r ""`

To move the folder `folder_name` nested in folder `outputs` to folder `results` in the target container

`AzureMove folder -a account_name -c container-name -t target-container -f outputs/folder_name -r results`

#### Usage

```
usage: AzureMove folder [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -t TARGET_CONTAINER [-r RESET_PATH]
                        [-s STORAGE_TIER] -f FOLDER

Move a folder within Azure storage

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
  -t TARGET_CONTAINER, --target_container TARGET_CONTAINER
                        The target container to which the container/file/folder is to be moved (this can be the same as the container_name if you want to move a file/folder within a container
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the container/file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use or ''
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for the container/file/folder to be moved. Options are "Hot", "Cool", and "Archive". Default is Hot
  -f FOLDER, --folder FOLDER
                        Name of folder to move in Azure storage. e.g. InterOp
```