## AzureStorage
This suite of tools (written in Python) allows you to manipulate containers/files/folders in your Azure storage account.

Full documentation available at the [AzureStorage Github pages site]( https://OLC-LOC-Bioinformatics.github.io/AzureStorage/)

## Quickstart

Conda is required to install AzureStorage see the [documentation](http://bioconda.github.io/) or [AzureStorage installation](https://olc-loc-bioinformatics.github.io/AzureStorage/install/) for instructions of getting conda installed on your system

`conda install -c olc-bioinformatics azure-storage`

### Credentials

You must enter your Azure storage connection string and account name into the system keyring before running any of the other scripts

`AzureCredentials store`

### Tests

The AzureStorage package comes with unit tests to ensure that the installation and provided credentials are valid

`python -m pytest tests/`

Ensure that all tests complete successfully before proceeding

## Scripts

1. [`AzureCredentials`](https://olc-loc-bioinformatics.github.io/AzureStorage/credentials/): enter, modify, or delete your Azure connection string and account name in your system keyring
2. [`AzureUpload`](https://olc-loc-bioinformatics.github.io/AzureStorage/upload/): upload a file or folder to a container in your Azure storage account
3. [`AzureSAS`](https://olc-loc-bioinformatics.github.io/AzureStorage/sas_url/): create SAS (shared access signature) URLs for a file, a folder, or an entire container in your Azure storage account
4. [`AzureMove`](https://olc-loc-bioinformatics.github.io/AzureStorage/move/): move a file, folder, or an entire container within your Azure storage account
5. [`AzureDownload`](https://olc-loc-bioinformatics.github.io/AzureStorage/download/): download a file, folder, or an entire container from your Azure storage account
6. [`AzureTier`](https://olc-loc-bioinformatics.github.io/AzureStorage/set_tier/): set the storage tier of a file, folder, or an entire container from your Azure storage account
7. [`AzureDelete`](https://olc-loc-bioinformatics.github.io/AzureStorage/delete/): delete a file, folder, or an entire container from your Azure storage account
8. [`AzureAutomate`](https://olc-loc-bioinformatics.github.io/AzureStorage/automate/): run upload, sas, move, download, set_tier, and/or delete in batch

## License

MIT License

Copyright (c) 2022 Government of Canada

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.