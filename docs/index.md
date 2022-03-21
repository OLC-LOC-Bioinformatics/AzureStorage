## OLC Bioinformatics AzureStorage tools

This suite of tools (written in Python) allows you to manipulate containers/files/folders in your Azure storage account.

There are nine scripts in this package:

1. [`AzureCredentials`](credentials.md): enter, modify, or delete your Azure connection string and account name into your system keyring, avoiding storing plain text passwords, environmental variables, and entering the connection string every time you run one of the scripts in the package
2. [`AzureUpload`](upload.md): upload a file or folder to a container in your Azure storage account
3. [`AzureSAS`](sas_url.md): create SAS (shared access signature) URLs for a file, a folder, or an entire container in your Azure storage account.
4. [`AzureMove`](move.md): move a file, folder, or an entire container within your Azure storage account
5. [`AzureDownload`](download.md): download a file, folder, or an entire container from your Azure storage account
6. [`AzureTier`](set_tier.md): set the storage tier of a file, folder, or an entire container from your Azure storage account
7. [`AzureDelete`](delete.md): delete a file, folder, or an entire container from your Azure storage account
8. [`AzureAutomate`](automate.md): run upload, sas, move, download, set_tier, and/or delete in batch
9. [`AzureList`](list.md): List and optionally filter containers and/or files in your Azure storage account


### Feedback

If you encounter any issues installing or running AzureStorage, have feature requests, or need assistance, please [open an issue on GitHub](https://github.com/OLC-LOC-Bioinformatics/AzureStorage/issues/new/choose), or email me at `adam.koziol@inspection.gc.ca`  