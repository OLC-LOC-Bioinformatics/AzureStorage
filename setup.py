#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name="AzureStorage",
    version="0.0.1",
    entry_points={
        'console_scripts': [
            'AzureCredentials = azure_storage.azure_credentials:cli',
            'AzureDownload = azure_storage.azure_download:cli',
            'AzureUpload = azure_storage.azure_upload:cli',
            'AzureSAS = azure_storage.azure_sas:cli'
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    author="Adam Koziol",
    author_email="adam.koziol@inspection.gc.ca",
    url="https://github.com/OLC-LOC-Bioinformatics/AzureStorage",
)
