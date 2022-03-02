## Installation

AzureStorage is available as a conda package, so conda must be installed on your system.

### Conda

Skip this step if you have already installed conda

```
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda
conda update -q conda
```

### AzureStorage

You can now install the AzureStorage package:

`conda install -c olc-bioinformatics azure-storage`

#### Credentials 

You must enter your Azure storage connection string and account name into the system keyring before running any of the other scripts

[Find your connection string](https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string#:~:text=You%20can%20find%20your%20storage,primary%20and%20secondary%20access%20keys.)

[Find your account key](https://www.zenko.io/blog/how-to-find-keys-and-account-info-for-aws-azure-and-google/#:~:text=Azure%20Account%20Name%C2%A0%3D%20the%20name%20of%20your%20Azure%20storage%20account%20located%20on%20the%20top%20of%20the%20Azure%20Portal%20(screenshot%20below%20%E2%80%93%20%E2%80%9Cscalitydemo%E2%80%9D%20is%20Azure%20Account%20Name).)

Once you know your account key and connection string, run:

`AzureCredentials store`

Your credentials will be securely stored in the system keyring

### Tests

The AzureStorage package comes with unit tests to ensure that the installation and provided credentials are valid

`python -m pytest tests/`

Ensure that all tests complete successfully before proceeding


