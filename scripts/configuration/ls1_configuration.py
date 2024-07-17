import copy
import hashlib
import io
import os
import yaml

from rich import print as rich_print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table, box

from plugins.FabMaMiCo.scripts.utils.sorted_dict import SortedDict
from plugins.FabMaMiCo.scripts.configuration.configuration import Configuration


class LS1Configuration(Configuration):
    """
    ls1-mardyn configuration class to store and manage the user configuration.
    """
    def __init__(self, plugin_filepath: str, config: str):
        """
        Initialize the ls1-mardyn configuration class with defaults and 
        a matching configuration dictionary.

        Returns:
            None
        """
        self.application_name = "ls1-mardyn"
        self.defaults = SortedDict({
            'ls1_branch_tag_commit': None,
        })
        self.non_cmake_flags = [
            'ls1_branch_tag_commit',
        ]
        self.config = copy.deepcopy(self.defaults)
        config_filepath = os.path.join(plugin_filepath, 'config_files', config, 'configuration/config_ls1.yml')
        with open(config_filepath, 'r') as config_file:
            try:
                self.config = {**self.config, **yaml.safe_load(config_file)}
            except yaml.YAMLError as e:
                raise e

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
    
    def update_config(self):
        pass
