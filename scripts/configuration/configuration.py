import hashlib
import io
import os
import yaml

from abc import ABC, abstractmethod

from rich import print as rich_print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table, box


class Configuration(ABC):
    """
    Configuration class to store and manage the user configuration.
    """
    def __init__(self):
        self.application_name = None
        self.config = {}
        self.defaults = {}

    def get(self, key, default = None):
        """
        Get a value from the configuration.

        Args:
            key (str): key of the value to get

        Returns:
            any: value of the key
        """
        if default is not None:
            return self.config.get(key, default)
        return self.config.get(key)
    
    def update(self, dict: dict):
        """
        Update the configuration with a dictionary.

        Args:
            dict (dict): dictionary with key value pairs to update

        Returns:
            None
        """
        self.config.update(dict)

    def get_cleaned(self):
        """
        Return the cleaned configuration.

        Returns:
            dict: dict with key value pairs that are not matching the defaults
        """
        # remove key value pairs from config if value is matching defaults
        cleaned_config = {k: v for k, v in self.config.items() if v != self.defaults.get(k, None)}
        return cleaned_config

    def print_config(self):
        """
        Print the user configuration as table.
        
        Returns:
            None
        """
        self._print_table(self.config, title=f"User Configuration: {self.application_name}")

    def print_defaults(self):
        """
        Print the default configuration as table.

        Returns:
            None
        """
        self._print_table(self.defaults, title=f"Default Configuration: {self.application_name}")

    def print_config_cleaned(self):
        """
        Print the cleaned configuration as table.

        Returns:
            None
        """
        cleaned_config = self.get_cleaned()
        self._print_table(cleaned_config, title=f"User Configuration: {self.application_name} (non-defaults)")

    def _print_table(self, dict: dict, title: str):
        """
        Print the user configuration in a table format.

        Args:
            dict (dict): dictionary with key value pairs
            title (str): title of the table

        Returns:
            None
        """
        table = Table(
            title=f"[green]{title}[/green]",
            show_header=True,
            show_lines=True,
            box=box.ROUNDED,
            header_style="dark_cyan",
        )
        table.add_column("Key", style="blue")
        table.add_column("Value", style="magenta")
        for k, v in dict.items():
            table.add_row(
                f"{k}",
                f"{v}",
            )
        console = Console()
        console.print(table)

    @abstractmethod
    def check_config(self, check: bool = True):
        """
        Check if the user configuration is valid.

        Args:
            check (bool): if True, check the configuration, otherwise return True

        Returns:
            bool: True if the configuration is valid, False otherwise
        """
        if not check:
            return True
        # TODO: check that e.g. if ls1 is used, the user has opted in for MPI
        # TODO: check that if 'BUILD_WITH_MPI' is set, it has to be loaded via module
        return True

    def get_yml_string(self):
        """
        Generate a string representation of the configuration according to yml format with 2 spaces indentation.

        Returns:
            io.StringIO: string representation of the configuration
        """
        # Cleanup the configuration:
        # TODO
        # Generate a string representation of the configuration according to yml format with 2 spaces indentation
        string_stream = io.StringIO()
        yaml.dump({ self.application_name: self.config }, string_stream, indent=2)
        return string_stream.getvalue()
