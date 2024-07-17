import hashlib
import io
import os
import yaml

from rich import print as rich_print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table, box

from plugins.FabMaMiCo.scripts.utils.functions import print_box
from plugins.FabMaMiCo.scripts.configuration.mamico_configuration import MaMiCoConfiguration
from plugins.FabMaMiCo.scripts.configuration.ls1_configuration import LS1Configuration


class MainConfiguration:
    """
    Configuration class to store and manage all the user configuration.
    """
    def __init__(self, plugin_filepath: str, config: str):
        """
        TODO: write docstring

        Returns:
            None
        """
        self.plugin_filepath = plugin_filepath
        self.config = config
        self.applications = ['MaMiCo']
        self.configs = {}
        self.configs['MaMiCo'] = MaMiCoConfiguration(plugin_filepath, config)
        if self.configs['MaMiCo'].get('use_ls1'):
            self.applications.append('ls1-mardyn')
            self.configs['ls1-mardyn'] = LS1Configuration(plugin_filepath, config)
        if self.configs['MaMiCo'].get('BUILD_WITH_ADIOS2'):
            self.applications.append('adios2')
            raise Exception("adios2 is not implemented yet.")
        if self.configs['MaMiCo'].get('BUILD_WITH_EIGEN'):
            self.applications.append('eigen')
            raise Exception("eigen is not implemented yet.")
        if self.configs['MaMiCo'].get('BUILD_WITH_LAMMPS'):
            self.applications.append('lammps')
            raise Exception("lammps is not implemented yet.")
        if self.configs['MaMiCo'].get('BUILD_WITH_OPENFOAM'):
            self.applications.append('openfoam')
            raise Exception("openfoam is not implemented yet.")
        if self.configs['MaMiCo'].get('BUILD_WITH_PRECICE'):
            self.applications.append('precice')
            raise Exception("precice is not implemented yet.")
        if self.configs['MaMiCo'].get('BUILD_WITH_PYBIND11'):
            self.applications.append('pybind11')
            raise Exception("pybind11 is not implemented yet.")
        
        for app in self.applications:
            self.configs[app].check_config()
            self.configs[app].update_config()
            self.configs[app].print_config()

    def get_cleaned(self):
        """
        Return the cleaned configuration.

        Returns:
            dict: dict with key value pairs that are not matching the defaults
        """
        # remove key value pairs from config if value is matching defaults
        cleaned_config = {k: v for k, v in self.config.items() if v != self.defaults[k]}
        return cleaned_config

    def print_config(self):
        """
        Print the user configuration as table.
        
        Returns:
            None
        """
        self._print_table(self.config, title="User Configuration")

    def print_defaults(self):
        """
        Print the default configuration as table.

        Returns:
            None
        """
        self._print_table(self.defaults, title="Default Configuration")

    def print_config_cleaned(self):
        """
        Print the cleaned configuration as table.

        Returns:
            None
        """
        cleaned_config = self.get_cleaned()
        self._print_table(cleaned_config, title="User Configuration (non-defaults)")

    def _print_table(self, dict, title):
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

    def check_config(self, check=True):
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

    def generate_checksum(self):
        data = {}
        for app in self.applications:
            data.update( { self.configs[app].application_name: self.configs[app].config } )
        io_string = io.StringIO()
        yaml.dump(data, io_string, indent=2)
        checksum = hashlib.md5(io_string.getvalue().encode('utf-8')).hexdigest()
        os.makedirs(os.path.join(self.plugin_filepath, 'tmp', 'checksum_files'), exist_ok=True)
        with open(os.path.join(self.plugin_filepath, 'tmp', 'checksum_files', f'{checksum}.yml'), 'w') as f:
            f.write(io_string.getvalue())
        print_box(
            f"MD5 Checksum: {checksum}",
            title="MD5 Checksum",
            color="green"
        )
        return checksum
