#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name="AzureStorage",
    version="0.0.1",
    entry_points={
        'console_scripts': [
            'AzureDownload = azure_download.azure_download:cli',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    author="Adam Koziol",
    author_email="adam.koziol@inspection.gc.ca",
    url="https://github.com/OLC-LOC-Bioinformatics/AzureStorage",
)
