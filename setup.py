#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name="AzureStorage",
    version="0.0.1",
    entry_points={
        'console_scripts': [
            'AzureCredentials = azure_storage.azure_credentials:cli',
            'AzureAutomate = azure_storage.azure_automate:cli',
            'AzureDownload = azure_storage.azure_download:cli',
            'AzureDelete = azure_storage.azure_delete:cli',
            'AzureUpload = azure_storage.azure_upload:cli',
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
