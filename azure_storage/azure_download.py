#!/usr/bin/env python

"""
Run methods to download files, folders and containers from Azure storage
"""


# Standard library imports
import logging
import os
import sys

# Related third party imports
from argparse import ArgumentParser, RawTextHelpFormatter
from azure.core.exceptions import ResourceNotFoundError
import coloredlogs

# Local application/library specific imports
from azure_storage.methods import (
    client_prep,
    create_blob_client,
    create_parent_parser,
    setup_arguments,
)


class AzureContainerDownload:
    """
    Download containers from Azure storage
    """
    def main(self):
        """
        Run the necessary container downloading methods
        """
        self.container_name, \
            self.connect_str, \
            self.blob_service_client, \
            self.container_client = \
            client_prep(
                container_name=self.container_name,
                account_name=self.account_name,
                create=False
            )
        self.download_container(
            container_client=self.container_client,
            blob_service_client=self.blob_service_client,
            container_name=self.container_name,
            output_path=self.output_path
        )

    @staticmethod
    def download_container(
            container_client,
            blob_service_client,
            container_name,
            output_path):
        """
        Download the container from Azure storage
        :param container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param output_path: type str: Name and path of the folder into which
        the container is to be downloaded
        """
        try:
            # Hide the INFO-level messages sent to the logger from Azure by
            # increasing the logging level to WARNING
            logging.getLogger().setLevel(logging.WARNING)

            # Identify all potential directories
            directories = set()
            generator = container_client.list_blobs()
            for blob in generator:
                # Split the blob name into parts and add each parent directory
                # to the set
                parts = blob.name.split('/')
                for i in range(1, len(parts)):
                    directories.add(
                        os.path.join(
                            output_path,
                            container_name,
                            *parts[:i]
                        )
                    )

            # Create directories
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logging.info("Directory created: %s", directory)

            # Recreate generator
            generator = container_client.list_blobs()
            for blob in generator:
                blob_path = os.path.join(
                    output_path,
                    container_name,
                    blob.name
                )

                # Ensure the directory for the blob exists
                os.makedirs(os.path.dirname(blob_path), exist_ok=True)

                # Skip if the blob path conflicts with an existing directory
                if os.path.isdir(blob_path):
                    logging.debug(
                        "Skipping blob with conflicting directory name: %s",
                        blob.name
                    )
                    continue

                # Download the blob
                blob_client = blob_service_client.get_blob_client(
                    container=container_name,
                    blob=blob.name
                )
                try:
                    with open(blob_path, 'wb') as file:
                        file.write(blob_client.download_blob().readall())
                except Exception as exc:
                    logging.error(
                        "Error downloading blob %s: %s", blob.name, exc)
                    raise SystemExit from exc

        except ResourceNotFoundError as exc:
            logging.error(
                'The specified container, %s, does not exist.', container_name
            )
            raise SystemExit from exc

    def __init__(self, container_name, output_path, account_name):
        # Set the container name variable
        self.container_name = container_name
        # Output path
        if output_path.startswith('~'):
            self.output_path = os.path.abspath(
                os.path.expanduser(os.path.join(output_path))
            )
        else:
            self.output_path = os.path.abspath(os.path.join(output_path))
        # Create the output path
        try:
            os.makedirs(self.output_path, exist_ok=True)
        except PermissionError as exc:
            logging.error(
                'Could not use the supplied output path: %s', self.output_path
            )
            raise SystemExit from exc
        # Initialise necessary class variables
        self.account_name = account_name
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


class AzureDownload:
    """
    Download file(s)/folder(s) from Azure storage
    """
    def main(self):
        """
        Run the file/folder downloading methods
        """
        self.container_name, \
            self.connect_str, \
            self.blob_service_client, \
            self.container_client = \
            client_prep(
                container_name=self.container_name,
                account_name=self.account_name,
                create=False
            )
        # Run the proper method depending on whether a file or a folder
        # is requested
        if self.category == 'file':
            self.download_file(
                container_client=self.container_client,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                object_name=self.object_name,
                output_path=self.output_path
            )
        elif self.category == 'folder':
            self.download_folder(
                container_client=self.container_client,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                object_name=self.object_name,
                output_path=self.output_path
            )
        else:
            logging.error(
                'Something is wrong. There is no %s option available',
                self.category
            )
            raise SystemExit

    @staticmethod
    def download_file(
            container_client,
            blob_service_client,
            container_name,
            object_name,
            output_path):
        """
        Download the specified file from Azure storage
        :param container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
        :param blob_service_client: type:
        azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param object_name: type str: Name and path of file to download
        from Azure storage
        :param output_path: type str: Name and path of the folder into which
        the file is to be downloaded
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Create a boolean to determine if the file has been located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by
        # increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        try:
            for blob_file in generator:
                # Filter for the blob name
                if blob_file.name == object_name:
                    # Update the file presence variable
                    present = True
                    # Create the blob client
                    blob_client = create_blob_client(
                        blob_service_client=blob_service_client,
                        container_name=container_name,
                        blob_file=blob_file
                    )
                    # Set the name of file by removing any path information
                    file_name = os.path.basename(blob_file.name)
                    # Finally, set the name and the path of the output file
                    download_file = os.path.join(output_path, file_name)
                    # Open the target output file as binary
                    with open(download_file, 'wb') as downloaded_file:
                        # Write the data from the blob client to the local file
                        downloaded_file.write(
                            blob_client.download_blob().readall()
                        )
            # Send an error to the user that the file could not be found
            if not present:
                logging.error(
                    'Could not locate the desired file %s in %s',
                    object_name,
                    container_name
                )
                raise SystemExit
        except ResourceNotFoundError as exc:
            logging.error(
                ' The specified container, %s, does not exist.',
                container_name
            )
            raise SystemExit from exc

    @staticmethod
    def download_folder(
            container_client,
            blob_service_client,
            container_name,
            object_name,
            output_path):
        """
        Download the specified folder from Azure storage
        :param container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
        :param blob_service_client: type:
        azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param object_name: type str: Name and path of folder to download
        from Azure storage
        :param output_path: type str: Name and path of the folder into which
        the folder is to be downloaded
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Boolean to track whether the folder was located
        present = False
        # Hide the INFO-level messages sent to the logger from Azure by
        # increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        try:
            for blob_file in generator:
                # Create the path of the file by adding the container name to
                # the path of the file
                blob_path = os.path.join(
                    container_name,
                    os.path.split(blob_file.name)[0]
                )
                # Ensure that the supplied folder path is present in the
                # blob path
                normalized_object_name = os.path.normpath(object_name)
                normalized_blob_path = os.path.normpath(blob_path)

                if normalized_object_name in normalized_blob_path:
                    # Update the folder presence boolean
                    present = True
                    # Create the blob client
                    blob_client = create_blob_client(
                        blob_service_client=blob_service_client,
                        container_name=container_name,
                        blob_file=blob_file
                    )
                    # Determine the path to output the file. Join the supplied
                    # path and the path of the blob
                    download_path = os.path.join(
                        output_path,
                        os.path.join(os.path.dirname(blob_file.name))
                    )
                    # Create the path if required
                    os.makedirs(download_path, exist_ok=True)
                    # Set the name of file by removing any path information
                    file_name = os.path.basename(blob_file.name)
                    # Finally, set the name and the path of the output file
                    download_file = os.path.join(download_path, file_name)
                    # Open the target output file as binary
                    with open(download_file, 'wb') as downloaded_file:
                        # Write the data from the blob client to the local file
                        downloaded_file.write(
                            blob_client.download_blob().readall()
                        )
            # Send an error to the user that the folder could not be found
            if not present:
                logging.error(
                    'Could not locate the desired folder %s in container %s',
                    object_name,
                    container_name
                )
                raise SystemExit
        except ResourceNotFoundError as exc:
            logging.error(
                ' The specified container, %s, does not exist.',
                container_name
            )
            raise SystemExit from exc

    def __init__(
            self,
            object_name,
            container_name,
            output_path,
            account_name,
            category):
        """
        Initializes an instance of the class.

        Parameters:
        object_name (str): The name of the file or folder to download.
        container_name (str): The name of the Azure storage container.
        output_path (str): The path where the downloaded file or folder
        should be stored.
        account_name (str): The name of the Azure storage account.
        category (str): The category of the object to download.

        The method sets the object name, container name, output path, account
        name, and category. It also initializes the connection string, blob
        service client, and container client to None.

        If the output path starts with '~', it is expanded to the absolute path
        The method attempts to create the output path, and raises a SystemExit
        exception if it fails due to a permission error.
    """
        # Set the name of the file/folder to download
        self.object_name = object_name
        # Set the container name variable
        self.container_name = container_name
        # Output path
        if output_path.startswith('~'):
            self.output_path = os.path.abspath(
                os.path.expanduser(os.path.join(output_path))
            )
        else:
            self.output_path = os.path.abspath(os.path.join(output_path))
        # Create the output path
        try:
            os.makedirs(self.output_path, exist_ok=True)
        except PermissionError as exc:
            logging.error(
                'Could not use the supplied output path: %s',
                self.output_path
            )
            raise SystemExit from exc
        # Initialise necessary class variables
        self.account_name = account_name
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None


def container_download(args):
    """
    Run the AzureContainerDownload method
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Downloading Azure container %s', args.container_name)
    # Create the container download object
    container_downloader = AzureContainerDownload(
        container_name=args.container_name,
        output_path=args.output_path,
        account_name=args.account_name,
    )
    container_downloader.main()


def file_download(args):
    """
    Run the AzureDownload class for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Downloading %s from Azure storage', args.file
    )
    # Create the file download object
    file_downloader = AzureDownload(
        object_name=args.file,
        container_name=args.container_name,
        output_path=args.output_path,
        account_name=args.account_name,
        category='file'
    )
    file_downloader.main()


def folder_download(args):
    """
    Run the AzureDownload class for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Downloading contents of folder %s from Azure storage',
        args.folder
    )
    folder_downloader = AzureDownload(
        object_name=args.folder,
        container_name=args.container_name,
        output_path=args.output_path,
        account_name=args.account_name,
        category='folder'
    )
    folder_downloader.main()


def cli():
    """
    Sets up the command-line interface for the application.

    The function creates an ArgumentParser and adds arguments for the output
    path, container name, file name, and folder name. It also creates
    subparsers for downloading a container, a file, and a folder from
    Azure storage.

    The function sets the default functions for the container, file, and folder
    subparsers to container_download, file_download, and
    folder_download, respectively.

    After setting up the arguments, the function increases the logging level
    to WARNING to suppress logs from
    azure.core.pipeline.policies.http_logging_policy, and then returns it to
    the requested level. It also redirects stderr to os.devnull to prevent
    the arguments from being printed to the console.

    Returns:
    argparse.Namespace: The parsed command-line arguments.
    """
    parser = ArgumentParser(
        description='Download containers/files/folders from Azure storage'
    )
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument(
        '-o', '--output_path',
        default=os.getcwd(),
        help='Name and path of directory in which the outputs are to be saved.'
        ' Default is your $CWD'
    )
    # Container downloading parser
    container_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Download a container from Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Download a container from Azure storage'
    )
    container_subparser.set_defaults(func=container_download)
    # Blob (file) downloading subparser
    file_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Download a file from Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Download a file from Azure storage'
    )
    file_subparser.add_argument(
        '-f', '--file',
        type=str,
        required=True,
        help='Name of file to download from Azure storage.'
             'e.g. 2022-SEQ-0001_S1_L001_R1_001.fastq.gz'
    )
    file_subparser.set_defaults(func=file_download)
    # Folder downloading subparser
    folder_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Download a folder from Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Download a folder from Azure storage'
    )
    folder_subparser.add_argument(
        '-f', '--folder',
        type=str,
        required=True,
        help='Name of the folder to download from Azure storage e.g. InterOp'
    )
    folder_subparser.set_defaults(func=folder_download)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to
    # WARNING to suppress the log being filled with information from
    # azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Download complete')
    # Prevent the arguments being printed to the console (they are returned in
    # order for the tests to work)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    return arguments


if __name__ == '__main__':
    cli()
    sys.exit(code=0)
