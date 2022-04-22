## AzureStorage

[![CircleCI](https://circleci.com/gh/OLC-LOC-Bioinformatics/AzureStorage/tree/main.svg?style=shield)](https://circleci.com/gh/OLC-LOC-Bioinformatics/AzureStorage/tree/main)
[![codecov](https://codecov.io/gh/OLC-LOC-Bioinformatics/AzureStorage/branch/main/graph/badge.svg?token=B65SOEV6QE)](https://codecov.io/gh/OLC-LOC-Bioinformatics/AzureStorage)
[![Anaconda-Server Badge](https://img.shields.io/badge/install%20with-conda-brightgreen)](https://anaconda.org/olcbioinformatics/azure_storage)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/OLC-LOC-Bioinformatics/AzureStorage?label=version)](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/releases/latest)
[![GitHub issues](https://img.shields.io/github/issues/OLC-LOC-Bioinformatics/AzureStorage)](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/issues)
[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=stable)](https://OLC-LOC-Bioinformatics.github.io/AzureStorage/?badge=stable)
[![license](https://img.shields.io/badge/license-MIT-brightgreen)](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/blob/main/LICENSE)

This suite of tools (written in Python) allows you to manipulate containers/files/folders in your Azure storage account.

Full documentation available at the [AzureStorage GitHub pages site](https://OLC-LOC-Bioinformatics.github.io/AzureStorage/)

## Quickstart

Conda is required to install AzureStorage. See the [documentation](http://bioconda.github.io/) or [AzureStorage installation](https://olc-loc-bioinformatics.github.io/AzureStorage/install/) for instructions of getting conda installed on your system

`conda install -c olc-bioinformatics azure-storage`

### Credentials

You must enter your Azure storage connection string and account name into the system keyring before running any of the other scripts

`AzureCredentials store`

### Tests

If you encounter issues with the AzureStorage package, tests are available to ensure that the installation was successful and your credentials are valid.

You will need to clone this repository and run the tests with pytest:


`git clone https://github.com/OLC-LOC-Bioinformatics/AzureStorage.git`

`cd AzureStorage`

`python -m pytest tests/ --cov=azure_storage --cov-config=.coveragec`

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
9. [`AzureList`](https://olc-loc-bioinformatics.github.io/AzureStorage/list/): List and optionally filter containers and/or files in your Azure storage account

## License

MIT License

Copyright (c) 2022 Government of Canada

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
