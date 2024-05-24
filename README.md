## AzureStorage

[![CircleCI](https://circleci.com/gh/OLC-LOC-Bioinformatics/AzureStorage/tree/main.svg?style=shield)](https://circleci.com/gh/OLC-LOC-Bioinformatics/AzureStorage/tree/main)
[![codecov](https://codecov.io/gh/OLC-LOC-Bioinformatics/AzureStorage/branch/main/graph/badge.svg?token=B65SOEV6QE)](https://codecov.io/gh/OLC-LOC-Bioinformatics/AzureStorage)
[![Anaconda-Server Badge](https://img.shields.io/badge/install%20with-conda-brightgreen)](https://anaconda.org/olcbioinformatics/azure_storage)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/OLC-LOC-Bioinformatics/AzureStorage?label=version)
[![GitHub issues](https://img.shields.io/github/issues/OLC-LOC-Bioinformatics/AzureStorage)](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/issues)
[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=stable)](https://OLC-LOC-Bioinformatics.github.io/AzureStorage/?badge=stable)
[![license](https://img.shields.io/badge/license-MIT-brightgreen)](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/blob/main/LICENSE)

This suite of tools (written in Python) allows you to manipulate containers/files/folders in your Azure storage account.

Full documentation available at the [AzureStorage GitHub pages site](https://OLC-LOC-Bioinformatics.github.io/AzureStorage/)

## Table of Contents

- [Quickstart](#quickstart)
- [Credentials](#credentials)
- [Tests](#tests)
- [Scripts](#scripts)
- [Reporting Issues](#reporting-issues)
- [License](#license)

## Quickstart

Conda is required to install AzureStorage. See the [documentation](http://bioconda.github.io/) or [AzureStorage installation](https://olc-loc-bioinformatics.github.io/AzureStorage/install/) for instructions of getting conda installed on your system

`conda install -c olcbioinformatics azure_storage`

### Credentials

You must store your Azure storage connection string before running any of the other scripts

`AzureCredentials store -a account_name`

### Tests

If you encounter issues with the AzureStorage package, tests are available to ensure that the installation was successful and your credentials are valid.

You will need to clone this repository and run the tests with pytest:

`git clone https://github.com/OLC-LOC-Bioinformatics/AzureStorage.git`

`cd AzureStorage`

`python -m pytest tests/ --cov=azure_storage --cov-config=.coveragec`

Ensure that all tests complete successfully before proceeding

## Scripts

1. [`AzureCredentials`](https://olc-loc-bioinformatics.github.io/AzureStorage/credentials/): store, modify, or delete your Azure connection string
2. [`AzureUpload`](https://olc-loc-bioinformatics.github.io/AzureStorage/upload/): upload a file or folder to a container in your Azure storage account
3. [`AzureSAS`](https://olc-loc-bioinformatics.github.io/AzureStorage/sas_url/): create SAS (shared access signature) URLs for a file, a folder, or an entire container in your Azure storage account
4. [`AzureCopy`](https://olc-loc-bioinformatics.github.io/AzureStorage/copy): copy a file, folder, or an entire container within your Azure storage account
5. [`AzureMove`](https://olc-loc-bioinformatics.github.io/AzureStorage/move/): move a file, folder, or an entire container within your Azure storage account
6. [`AzureDownload`](https://olc-loc-bioinformatics.github.io/AzureStorage/download/): download a file, folder, or an entire container from your Azure storage account
7. [`AzureTier`](https://olc-loc-bioinformatics.github.io/AzureStorage/set_tier/): set the storage tier of a file, folder, or an entire container from your Azure storage account
8. [`AzureList`](https://olc-loc-bioinformatics.github.io/AzureStorage/list/): List and optionally filter containers and/or files in your Azure storage account
9. [`AzureDelete`](https://olc-loc-bioinformatics.github.io/AzureStorage/delete/): delete a file, folder, or an entire container from your Azure storage account
10. [`AzureAutomate`](https://olc-loc-bioinformatics.github.io/AzureStorage/automate/): run upload, sas, move, download, set_tier, and/or delete in batch

## Reporting Issues

If you encounter any issues while using AzureStorage, please report them on our [Issues page](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/issues).

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/blob/main/LICENSE) file for details.