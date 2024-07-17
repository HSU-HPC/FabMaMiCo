import copy
import hashlib
import io
import os
import yaml

from rich import print as rich_print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table, box

from plugins.FabMaMiCo.scripts.utils.functions import get_latest_commit_api

from plugins.FabMaMiCo.scripts.utils.sorted_dict import SortedDict
from plugins.FabMaMiCo.scripts.configuration.configuration import Configuration

class MaMiCoConfiguration(Configuration):
    """
    MaMiCo configuration class to store and manage the user configuration.
    """
    def __init__(self, plugin_filepath: str, config: str):
        """
        Initialize the MaMiCo configuration class with defaults and 
        a matching configuration dictionary.

        Returns:
            None
        """
        self.application_name = "MaMiCo"
        self.defaults = SortedDict({
            'mamico_branch_tag_commit': 'master',
            'use_ls1': False,
            'BUILD_TESTING': False,
            'BUILD_WITH_ADIOS2': False,
            'BUILD_WITH_EIGEN': False,
            'BUILD_WITH_LAMMPS': False,
            'BUILD_WITH_MPI': False,
            'BUILD_WITH_OPENFOAM': False,
            'BUILD_WITH_PINT_DEBUG': False,
            'BUILD_WITH_PRECICE': False,
            'BUILD_WITH_PYBIND11': False,
            'CMAKE_BUILD_TYPE': 'DebugOptimized',
            'CMAKE_INSTALL_PREFIX': '/usr/local',
            'COMPILETEST_COMPILERS': 'g++ clang++',
            'COMPILETEST_MODES': ['Debug', 'DebugOptimized', 'RelWithDebInfo', 'Release'],
            'MDDim': 'MDDim3',
            'MD_SIM': 'SIMPLE_MD'
        })
        self.non_cmake_flags = [
            'mamico_branch_tag_commit',
            'use_ls1'
        ]
        self.config = copy.deepcopy(self.defaults)
        config_filepath = os.path.join(plugin_filepath, 'config_files', config, 'configuration/config_mamico.yml')
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
        # Determine the commit hash of the given branch/tag/commit
        # TODO
        # commit_hash = get_latest_commit_api(
        #     owner="HSU-HPC",
        #     repository="MaMiCo",
        #     branch=self.config['mamico_branch_tag_commit']
        # )
        # self.config.update({ 'mamico_branch_tag_commit': commit_hash })
        pass
