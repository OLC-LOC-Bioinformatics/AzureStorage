## AzureAutomate

Perform multiple upload, SAS URL creation, move, download, storage tier setting, or delete actions. Alternatively, perform multiple actions in a single call

Choose either the [`upload`](#azureautomate-upload), [`sas`](#azureautomate-sas), [`move`](#azureautomate-move), [`download`](#azureautomate-download), [`tier`](#azureautomate-tier), [`delete`](#azureautomate-delete), or [`batch`](#azureautomate-batch) functionality

#### General usage

```
usage: AzureAutomate [-h] {upload,sas,move,download,tier,delete,batch} ...

Automate the submission of multiple AzureStorage commands

optional arguments:
  -h, --help            show this help message and exit

Available functionality:
  {upload,sas,move,download,tier,delete,batch}
    upload              Upload files/folders to Azure storage
    sas                 Create SAS URLs for containers/files/folders in Azure storage
    move                Move containers/files/folders in Azure storage
    download            Download containers/files/folders in Azure storage
    tier                Set the storage tier of containers/files/folders in Azure storage
    delete              Delete containers/files/folders in Azure storage
    batch               Perform multiple different operations in batch
```
### AzureAutomate upload

Choose either the [`file`](#azureautomate-upload-file) or [`folder`](#azureautomate-upload-folder) functionality

#### General usage

```
usage: AzureAutomate upload [-h] {file,folder} ...

Upload files/folders to Azure storage

optional arguments:
  -h, --help     show this help message and exit

Upload functionality:
  {file,folder}
    file         Upload files to Azure storage
    folder       Upload folders to Azure storage
```

### AzureAutomate upload file

Automate the upload of multiple files to your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, file name, destination path (optional), storage tier (optional)`

For additional details on running file uploads, please see the [`AzureUpload file`](upload.md#azureupload-file) section

#### Usage

```
usage: AzureAutomate upload file [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Upload files to Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, file name, destination path (optional), storage tier (optional)
```

### AzureAutomate upload folder

Automate the upload of multiple folders to your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, folder name, destination path (optional), storage tier (optional)`

For additional details on running folder uploads, please see the [`AzureUpload folder`](upload.md#azureupload-folder) section

#### Usage

```
usage: AzureAutomate upload folder [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Upload folders to Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields (one entry per line):
                         container name, folder name, destination path (optional), storage tier (optional)
```

### AzureAutomate sas

Choose either the [`container`](#azureautomate-sas-container), [`file`](#azureautomate-sas-file), or [`folder`](#azureautomate-sas-folder) functionality

#### General usage

```
usage: AzureAutomate sas [-h] {container,file,folder} ...

Create SAS URLs for containers/files/folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

SAS URL creation functionality:
  {container,file,folder}
    container           Create SAS URLs for containers in Azure storage
    file                Create SAS URLs for files in Azure storage
    folder              Create SAS URLs for folders in Azure storage
```

#### AzureAutomate sas container

Automate the creation of SAS URLs for multiple containers in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, expiry (optional), output file (optional)`

For additional details on creating SAS URLs for containers, please see the [`AzureSAS container`](sas_url.md#azuresas-container) section

#### Usage

```
usage: AzureAutomate sas container [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Create SAS URLs for containers in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                        container name, expiry (optional), output file (optional)
```

#### AzureAutomate sas file

Automate the creation of SAS URLs for multiple files in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, file name and path, expiry (optional), output file (optional)`

For additional details on creating SAS URLs for files, please see the [`AzureSAS file`](sas_url.md#azuresas-file) section

#### Usage

```
usage: AzureAutomate sas file [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Create SAS URLs for files in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, file name and path, expiry (optional), output file (optional)
```

#### AzureAutomate sas folder

Automate the creation of SAS URLs for multiple folders in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, folder name and path, expiry (optional), output file (optional)`

For additional details on creating SAS URLs for folders, please see the [`AzureSAS folder`](sas_url.md#azuresas-folder) section

#### Usage

```
usage: AzureAutomate sas folder [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Create SAS URLs for folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, folder name and path, expiry (optional), output file (optional)
```

### AzureAutomate move

Choose either the [`container`](#azureautomate-move-container), [`file`](#azureautomate-move-file), or [`folder`](#azureautomate-move-folder) functionality

#### General usage

```
usage: AzureAutomate move [-h] {container,file,folder} ...

Move containers/files/folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Move functionality:
  {container,file,folder}
    container           Move containers in Azure storage
    file                Move files in Azure storage
    folder              Move folders in Azure storage
```

#### AzureAutomate move container

Automate the moving of multiple containers in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, target container, destination path (optional), storage tier (optional)`

For additional details on moving containers, please see the [`AzureMove container`](move.md#azuremove-container) section

#### Usage

```
usage: AzureAutomate move container [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Move containers in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, target container, destination path (optional), storage tier (optional)
```

#### AzureAutomate move file

Automate the moving of multiple files in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, target container, file name, destination path (optional), storage tier (optional)`

For additional details on moving files, please see the [`AzureMove file`](move.md#azuremove-file) section

#### Usage

```
usage: AzureAutomate move file [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Move files in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, target container, file name, destination path (optional), storage tier (optional)
```

#### AzureAutomate move folder

Automate the moving of multiple folders in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, target container, folder name, destination path (optional), storage tier (optional)`

For additional details on moving folders, please see the [`AzureMove folder`](move.md#azuremove-folder) section

#### Usage

```
usage: AzureAutomate move folder [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Move folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, target container, folder name, destination path (optional), storage tier (optional)

```

### AzureAutomate download

Choose either the [`container`](#azureautomate-download-container), [`file`](#azureautomate-download-file), or [`folder`](#azureautomate-download-folder) functionality

#### General usage

```
usage: AzureAutomate download [-h] {container,file,folder} ...

Download containers/files/folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Download functionality:
  {container,file,folder}
    container           Download containers from Azure storage
    file                Download files from Azure storage
    folder              Download folders from Azure storage
```

### AzureAutomate download container

Automate the downloading of multiple containers from your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, output path (optional)`

For additional details on downloading containers, please see the [`AzureDownload container`](download.md#azuredownload-container) section

#### Usage

```
usage: AzureAutomate download container [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Download containers from Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, output path (optional)
```

### AzureAutomate download file

Automate the downloading of multiple files from your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, file name, output path (optional)`

For additional details on downloading files, please see the [`AzureDownload file`](download.md#azuredownload-file) section

#### Usage

```
usage: AzureAutomate download file [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Download files from Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, file name, output path (optional)
```

### AzureAutomate download folder

Automate the downloading of multiple folders from your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, folder name, output path (optional)`

For additional details on downloading folders, please see the [`AzureDownload folder`](download.md#azuredownload-folder) section

#### Usage

```
usage: AzureAutomate download folder [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Download folders from Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, folder name, output path (optional)
```

### AzureAutomate tier

Choose either the [`container`](#azureautomate-tier-container), [`file`](#azureautomate-tier-file), or [`folder`](#azureautomate-tier-folder) functionality

#### General usage

```
usage: AzureAutomate tier [-h] {container,file,folder} ...

Set the storage tier of containers/files/folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Storage tier setting functionality:
  {container,file,folder}
    container           Set the storage tier of containers in Azure storage
    file                Set the storage tier of files in Azure storage
    folder              Set the storage tier of folders in Azure storage
```

### AzureAutomate tier container

Automate setting the storage tier for multiple containers in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, storage tier`

For additional details on setting the storage tier of containers, please see the [`AzureTier container`](set_tier.md#azuretier-container) section

#### Usage

```
usage: AzureAutomate tier container [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Set the storage tier of containers in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, storage tier

```

### AzureAutomate tier file

Automate setting the storage tier for multiple files in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, file name, storage tier`

For additional details on setting the storage tier of files, please see the [`AzureTier file`](set_tier.md#azuretier-file) section

#### Usage

```
usage: AzureAutomate tier file [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Set the storage tier of files in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, file name, storage tier
```

### AzureAutomate tier folder

Automate setting the storage tier for multiple folders in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, folder name, storage tier`

For additional details on setting the storage tier of folders, please see the [`AzureTier folder`](set_tier.md#azuretier-folder) section

#### Usage

```
usage: AzureAutomate tier folder [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Set the storage tier of folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, folder name, storage tier
```

### AzureAutomate delete

Choose either the [`container`](#azureautomate-delete-container), [`file`](#azureautomate-delete-file), or [`folder`](#azureautomate-delete-folder) functionality

#### General usage

```
usage: AzureAutomate delete [-h] {container,file,folder} ...

Delete containers/files/folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit

Delete functionality:
  {container,file,folder}
    container           Delete containers in Azure storage
    file                Delete files in Azure storage
    folder              Delete folders in Azure storage
```

### AzureAutomate delete container

Automate deleting multiple containers in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

File with the following field:

`container name`

For additional details on deleting containers, please see the [`AzureDelete container`](delete.md#azuredelete-container) section

#### Usage

```
usage: AzureAutomate delete container [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Delete containers in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        File with the following field:
                         container name
```

### AzureAutomate delete file

Automate deleting multiple files in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, file name, retention time (optional)`

For additional details on deleting files, please see the [`AzureDelete file`](delete.md#azuredelete-file) section

#### Usage

```
usage: AzureAutomate delete file [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Delete files in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, file name, retention time (optional)

```

### AzureAutomate delete folder

Automate deleting multiple folders in your Azure storage account

#### Required arguments:
- container name
- account name
- name and path of batch file

#### Optional arguments:
- passphrase used to store your connection string in the system keyring (default is AzureStorage)
- verbosity: set the logging level. Options are debug,info,warning,error,critical. Default is info

#### Batch file format

Tab-separated file with the following fields:

`container name, folder name, retention time (optional)`

For additional details on deleting folders, please see the [`AzureDelete folder`](delete.md#azuredelete-folder) section

#### Usage

```
usage: AzureAutomate delete folder [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Delete folders in Azure storage

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file with the following fields:
                         container name, folder name, retention time (optional)
```

### AzureAutomate batch

Automate multiple operations

### Batch file format

Tab-separated file in the following format:

`command, sub-command, command:subcommand-specific arguments`

Please review the [`AzureAutomate`](#azureautomate) documentation for all the possible operations

### Usage

```
usage: AzureAutomate batch [-h] -a ACCOUNT_NAME [-p PASSPHRASE] [-v VERBOSITY] -b BATCH_FILE

Perform multiple different operations in batch

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT_NAME, --account_name ACCOUNT_NAME
                        Name of the Azure storage account
  -p PASSPHRASE, --passphrase PASSPHRASE
                        The passphrase to use when encrypting the azure storage-specific connection string to the system keyring. Default is "AzureStorage".
  -v VERBOSITY, --verbosity VERBOSITY
                        Set the logging level. Options are debug, info, warning, error, and critical. Default is info.
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Tab-separated file in the following format:
                        command, sub-command, arguments

                        Below is the complete list of functionalities:
                        upload, file, container name, file name, destination path (optional), storage tier (optional)
                        upload, folder, container name, folder name, destination path (optional), storage tier (optional)
                        sas, container, container name, expiry (optional), output file (optional)
                        sas, file, container name, file name and path, expiry (optional), output file (optional)
                        sas, folder, container name, folder name and path, expiry (optional), output file (optional)
                        move, container, container name, target container, destination path (optional), storage tier (optional)
                        move, file, container name, target container, file name, destination path (optional), storage tier (optional)
                        move, folder, container name, target container, folder name, destination path (optional), storage tier (optional)
                        download, container, container name, output path (optional)
                        download, file, container name, file name, output path (optional)
                        download, folder, container name, folder name, output path (optional)
                        tier, container, container name, storage tier
                        tier, file, container name, file name, storage tier
                        tier, folder, container name, folder name, storage tier
                        delete, container, container name
                        delete, file, container name, file name, retention time (optional)
                        delete, folder, container name, folder name, retention time (optional)
```
