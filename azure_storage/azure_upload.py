#!/usr/bin/env python
"""
Upload files or folders to Azure storage
"""

# Standard imports
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)
import logging
import os
import sys

# Third party imports
from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError
)
import coloredlogs

# Local imports
from azure_storage.methods import (
    client_prep,
    create_blob_client,
    create_parent_parser,
    setup_arguments
)


class AzureUpload:
    """
    Class for uploading a file or folder to an Azure storage container.

    Attributes:
        container_name (str): Name of the container.
        connect_str (str): Connection string for the Azure storage account.
        blob_service_client (azure.storage.blob.BlobServiceClient):
            BlobServiceClient object to interact with the Azure storage.
        container_client (azure.storage.blob.ContainerClient):
            ContainerClient object for the container.
        account_name (str): Name of the Azure storage account.
        category (str): The category of the object to upload ('file' or
            'folder').
        object_name (str): The name of the object to upload.
        path (str): The local path of the object to upload.
        storage_tier (str): The desired storage tier for the uploaded object.
    """

    def main(self):
        """
        Main method for the AzureUpload class.

        This method validates the container name, retrieves the connection
        string, creates the necessary clients, and uploads the specified file
        or folder to the container.
        """
        self.container_name, \
            self.connect_str, \
            self.blob_service_client, \
            self.container_client = \
            client_prep(
                container_name=self.container_name,
                account_name=self.account_name
            )
        # Hide the INFO-level messages sent to the logger from Azure by
        # increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        # Run the proper method depending on whether a file or a folder is
        # requested
        if self.category == 'file':
            # If the container doesn't exist, run the container creation
            # method, and re-run the upload
            self.upload_file(
                object_name=self.object_name,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                account_name=self.account_name,
                path=self.path,
                storage_tier=self.storage_tier
            )
        elif self.category == 'folder':
            self.upload_folder(
                object_name=self.object_name,
                blob_service_client=self.blob_service_client,
                container_name=self.container_name,
                account_name=self.account_name,
                path=self.path,
                storage_tier=self.storage_tier
            )

    @staticmethod
    def upload_file(
            object_name,
            blob_service_client,
            container_name,
            account_name,
            path,
            storage_tier):
        """
        Upload a single file to Azure storage
        :param object_name: type str: Name and path of file/folder to download
        from Azure storage
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param account_name: type str: Name of the Azure storage account
        :param path: type str: Path of folders in which the files are to
            be placed
        :param storage_tier: type str: Storage tier to use for the file
        """
        # Extract the name of the file from the provided name, as it may
        # include the path
        file_name = os.path.basename(object_name)
        if path is not None:
            file_name = os.path.join(path, file_name)
        # Create a blob client for this file in the container in which it will
        # be stored
        blob_client = create_blob_client(
            blob_service_client=blob_service_client,
            container_name=container_name,
            blob_file=file_name
        )
        # Attempt to upload the file to the specified container.
        try:
            # Read in the file data as binary
            with open(object_name, "rb") as data:
                # Upload the file data to the blob
                blob_client.upload_blob(data)
                # Set the storage tier
                blob_client.set_standard_blob_tier(
                    standard_blob_tier=storage_tier)
        # If a file with that name already exists in that container, warn the
        # user
        except ResourceExistsError as exc:
            logging.warning(
                'The file %s already exists in container %s in storage '
                'account %s',
                file_name, container_name, account_name
            )
            raise SystemExit from exc
        # Despite the attempt to correct the container name, it may still be
        # invalid
        except HttpResponseError as exc:
            if 'ContainerNotFound' in str(exc):
                logging.warning(
                    'Could not create container %s', container_name
                )
                raise SystemExit from exc
        except FileNotFoundError as exc:
            logging.error(
                'Could not find the specified file %s to upload. Please '
                'ensure that the supplied name and path are correct.',
                object_name
            )
            raise SystemExit from exc

    @staticmethod
    def upload_folder(
            object_name,
            blob_service_client,
            container_name,
            account_name,
            path,
            storage_tier):
        """
        Upload all the files (and sub-folders as applicable) in the specified
        folder to Azure storage
        :param object_name: type str: Name and path of file/folder to download
            from Azure storage
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param container_name: type str: Name of the container of interest
        :param account_name: type str: Name of the Azure storage account
        :param path: type str: Path of folders in which the files are to
            be placed
        :param storage_tier: type str: Storage tier to use for the folder
        """
        # Use os.walk to find all the files and folders in the supplied
        # directory
        for root, _, files in os.walk(object_name):
            # Determine the relative path for the current sub-folder to the
            # supplied root folder by creating a list from the splitting of
            # the root path using the OS-appropriate separator (os.sep) and
            # slicing the list to remove the first entry (the root)
            # .g. outputs/files/reports, where 'outputs/files' is the supplied
            # directory, would return 'files/reports'
            rel_path = os.path.join(os.sep.join(root.split(os.sep)[1:]))
            for file_name in files:
                # If the path is supplied, the folders of interest must be
                # extracted in order to keep the original folder structure
                if path is not None:
                    # Set the target folder as the relative path between the
                    # root and the supplied folder name e.g.
                    # /home/users/files/folder/nested_folder and
                    # /home/users/files/folder would return
                    # nested_folder, while identical root and folder would
                    # return a dot (.)
                    target_folder = os.path.relpath(
                        root, start=object_name.rstrip(os.sep))
                    # If the target_folder is a dot, treat it as empty
                    target_folder = \
                        target_folder if target_folder != '.' else ''
                    # Create the target file in the container by joining the
                    # desired path, the target folder and the name of the file
                    target_file = os.path.join(path, target_folder, file_name)
                # Add the file name to the calculated relative path to set the
                # name of the blob in Azure storage e.g.
                # files/reports/summary.tsv
                else:
                    target_file = os.path.join(rel_path, file_name)
                # Create a blob client for this file using the supplied
                # container name
                blob_client = create_blob_client(
                    blob_service_client=blob_service_client,
                    container_name=container_name,
                    blob_file=target_file
                )
                # Set the local name and path of the file, so it can be opened
                local_file = os.path.join(root, file_name)
                # Attempt to upload the file to the specified container
                try:
                    # Re-add the root path to find the file on the local system
                    with open(os.path.join(local_file), "rb") as data:
                        # Upload the file to Azure storage
                        blob_client.upload_blob(data)
                        # Set the storage tier
                        blob_client.set_standard_blob_tier(
                            standard_blob_tier=storage_tier)
                # Print a warning if a file with that name already exists in
                # the specified container
                except ResourceExistsError:
                    logging.warning(
                        'The file %s already exists in container %s in '
                        'storage account %s as %s',
                        local_file, container_name, account_name, target_file
                    )

    def __init__(
            self,
            object_name,
            container_name,
            account_name,
            path,
            storage_tier,
            category):
        # Set the name of the file/folder to upload
        self.object_name = object_name
        if category == 'file':
            try:
                assert os.path.isfile(self.object_name)
            except AssertionError as exc:
                logging.error(
                    'Cannot locate the specified file to upload: %s',
                    self.object_name
                    )
                raise SystemExit from exc
        elif category == 'folder':
            try:
                assert os.path.isdir(self.object_name)
            except AssertionError as exc:
                logging.error(
                    'Cannot located the specified folder to upload: %s',
                    self.object_name
                    )
                raise SystemExit from exc
        else:
            logging.error(
                'Something is wrong. There is no %s option available',
                category
            )
            raise SystemExit
        # Initialise necessary class variables
        self.account_name = account_name
        self.container_name = container_name
        self.path = path
        self.storage_tier = storage_tier
        self.category = category
        self.connect_str = str()
        self.blob_service_client = None
        self.container_client = None
        self.retry = False


def file_upload(args):
    """
    Run the AzureUpload class for a file
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Uploading %s to container %s in Azure storage account %s',
        args.file, args.container_name, args.account_name
    )
    # Create the file_upload object
    file_uploader = AzureUpload(
        object_name=args.file,
        account_name=args.account_name,
        container_name=args.container_name,
        path=args.reset_path,
        storage_tier=args.storage_tier,
        category='file'
    )
    file_uploader.main()


def folder_upload(args):
    """
    Run the AzureUpload class for a folder
    :param args: type ArgumentParser arguments
    """
    logging.info(
        'Uploading folder (and its contents) %s to container %s in Azure '
        'storage account %s',
        args.folder, args.container_name, args.account_name
    )
    folder_uploader = AzureUpload(
        object_name=args.folder,
        account_name=args.account_name,
        container_name=args.container_name,
        path=args.reset_path,
        storage_tier=args.storage_tier,
        category='folder'
    )
    folder_uploader.main()


def cli():
    """
    CLI function for uploading files or folders to Azure storage.

    This function sets up argument parsing for the CLI, including subparsers
    for uploading files and folders.

    The function then sets up the arguments and runs the appropriate subparser
    based on the provided arguments.

    After the operation is complete, the function logs a completion message
    and suppresses further console output.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = ArgumentParser(
        description='Upload files or folders to Azure storage'
    )
    # Create the parental parser, and the subparser
    subparsers, parent_parser = create_parent_parser(parser=parser)
    parent_parser.add_argument(
        '-r', '--reset_path', type=str,
        help='Set the path of the file/folder within a folder in the target '
        'container e.g. sequence_data/220202-m05722. If you want to place it '
        'directly in the container without any nesting, use or \'\''
    )
    parent_parser.add_argument(
        '-s', '--storage_tier', type=str, default='Hot',
        choices=['Hot', 'Cool', 'Archive'],
        metavar='STORAGE_TIER',
        help='Set the storage tier for the file/folder to be uploaded. '
        'Options are "Hot", "Cool", and "Archive". Default is Hot'
    )
    # File upload subparser
    file_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='file',
        description='Upload a file to Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Upload a file to Azure storage'
    )
    file_subparser.add_argument(
        '-f', '--file', type=str, required=True,
        help='Name and path of the file to upload to Azure storage. e.g. '
        '/mnt/sequences/220202_M05722/2022-SEQ-0001_S1_L001_R1_001.fastq.gz'
    )
    file_subparser.set_defaults(func=file_upload)
    # Folder upload subparser
    folder_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='folder',
        description='Upload a folder to Azure storage',
        formatter_class=RawTextHelpFormatter,
        help='Upload a folder to Azure storage'
    )
    folder_subparser.add_argument(
        '-f', '--folder',
        type=str,
        required=True,
        help='Name and path of the folder to upload to Azure storage.'
             'e.g. /mnt/sequences/220202_M05722/'
    )
    folder_subparser.set_defaults(func=folder_upload)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to
    # WARNING to suppress the log being filled with information from
    # azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    logging.info('Upload complete')
    # Prevent the arguments being printed to the console (they are returned in
    # order for the tests to work)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    return arguments


if __name__ == '__main__':
    cli()
