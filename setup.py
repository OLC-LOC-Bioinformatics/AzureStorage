#!/usr/bin/env python
from setuptools import setup, find_packages
from distutils.util import convert_path
import os
__author__ = 'adamkoziol'

# Find the version
version = dict()
with open(convert_path(os.path.join('azure_storage', 'version.py')), 'r') as version_file:
    exec(version_file.read(), version)
setup(
    name="AzureStorage",
    version=version['__version__'],
    entry_points={
        'console_scripts': [
            'AzureCredentials = azure_storage.azure_credentials:cli',
            'AzureAutomate = azure_storage.azure_automate:cli',
            'AzureDownload = azure_storage.azure_download:cli',
            'AzureDelete = azure_storage.azure_delete:cli',
            'AzureUpload = azure_storage.azure_upload:cli',
            'AzureCopy = azure_storage.azure_copy:cli',
            'AzureList = azure_storage.azure_list:cli',
            'AzureMove = azure_storage.azure_move:cli',
            'AzureTier = azure_storage.azure_tier:cli',
            'AzureSAS = azure_storage.azure_sas:cli'
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    author="Adam Koziol",
    author_email="adam.koziol@inspection.gc.ca",
    url="https://github.com/OLC-LOC-Bioinformatics/AzureStorage",
)
