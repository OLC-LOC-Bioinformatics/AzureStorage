#!/usr/bin/env python

"""
Explore an Azure storage account. List containers, files, or folders
"""

# Standard imports
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)
import logging
import os
import pathlib
import re
import sys

# Third party imports
import coloredlogs
from termcolor import colored

# Local imports
from azure_storage.methods import \
    create_blob_service_client, \
    client_prep, \
    create_parent_parser, \
    decrypt_credentials, \
    setup_arguments


class AzureContainerList:
    """
    Class for listing Azure storage containers.

    Attributes:
        connect_str (str): Connection string for the Azure storage account.
        blob_service_client (azure.storage.blob.BlobServiceClient):
            BlobServiceClient object to interact with the Azure storage.
        expression (str): Expression to filter the containers.
        print_container (bool): Whether to print the container names.
        output_file (str): Path to the output file to write the container
            names.
        account_name (str): Name of the Azure storage account.
    """

    def main(self):
        """
        Main method for the AzureContainerList class.

        This method sets the logging level to WARNING to suppress INFO-level
        messages from Azure, decrypts the credentials to get the connection
        string, creates the BlobServiceClient, and lists the containers.

        Returns:
            list: The list of containers.
        """
        # Hide the INFO-level messages sent to the logger from Azure by
        # increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        # Extract the connection string
        self.connect_str = decrypt_credentials(
            account_name=self.account_name
        )
        # Create the blob service client using the connection string
        self.blob_service_client = create_blob_service_client(
            connect_str=self.connect_str)
        containers = self.list_containers(
            blob_service_client=self.blob_service_client,
            expression=self.expression,
            print_container=self.print_container,
            output_file=self.output_file
        )
        return containers

    @staticmethod
    def list_containers(
            blob_service_client,
            expression,
            print_container,
            output_file):
        """
        List all containers in a storage account. If an expression is
        provided, find all containers that
        match the expression
        :param blob_service_client: type: azure.storage.blob.BlobServiceClient
        :param expression: type str: Expression to match. Can be a regular
        expression or 'normal' expression
        :param print_container: type bool: Boolean on whether to print
        container matches to the terminal
        :param output_file: type str: Name and path of file in which container
        names are to be written. Optional
        :return: container_matches: List of containers that match the
        expression
        """
        # Create a generator of all the containers in the storage account
        containers = blob_service_client.list_containers()
        # Prepare a list to store the containers that match the expression
        container_matches = list()
        # Allow a quiet exit on keyboard interrupts
        try:
            for container in containers:
                # Boolean to determine whether the expression matched the
                # container name
                match = False
                # If the expression contains non-alphanumeric characters
                # either at the start or anywhere, treat it as a
                # regular expression
                if re.match(r'.*\W', expression.replace('-', '_')):
                    # Use re.sub to convert * to .* to be consistent with
                    # regex rules. It seemed unintuitive to force the user to
                    # use .* rather than just * for simple queries.
                    # If .* was provided, don't add the '.' by using a negative
                    # lookbehind assertion
                    regex_expression = re.sub(r'(?<!\.)\*', '.*', expression)
                    # Use re.fullmatch to determine if the expression matches
                    # the container name
                    if re.fullmatch(rf'{regex_expression}$', container.name):
                        # Update the match boolean and append the container to
                        # the list of matches
                        match = True
                        container_matches.append(container)
                # The expression doesn't appear to be a regular expression
                else:
                    # Ensure a perfect match for non regex queries
                    if expression == container.name:
                        # Update the match boolean and append the container to
                        # the list of matches
                        match = True
                        container_matches.append(container)
                # Print the name of the container on a match
                if print_container and match:
                    # Use termcolor to print the name in bold green
                    print(colored(container.name, 'green', attrs=['bold']))
                # If requested, write the name of the container to the output
                # file on a match
                if output_file and match:
                    with open(output_file, 'a+', encoding='utf-8') as output:
                        output.write(f'{container.name}\n')
        except KeyboardInterrupt as exc:
            raise SystemExit from exc
        return container_matches

    def __init__(
            self,
            expression,
            account_name,
            output_file,
            print_container=True):
        self.expression = expression if expression else '*'
        self.account_name = account_name
        # Ensure that the output file can be used
        if output_file:
            # Output file
            if output_file.startswith('~'):
                self.output_file = os.path.abspath(
                    os.path.expanduser(os.path.join(output_file)))
            else:
                self.output_file = os.path.abspath(os.path.join(output_file))
                # Ensure that the output file can be used
                if not os.path.isfile(self.output_file):
                    try:
                        # Create the parental directory for the output file as
                        # required
                        os.makedirs(
                            os.path.dirname(
                                self.output_file),
                            exist_ok=True)
                    except PermissionError as exc:
                        logging.error(
                            'Insufficient permissions to create output '
                            'file %s',
                            self.output_file
                        )
                        raise SystemExit from exc
                    try:
                        open(self.output_file, 'w', encoding='utf-8').close()
                    except IsADirectoryError as exc:
                        logging.error(
                            'A directory or an empty file name was provided '
                            'for the output file %s',
                            self.output_file
                            )
                        raise SystemExit from exc
                    except PermissionError as exc:
                        logging.error(
                            'Insufficient permissions to create output '
                            'file %s',
                            self.output_file
                        )
                        raise SystemExit from exc
        else:
            self.output_file = str()
        self.connect_str = str()
        self.blob_service_client = None
        # Boolean on whether the container name should be printed to terminal
        self.print_container = print_container


class AzureList:
    """
    Class for listing files in Azure storage containers.

    Attributes:
        container_name (str): Name of the container where the files are.
        connect_str (str): Connection string for the Azure storage account.
        blob_service_client (azure.storage.blob.BlobServiceClient):
            BlobServiceClient object to interact with the Azure storage.
        expression (str): Expression to filter the files.
        output_file (str): Path to the output file to write the file names.
        account_name (str): Name of the Azure storage account.
    """
    def main(self):
        """
        Main method for the AzureList class.

        This method sets the logging level to WARNING to suppress INFO-level
        messages from Azure, checks if the container name is provided and
        does not look like a regular expression, and then either lists the
        files in the specified container or lists the files in all containers
        that match the provided expression.
        """
        # Hide the INFO-level messages sent to the logger from Azure by
        # increasing the logging level to WARNING
        logging.getLogger().setLevel(logging.WARNING)
        # If the container name was provided, and does not look like a regular
        # expression, run the client_prep method to validate the container
        # name, extract the connection string, and create the blob service
        # client and container client
        if self.container_name and not re.match(
                r'.*\W', self.container_name.replace('-', '_')):
            self.container_name, \
                self.connect_str, \
                self.blob_service_client, \
                container_client = \
                client_prep(
                    container_name=self.container_name,
                    account_name=self.account_name
                )
            # List all the files that match the expression
            self.list_files(
                container_client=container_client,
                expression=self.expression,
                output_file=self.output_file,
                container_name=self.container_name
            )
        # If the container name wasn't provided, or looks like a regular
        # expression, use the AzureContainerList class to find containers
        # that match the provided expression
        else:
            list_containers = AzureContainerList(
                expression=self.container_name,
                account_name=self.account_name,
                output_file=str(),
                print_container=False
            )
            containers = list_containers.main()
            # Extract the connection string
            self.connect_str = decrypt_credentials(
                account_name=self.account_name)
            # Create the blob service client using the connection string
            self.blob_service_client = create_blob_service_client(
                connect_str=self.connect_str)
            # List all the files in each of the containers that match the
            # provided expression
            for container in containers:
                # Create a container client for the container
                container_client = \
                    self.blob_service_client.get_container_client(
                        container.name
                    )
                # Run the list_files method to list and optionally filter the
                # files
                self.list_files(
                    container_client=container_client,
                    expression=self.expression,
                    output_file=self.output_file,
                    container_name=container.name
                )

    @staticmethod
    def list_files(container_client, expression, output_file, container_name):
        """
        List and optionally filter (with a user-provided expression) all files
        in a container
        :param container_client: type
        azure.storage.blob.BlobServiceClient.ContainerClient
        :param expression: type str: Expression to match. Can be a regular
        expression or 'normal' expression
        :param output_file: type str: Name and path of file in which container
        names are to be written. Optional
        :param container_name: type str: Name of the container of interest
        """
        # Create a generator containing all the blobs in the container
        generator = container_client.list_blobs()
        # Allow a quiet exit on keyboard interrupts
        try:
            # Iterate through all the files in the container
            for blob_file in generator:
                # Store the file name and path in a variable
                filename = blob_file.name
                # Initialise a variable to track whether this file is a match
                # to the expression
                match = False
                # Use pathlib to create a path object from the file name
                path_obj = pathlib.Path(os.path.normpath(filename))
                # Split the file name into its separate components
                components = path_obj.parts
                # Check whether the expression contains non-alphanumeric
                # characters. If it does, treat it as a
                # regular expression. Ignore dashes as a non-alphanumeric
                # character.
                if re.match(r'.*\W', expression.replace('-', '_')):
                    # If the expression is targeted to nested files/folders,
                    # split the expression into its
                    # path components e.g. reports/outputs/output.tsv contains
                    # three components
                    expression_obj = pathlib.Path(os.path.normpath(expression))
                    expression_components = list(expression_obj.parts)
                    # The number of matches required is the number of path
                    # components e.g. reports/outputs/output.tsv requires
                    # three matches
                    matches_required = len(expression_components)
                    # Initialise a dictionary to track matches to each of the
                    # components
                    component_matches = dict()
                    # Search through all the path components of the file name
                    for i, component in enumerate(components):
                        # Check for nested files/folders
                        if len(expression_components) > 1:
                            while len(expression_components) < len(components):
                                expression_components.insert(-1, '*')
                            # Reset the number of matches required to the new
                            # length of the expression components
                            matches_required = len(expression_components)
                            # Use re.sub to convert * to .* to be consistent
                            # with regex rules
                            regex_expression = re.sub(
                                r'(?<!\.)\*', '.*', expression_components[i])
                            # If the components match, increment the number of
                            # matches
                            if re.fullmatch(
                                    rf'{regex_expression}$', component):
                                # Set the match to the current component to
                                # true
                                component_matches[component] = True
                        else:
                            # Use re.sub to convert * to .* to be consistent
                            # with regex rules
                            regex_expression = re.sub(
                                r'(?<!\.)\*', '.*', expression)
                            # If the component matches, set the match boolean
                            # to True
                            if re.fullmatch(
                                    rf'{regex_expression}$', component):
                                match = True
                    # Check to see if the number of matches observed in a
                    # multi-component expression is the number
                    # matches required for a match before setting the match
                    # boolean to True
                    if len(component_matches) == matches_required:
                        match = True
                # The expression does not look like a regular expression
                else:
                    for component in components:
                        # An exact match is required to be considered a match
                        if expression == component:
                            match = True
                # Only proceed if the file matches the expression
                if match:
                    # If the output file has been provided, write the file name
                    # to it
                    if output_file:
                        with open(
                                output_file, 'a+', encoding='utf-8') as output:
                            output.write(f'{container_name}\t{filename}\n')
                    # Initialise a variable to store the path information of
                    # the file
                    file_path = None
                    # Use termcolor to print the container name in bold green
                    container = colored(
                        container_name, 'green', attrs=['bold'])
                    # Determine if the file is nested in one or more folders
                    if len(path_obj.parts) > 1:
                        # Use termcolor to print the path in bold blue
                        file_path = colored(
                            f'{os.sep.join(components[: -1])} {os.sep} ',
                            'blue', attrs=['bold'])
                    # Remove any path information from the file name
                    filename = os.path.basename(filename)
                    # Use termcolor to print any archive files as bold red
                    if filename.endswith('.gz') or filename.endswith(
                            '.bz2') or filename.endswith('.zip'):
                        filename = colored(filename, 'red', attrs=['bold'])
                    # If the file was nested, print the extracted path
                    # information
                    if file_path:
                        print(f'{container}\t{file_path}{filename}')
                    # Otherwise, only print the file name
                    else:
                        print(f'{container}\t{filename}')
        except KeyboardInterrupt as exc:
            raise SystemExit from exc

    def __init__(self, container_name, expression, output_file, account_name):
        # If the container name wasn't provided, set it to *
        self.container_name = container_name if container_name else '*'
        self.expression = expression if expression else '*'
        self.account_name = account_name
        if output_file:
            # Output file
            if output_file.startswith('~'):
                self.output_file = os.path.abspath(
                    os.path.expanduser(os.path.join(output_file)))
            else:
                self.output_file = os.path.abspath(os.path.join(output_file))
                # Ensure that the output file can be used
                if not os.path.isfile(self.output_file):
                    try:
                        # Create the parental directory for the output file as
                        # required
                        os.makedirs(
                            os.path.dirname(
                                self.output_file),
                            exist_ok=True)
                    except PermissionError as exc:
                        logging.error(
                            'Insufficient permissions to create output '
                            'file %s',
                            self.output_file
                        )
                        raise SystemExit from exc
                    try:
                        open(self.output_file, 'w', encoding='utf-8').close()
                    except IsADirectoryError as exc:
                        logging.error(
                            'A directory or an empty file name was provided '
                            'for the output file %s',
                            self.output_file
                        )
                        raise SystemExit from exc
                    except PermissionError as exc:
                        logging.error(
                            'Insufficient permissions to create output '
                            'file %s',
                            self.output_file
                        )
                        raise SystemExit from exc
        else:
            self.output_file = str()
        self.connect_str = str()
        self.blob_service_client = None


def container_search(args):
    """
    Run the AzureContainerList class
    :param args: type ArgumentParser arguments
    """
    # Welcome message that is adjusted depending on whether an expression has
    # been provided
    phrase = f'Listing containers in Azure storage account {
        args.account_name}.'
    if args.expression:
        phrase += f'\nFiltering containers with the expression: {
            args.expression} '
    logging.info(phrase)
    list_containers = AzureContainerList(
        expression=args.expression,
        account_name=args.account_name,
        output_file=args.output_file,
    )
    list_containers.main()


def azure_search(args):
    """
    Run the AzureList class with the provided command line arguments
    :param args: type ArgumentParser arguments
    """
    # Welcome message that is adjusted depending on whether a container and/or
    # an expression have been provided
    phrase = f'Searching for files in Azure storage account {
        args.account_name}.'
    if args.container_name:
        phrase += f'\nFiltering containers with the expression: {
            args.container_name} '
    phrase += f'\nFiltering files with the expression: {args.expression}'
    logging.info(phrase)
    list_files = AzureList(
        container_name=args.container_name,
        expression=args.expression,
        account_name=args.account_name,
        output_file=args.output_file,
    )
    list_files.main()


def cli():
    """
    CLI function for exploring an Azure storage account.

    This function sets up argument parsing for the CLI, including subparsers
    for searching containers and files.

    The function then sets up the arguments and runs the appropriate
    subparser based on the provided arguments.

    After the operation is complete, the function logs a completion message
    and suppresses further console output.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = ArgumentParser(description='Explore your Azure storage account')
    subparsers, parent_parser = create_parent_parser(
        parser=parser,
        container=False
    )
    parent_parser.add_argument(
        'expression',
        nargs='?',
        # This allows the argument to be optional so things behave like actual
        # ls.
        default=None,
        type=str,
        help='Expression to search. This command supports regular expressions.'
             ' e.g. 1912* will return all containers starting with 1912, '
             'including 191216-dar. Note that since the regular expression is '
             'being entered on the command line, you may need to escape '
             'certain characters e.g. ! should be \\!'
    )
    parent_parser.add_argument(
        '-o', '--output_file', default=str(),
        help='Optionally provide the name and path of file in which the '
        'outputs are to be saved.'
    )
    container_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='container',
        description='Filter and list containers in your Azure storage account',
        formatter_class=RawTextHelpFormatter,
        help='Filter and list containers in your Azure storage account'
    )
    container_subparser.set_defaults(func=container_search)
    ls_subparser = subparsers.add_parser(
        parents=[parent_parser],
        name='search',
        description='Filter files in a container (or containers) in Azure '
        'storage',
        formatter_class=RawTextHelpFormatter,
        help='Filter files in a container (or containers) in Azure storage'
    )
    ls_subparser.add_argument(
        '-c', '--container_name', nargs='?', type=str, default=str(),
        help='Name of the Azure storage container. This command supports '
        'regular expressions e.g. 1912* will return all containers starting '
        'with 1912. Note that since the regular expression is being entered '
        'on the command line, you may need to escape certain characters '
        'e.g. ! should be \\! You can make your queries as complex as you '
        'wish: 1912\\d{2}-\\D{3}\\(\\?\\!*output\\) will only return '
        'containers that start with 1912, and have two additional digits. If '
        'the word output is present, any matches are ignored. There also '
        'have to be exactly three letters following a dash and the first '
        'six numbers e.g. 191216-dar and 191227-dar will be returned but not '
        '191216-dar-outputs 191202-test, 191216dar, 1912162-dar, '
        '191203-m05722, 191114-gta, or 200105-dar (and many others)'
    )
    ls_subparser.set_defaults(func=azure_search)
    # Set up the arguments, and run the appropriate subparser
    arguments = setup_arguments(parser=parser)
    # Return to the requested logging level, as it has been increased to
    # WARNING to suppress the log being filled with
    # information from azure.core.pipeline.policies.http_logging_policy
    coloredlogs.install(level=arguments.verbosity.upper())
    # Prevent the arguments being printed to the console (they are returned in
    # order for the tests to work)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    return arguments
