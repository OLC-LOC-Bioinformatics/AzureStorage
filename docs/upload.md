## AzureUpload

AzureUpload allows you to upload a file or a folder to your Azure storage account.

Choose either the [`file`](#azureupload-file) or [`folder`](#azureupload-folder) functionality

#### General Usage
```
usage: AzureUpload [-h] {file,folder} ...

Upload files or folders to Azure storage

optional arguments:
  -h, --help     show this help message and exit

Available functionality:
  {file,folder}
    file         Upload a file to Azure storage
    folder       Upload a folder to Azure storage
```

### AzureUpload file

Upload a single file to your Azure storage account. 

#### Required arguments:
- container name
- account name
- name and path of file to upload

#### Optional arguments:
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- path to store the file: change the folder structure of the file in Azure storage compared to your local system
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot

#### Example commands:

These commands will use `container-name` as the name of the container, and `account_name` as the name of the storage account

To upload the file `file_name.gz` in your current working directory:

`AzureUpload file -a account_name -c container-name -f file_name.gz`

To upload the file `file_name.gz` in your current working directory and set the storage tier to `Cool`:

`AzureUpload file -a account_name -c container-name -f file_name.gz -s Cool`

To upload the file `file_name.gz` nested in the folder `outputs` in your current working directory:

`AzureUpload file -a account_name -c container-name -f outputs/file_name.gz`

To upload the file `file_name.gz` nested in the folder `outputs` in your current working directory to the root of the container:

`AzureUpload file -a account_name -c container-name -f outputs/file_name.gz -r ""`

To upload the file `file_name.gz` nested in the folder `outputs` in your current working directory to the folder `results/parsing` in the container:

`AzureUpload file -a account_name -c container-name -f outputs/file_name.gz -r results/parsing`

To upload the file `/home/users/account/files/file_name.gz` to path `data`:

`AzureUpload file -a account_name -c container-name -f /home/users/account/files/file_name.gz -r data`

To upload that same file to the root of the container:

`AzureUpload file -a account_name -c container-name -f /home/users/account/files/file_name.gz -r ""`

To retain the path of the file:

`AzureUpload file -a account_name -c container-name -f /home/users/account/files/file_name.gz`

#### Usage

```
usage: AzureUpload file [-h] -c CONTAINER_NAME -a ACCOUNT_NAME
                        [-v {debug,info,warning,error,critical}] [-r RESET_PATH]
                        [-s {Hot,Cool,Archive}] -f FILE

Upload a file to Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                         Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v {debug,info,warning,error,critical}, --verbosity {debug,info,warning,error,critical}
                        Set the logging level. Default is info.
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use "" or ''
  -s {Hot,Cool,Archive}, --storage_tier {Hot,Cool,Archive}
                        Set the storage tier for the file/folder to be uploaded. Options are "Hot", "Cool", and "Archive". Default is Hot
  -f FILE, --file FILE  Name and path of the file to upload to Azure storage.e.g. /mnt/sequences/220202_M05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz
```

### AzureUpload folder

Upload a single folder (and its contents) to your Azure storage account. Note that having a trailing slash ('/') at the end of your folder name will not affect the script

#### Required arguments:
- container name
- account name
- name and path of folder to upload

#### Optional arguments:
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info
- path to store the file: change the folder structure of the file in Azure storage compared to your local system
- storage tier: set the storage tier of the file in Azure storage. Options are Hot, Cool, Archive. Default is Hot

#### Example commands:

These commands will use `container-name` as the name of the container, and `account_name` as the name of the storage account

To upload the folder `folder_name` in your current working directory:

`AzureUpload folder -a account_name -c container-name -f folder_name`

To upload the folder `folder_name` in your current working directory and set the storage tier to `Cool`:

`AzureUpload folder -a account_name -c container-name -f folder_name -s Cool`

To upload the folder `folder_name` nested in the folder `outputs` in your current working directory:

`AzureUpload folder -a account_name -c container-name -f outputs/folder_name`

To upload the folder `folder_name` nested in the folder `outputs` in your current working directory to the root of the container:

`AzureUpload folder -a account_name -c container-name -f outputs/file_name.gz -r ""`

To upload the folder `folder_name` nested in the folder `outputs` in your current working directory to the folder `results/parsing` in the container:

`AzureUpload folder -a account_name -c container-name -f outputs/folder_namw -r results/parsing`

To upload the folder `/home/users/account/files/` to path `data`:

`AzureUpload folder -a account_name -c container-name -f /home/users/account/files/ -r data`

To upload that same folder to the root of the container:

`AzureUpload folder -a account_name -c container-name -f /home/users/account/files -r ""`

To retain the path of the folder:

`AzureUpload folder -a account_name -c container-name -f /home/users/account/files/`


#### Usage

```
usage: AzureUpload folder [-h] -c CONTAINER_NAME -a ACCOUNT_NAME
                          [-v {debug,info,warning,error,critical}] [-r RESET_PATH]
                          [-s {Hot,Cool,Archive}] -f FOLDER

Upload a folder to Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -c CONTAINER_NAME, --container_name CONTAINER_NAME
                         Name of the Azure storage container. Note that container names must be lowercase, between 3 and 63 characters, start with a letter or number, and can contain only letters, numbers, and the dash (-) character. Consecutive dashes are not permitted.
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -v {debug,info,warning,error,critical}, --verbosity {debug,info,warning,error,critical}
                        Set the logging level. Default is info.
  -r RESET_PATH, --reset_path RESET_PATH
                        Set the path of the file/folder within a folder in the target container e.g. sequence_data/220202-m05722. If you want to place it directly in the container without any nesting, use "" or ''
  -s {Hot,Cool,Archive}, --storage_tier {Hot,Cool,Archive}
                        Set the storage tier for the file/folder to be uploaded. Options are "Hot", "Cool", and "Archive". Default is Hot
  -f FOLDER, --folder FOLDER
                        Name and path of the folder to upload to Azure storage.e.g. /mnt/sequences/220202_M05722/

```