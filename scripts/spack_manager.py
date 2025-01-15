import hashlib
import io
import os
import shutil
import subprocess

import yaml
from rich import print as rich_print
from rich.panel import Panel

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from fabsim.base.networks import *
from plugins.FabMaMiCo.scripts.settings import Settings

FABMAMICO_PATH = get_plugin_path("FabMaMiCo")


class SpackManager():
    """
    Class to set up and manage a Spack installation on a remote machine.
    """


    def __init__(self):
        """
        Initialize class variables and set up local path.

        Args:
            plugin_filepath (str): The absolute filepath to the plugin's root directory
            config (str): The name of the user configuration directory

        Returns:
            None
        """
        self.local_tmp_path: str = os.path.join(FABMAMICO_PATH, 'tmp')
        self.local_spack_path: str = os.path.join(FABMAMICO_PATH, 'tmp', 'Spack')


    def prepare_locally(self) -> str:
        """
        Download Spack from Github if not already available locally.
        Otherwise, pull the latest changes.

        Returns:
            None
        """

        # Check whether MaMiCo folder is already available locally
        if not os.path.isdir(self.local_spack_path):
            # Download Spack
            rich_print(
                Panel(
                    f"Please wait until Spack is available locally.",
                    title="Downloading Spack",
                    border_style="pink1",
                    expand=False,
                )
            )
            local(
                f"git clone --depth=2 --branch=releases/v0.23 https://github.com/spack/spack.git {self.local_spack_path}"
                git clone --depth=2 --single-branch --branch releases/v0.22 git@github.com:spack/spack.git ./Spack
            )
        else:
            # Spack is already downloaded locally
            # Pull latest changes
            rich_print(
                Panel(
                    f"Please wait until the latest version of Spack is available locally.",
                    title="Pulling latest Spack changes",
                    border_style="pink1",
                    expand=False,
                )
            )
            local(
                "git pull",
                cwd=self.local_spack_path,
            )
        # Print a message that Spack is up-to-date
        rich_print(
            Panel(
                f"Spack is up to date locally.",
                title="Spack is now locally available",
                border_style="green",
                expand=False,
            )
        )


    def transfer_to_remote_host(self):
        """
        Transfer the Spack source code to the remote host.
        """
        rich_print(
            Panel(
                f"Please wait until the source code of Spack is copied to {env.host}.",
                title="Transferring Source Code",
                border_style="pink1",
                expand=False
            )
        )
        # Set which files to exclude
        exclude = ['.git/', '.github/', '.gitignore', '.gitmodules']

        # Copy Spack to the remote machine
        rsync_project(
            local_dir=self.local_spack_path,
            remote_dir=os.path.join(env.spack_dir),
            exclude=exclude,
            delete=True,
            quiet=True
        )
        rich_print(
            Panel(
                f"Spack has been successfully copied to {env.spack_dir} and is available for use.",
                title=f"Transfer to {env.host} succeeded",
                border_style="green",
                expand=False
            )
        )





    def generate_compile_command_ls1(self):
        """
        Generate the command to compile ls1-mardyn.

        Returns:
            str: The command to compile ls1-mardyn
        """
        txt = ""
        if self.settings.get('need_ls1', False):
            txt += f"cd {os.path.join(env.mamico_dir, env.mamico_checksum, 'ls1')}\n"
            txt += "cmake -S. -Bbuild"
            # txt += " -DMAMICO_COUPLING=ON -DMAMICO_SRC_DIR='..'"
            for key, value in self.settings.get('cmake_flags_ls1', {}).items():
                if isinstance(value, bool):
                    value = "ON" if value else "OFF"
                txt += f" -D{key}={value}"
            txt += "\n"
            txt += f"cmake --build build -- -j{env.compile_threads}"
        return txt

    def generate_compile_command_mamico(self):
        """
        Generate the command to compile MaMiCo.

        Returns:
            str: The command to compile MaMiCo
        """
        txt = ""
        txt += f"cd {os.path.join(env.mamico_dir, env.mamico_checksum)}\n"
        txt += "cmake -S. -Bbuild"
        for key, value in self.settings.get('cmake_flags_mamico', {}).items():
            if isinstance(value, bool):
                value = "ON" if value else "OFF"
            txt += f" -D{key}={value}"
        txt += "\n"
        txt += f"cmake --build build -- -j{env.compile_threads}"
        return txt

    def generate_compile_command_openfoam(self):
        """
        Generate the command to compile OpenFOAM.
        
        Returns:
            str: The command to compile OpenFOAM
        """
        txt = ""
        if self.settings.get('need_openfoam', False):
            txt += f"cd {os.path.join(env.openfoam_dir, 'OpenFOAM-v2206')}\n"
            txt += f"source {os.path.join(env.openfoam_dir, 'OpenFOAM-v2206/etc/bashrc')} || true\n"
            txt +=  "foamSystemCheck\n"
            txt +=  "foam || true\n"
            txt += f"./Allwmake -s -l -j {env.compile_threads}"
        return txt


    def save_config_yml(self):
        """
        Transfer the config file to the remote machine.

        Returns:
            None
        """
        local(
            f"scp -q -o LogLevel=QUIET {os.path.join(self.plugin_path, 'tmp/checksum_files', f'{env.mamico_checksum}.yml')} "\
            f"{env.username}@{env.remote}:{os.path.join(env.mamico_dir, env.mamico_checksum, 'compilation_info.yml')}"
        )

    def _get_latest_commit(self, directory: str = None) -> str:
        """
        Get the latest commit hash of the given directory.

        Args:
            directory (str): The directory to get the latest commit hash from
        
        Returns:
            str: The latest commit hash
        """
        res = subprocess.run(
            ["git rev-parse HEAD"],
            cwd=directory,
            capture_output=True,
            shell=True,
            check=True
        )
        return res.stdout.decode('utf-8').strip()
