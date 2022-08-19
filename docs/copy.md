## AzureCopy

Copy containers, files, or folders within your Azure storage account.

Choose either the [`container`](#azurecopy-container), [`file`](#azurecopy-file), or  [`folder`](#azurecopy-folder) functionality

#### General usage

```
usage: AzureCopy [-h] {container,file,folder} ...

Copy containers, files, or folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Available functionality:
  {container,file,folder}
    container           Copy a container in Azure storage
    file                Copy a file within Azure storage 
    folder              Copy a folder within Azure storage

```

### AzureCopy container

Copy a container within your Azure storage account

#### Required arguments:
- container name
- account name

#### Optional arguments:
- target container: name of the container into which the container is to be copied
- path to store the container: nest the container within the target container
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot

#### Example commands:

These commands will use `container-name` as the name of the container, `target-container` as the name of the target container, and `account_name` as the name of the storage account

To perform a basic copy:

`AzureCopy container -a account_name -c container-name -t target-container`

To copy a container, and set the storage tier to `Cool`

`AzureCopy container -a account_name -c container-name -t target-container -s Cool`

To copy a container and nest it into folder `outputs`:

`AzureCopy container -a account_name -c container-name -t target-container -r outputs`


#### Usage

```
usage: AzureCopy container [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-v VERBOSITY] -t TARGET_CONTAINER [-r RESET_PATH]
                           [-s STORAGE_TIER]

Copy a container in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -t TARGET_CONTAINER, --target_container TARGET_CONTAINER
                        The target container to which the container/file/folder is to be copyd (this can be the same as the container_name if you want to copy a file/folder within a container
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the container/file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use or ''
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for the container/file/folder to be copyd. Options are "Hot", "Cool", and "Archive". Default is Hot
```

### AzureCopy file

Copy a file within your Azure storage account

#### Required arguments:
- container name
- account name
- file name

#### Optional arguments:
- target container: name of the container into which the container is to be copied (can be the same as `container name`)
- path to store the container: nest the container within the target container
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot
- name: set the name of the copied file

#### Example commands:

These commands will use `container-name` as the name of the container, `target-container` as the name of the target container, and `account_name` as the name of the storage account

To copy the file `file_name.gz`

`AzureCopy file -a account_name -c container-name -t target-container -f file_name.gz`

To copy the file `file_name.gz` and rename it `copy.gz`

`AzureCopy file -a account_name -c container-name -t target-container -f file_name.gz -n copy.gz`

To copy the file `file_name.gz`, and set the storage tier to `Cool`

`AzureCopy file -a account_name -c container-name -t target-container -f file_name.gz -s Cool`

To copy the file `file_name.gz` nested in folder `outputs` (will remain nested in `outputs` in `target-container`)

`AzureCopy file -a account_name -c container-name -t target-container -f outputs/file_name.gz`

To copy the file `file_name.gz` nested in folder `outputs` and rename it `copy.gz` (will remain nested in `outputs` in `target-container`)

`AzureCopy file -a account_name -c container-name -t target-container -f outputs/file_name.gz` -n `copy.gz`

To copy the file `file_name.gz` nested in folder `outputs` to the root of the source container

`AzureCopy file -a account_name -c container-name -t container-name -f outputs/file_name.gz -r ""`

To copy the file `file_name.gz` nested in folder `outputs` to the root of the source container and rename it `copy.gz`

`AzureCopy file -a account_name -c container-name -t container-name -f outputs/file_name.gz -r "" -n copy.gz`

To copy the file `file_name.gz` nested in folder `outputs` to folder `results` in the source container

`AzureCopy file -a account_name -c container-name -t container-name -f outputs/file_name.gz -r results`

To copy the file `file_name.gz` nested in folder `outputs` to folder `results` in the source container and rename it `copy.gz

`AzureCopy file -a account_name -c container-name -t container-name -f outputs/file_name.gz -r results -n copy.gz`

To copy the file `file_name.gz` nested in folder `outputs` to the root of the target container

`AzureCopy file -a account_name -c container-name -t target-container -f outputs/file_name.gz -r ""`

To copy the file `file_name.gz` nested in folder `outputs` to folder `results` in the target container

`AzureCopy file -a account_name -c container-name -t target-container -f outputs/file_name.gz -r results`

#### Usage

```
usage: AzureCopy file [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-v VERBOSITY] -t TARGET_CONTAINER [-r RESET_PATH]
                      [-s STORAGE_TIER] -f FILE

Copy a file within Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -t TARGET_CONTAINER, --target_container TARGET_CONTAINER
                        The target container to which the container/file/folder is to be copyd (this can be the same as the container_name if you want to copy a file/folder within a container
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the container/file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use or ''
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for the container/file/folder to be copyd. Options are "Hot", "Cool", and "Archive". Default is Hot
  -f FILE, --file FILE  Name of blob file to copy in Azure storage. e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz
  -n NAME, --name NAME  Name of duplicate file. Required if copying within the same container (and folder). Otherwise, the original name will be used.
```

### AzureCopy folder

Copy a folder within your Azure storage account

#### Required arguments:
- container name
- account name
- folder name

#### Optional arguments:
- target container: name of the container into which the container is to be copyd
- path to store the container: nest the container within the target container
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot

#### Example commands:

These commands will use `container-name` as the name of the container, `target-container` as the name of the target container, and `account_name` as the name of the storage account

To copy the folder `folder_name`

`AzureCopy folder -a account_name -c container-name -t target-container -f folder_name`

To copy the folder `folder_name`, and set the storage tier to `Cool`

`AzureCopy folder -a account_name -c container-name -t target-container -f folder_name -s Cool`

To copy the folder `folder_name` nested in folder `outputs`

`AzureCopy folder -a account_name -c container-name -t target-container -f outputs/folder_name`

To copy the folder `folder_name` nested in folder `outputs` to the root of the source container

`AzureCopy folder -a account_name -c container-name -t container-name -f outputs/folder_name -r ""`

To copy the folder `folder_name` nested in folder `outputs` to folder `results` in the source container

`AzureCopy folder -a account_name -c container-name -t container-name -f outputs/folder_name -r results`

To copy the folder `folder_name` nested in folder `outputs` to the root of the target container

`AzureCopy folder -a account_name -c container-name -t target-container -f outputs/folder_name -r ""`

To copy the folder `folder_name` nested in folder `outputs` to folder `results` in the target container

`AzureCopy folder -a account_name -c container-name -t target-container -f outputs/folder_name -r results`

#### Usage

```
usage: AzureCopy folder [-h] -c CONTAINER_NAME -a ACCOUNT_NAME [-v VERBOSITY] -t TARGET_CONTAINER [-r RESET_PATH]
                        [-s STORAGE_TIER] -f FOLDER

Copy a folder within Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                        Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -t TARGET_CONTAINER, --target_container TARGET_CONTAINER
                        The target container to which the container/file/folder is to be copyd (this can be the same as the container_name if you want to copy a file/folder within a container
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the container/file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use or ''
  -s STORAGE_TIER, --storage_tier STORAGE_TIER
                        Set the storage tier for the container/file/folder to be copyd. Options are "Hot", "Cool", and "Archive". Default is Hot
  -f FOLDER, --folder FOLDER
                        Name of folder to copy in Azure storage. e.g. InterOp
```