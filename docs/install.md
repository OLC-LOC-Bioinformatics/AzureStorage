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

You can now install the AzureStorage package (this command creates a new conda environment with AzureStorage installed):

`conda create -n azurestorage -c olc-bioinformatics azure_storage=0.0.4`

### Credentials 

You must store your Azure storage connection string before running any of the other scripts

[Find your connection string](https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string#:~:text=You%20can%20find%20your%20storage,primary%20and%20secondary%20access%20keys.)

 - In a browser, navigate to the [azure portal](portal.azure.com)
 - Login using your corporate credentials
 - From the Azure services (top of page), select 'Storage accounts'
 - Click on your account Name (ask a bioinformatician for this info)
 - From the options on the left, navigate down to and select "Access keys"
 - You will be able to "show" and copy your access key from this page

[Find your account key](https://www.zenko.io/blog/how-to-find-keys-and-account-info-for-aws-azure-and-google/#:~:text=Azure%20Account%20Name%C2%A0%3D%20the%20name%20of%20your%20Azure%20storage%20account%20located%20on%20the%20top%20of%20the%20Azure%20Portal%20(screenshot%20below%20%E2%80%93%20%E2%80%9Cscalitydemo%E2%80%9D%20is%20Azure%20Account%20Name).)

Once you know your account name and connection string, run:

`AzureCredentials store -a account_name`

Your credentials will be encrypted, and stored in the folder containing the `AzureStorage` package scripts

### Tests

If you encounter issues with the AzureStorage package, tests are available to ensure that the installation was successful and your credentials are valid.

You will need to clone this repository and run the tests with pytest


`git clone https://github.com/OLC-LOC-Bioinformatics/AzureStorage.git`

`cd AzureStorage`

`python -m pytest tests/ --cov=azure_storage --cov-config=.coveragec`



