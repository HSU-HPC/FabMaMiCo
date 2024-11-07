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


class MaMiCoSetup():
    """
    Class to set up a MaMiCo installation on a remote machine.
    """

    def __init__(self, plugin_path: str, config: str, settings: Settings):
        """
        Initialize class variables and set up local path.

        Args:
            plugin_filepath (str): The absolute filepath to the plugin's root directory
            config (str): The name of the user configuration directory

        Returns:
            None
        """
        self.plugin_path: str = plugin_path
        self.config: str = config
        self.settings: Settings = settings
        self.local_tmp_path: str = os.path.join(self.plugin_path, 'tmp')
        self.local_mamico_path: str = os.path.join(self.plugin_path, 'tmp', 'MaMiCo')
        self.local_openfoam_path: str = os.path.join(self.plugin_path, 'tmp', 'OpenFoam')

    def prepare_mamico_locally(self) -> str:
        """
        Download MaMiCo from github if not already available locally.
        Check out the given branch/tag/commit.

        Returns:
            str: The latest commit hash of MaMiCo
        """
        # Check if the user specified a branch/tag/commit for MaMiCo, otherwise use 'master'
        mamico_branch_tag_commit = self.settings.get('mamico_branch_tag_commit', 'master')

        # Check whether MaMiCo folder is already available locally
        if not os.path.isdir(self.local_mamico_path):
            # Download MaMiCo and checkout the given branch/tag/commit
            rich_print(
                Panel(
                    f"Please wait until branch/tag/commit '{mamico_branch_tag_commit}' "\
                    f"is available locally.",
                    title="Downloading MaMiCo",
                    border_style="pink1",
                    expand=False,
                )
            )
            # Clone MaMiCo from GitHub
            local(
                f"git clone https://github.com/HSU-HPC/MaMiCo.git {self.local_mamico_path}",
                capture=True
            )
            local(
                "git reset --hard",
                cwd=self.local_mamico_path,
                capture=True
            )
            local(
                f"git checkout {mamico_branch_tag_commit}",
                cwd=self.local_mamico_path,
                capture=True
            )
        else:
            # MaMiCo is already downloaded locally
            # Checkout to master to be able to pull latest changes
            #   (this is not possible with checked out tags/commits)
            rich_print(
                Panel(
                    f"Please wait until branch/tag/commit '{mamico_branch_tag_commit}' "\
                    f"is updated and checked out.",
                    title="Pulling latest MaMiCo changes",
                    border_style="pink1",
                    expand=False,
                )
            )
            local(
                "git reset --hard",
                cwd=self.local_mamico_path,
                capture=True
            )
            local(
                "git checkout master",
                cwd=self.local_mamico_path,
                capture=True
            )
            # Pull the latest changes and all branches/tags/commits
            local(
                "git pull",
                cwd=self.local_mamico_path,
                capture=True
            )
            # Checkout the given branch/tag/commit
            local(
                f"git checkout {mamico_branch_tag_commit}",
                cwd=self.local_mamico_path,
                capture=True
            )
        # Determine the latest commit hash
        mamico_commit = self._get_latest_commit(directory=self.local_mamico_path)
        detail_text = ""
        if mamico_commit != mamico_branch_tag_commit:
            detail_text = f"\n - commit: '{mamico_commit}'."
        # Print a message that MaMiCo is up-to-date
        rich_print(
            Panel(
                f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}' is up to date."\
                f"{detail_text}",
                title="MaMiCo is now locally available",
                border_style="green",
                expand=False,
            )
        )
        return mamico_commit

    def prepare_ls1_locally(self, need_ls1: bool = False) -> str:
        """
        Optionally download ls1-mardyn if instructed by the user-configuration.
        Check out the given branch/tag/commit for ls1-mardyn.
        
        Args:
            need_ls1 (bool): Whether ls1-mardyn is needed or not
        
        Returns:
            str: The latest commit hash of ls1-mardyn or empty string if not needed
        """
        if need_ls1:
            # If the user wants to use ls1-mardyn, check if the user specified
            #   a branch/tag/commit for ls1-mardyn, otherwise use default
            ls1_branch_tag_commit = self.settings.get('ls1_branch_tag_commit', None)
            if len(os.listdir(os.path.join(self.local_mamico_path, "ls1"))) == 0:
                rich_print(
                    Panel(
                        f"Please wait until branch/tag/commit "\
                        f"'{ls1_branch_tag_commit}' is available locally.\n"\
                        f"This may take a while.""",
                        title="Downloading ls1-mardyn",
                        border_style="pink1",
                        expand=False,
                    )
                )
            else:
                rich_print(
                    Panel(
                        f"Please wait until branch/tag/commit "\
                        f"'{ls1_branch_tag_commit}' is updated and checked out.",
                        title="Pulling latest ls1-mardyn changes",
                        border_style="pink1",
                        expand=False,
                    )
                )
            # Pull ls1 whether locally already available or not
            # This also checks out the default branch/tag/commit that is given in the MaMiCo repository
            local(
                "git submodule update --init --recursive",
                cwd=self.local_mamico_path,
                capture=True
            )
            # Check if using a specific branch/tag/commit for ls1-mardyn
            if ls1_branch_tag_commit is not None:
                local(
                    "git reset --hard",
                    cwd=os.path.join(self.local_mamico_path, "ls1"),
                    capture=True
                )
                local(
                    f"git checkout {ls1_branch_tag_commit}",
                    cwd=os.path.join(self.local_mamico_path, "ls1"),
                    capture=True
                )
            rich_print(
                Panel(
                    f"ls1-mardyn branch/tag/commit '{ls1_branch_tag_commit}' is up to date.",
                    title="ls1-mardyn is now locally available",
                    border_style="green",
                    expand=False,
                )
            )
            return self._get_latest_commit(directory=os.path.join(self.local_mamico_path, "ls1"))
        else:
            # Remove ls1 folder if not needed
            shutil.rmtree(os.path.join(self.local_mamico_path, "ls1"), ignore_errors=True)
            # Recreate empty folder ls1
            os.makedirs(os.path.join(self.local_mamico_path, "ls1"), exist_ok=True)
            return ''

    def check_mamico_availability(self, output: bool = True) -> bool:
        """
        Check whether MaMiCo executable 'couette' is already available on the remote machine.

        Returns:
            bool: True if MaMiCo's 'couette' is already available, False otherwise
        """
        try:
            run(
                f'test -d {env.mamico_dir}/{env.mamico_checksum}/build '\
                f'&& test -e {env.mamico_dir}/{env.mamico_checksum}/build/couette '\
                f'&& test -e {env.mamico_dir}/{env.mamico_checksum}/build/compilation_info.yml',
                capture=True
            )
            if output:
                rich_print(
                    Panel(
                        f"MaMiCo has already been compiled - the executable [bold]couette[/bold] is located here:\n" \
                        f"{env.mamico_dir}/{env.mamico_checksum}/build",
                        title=f"MaMiCo is available on {env.host}",
                        border_style="green",
                        expand=False,
                    )
                )
            return True
        except Exception as e:
            return False

    def transfer_to_remote_host(self):
        """
        Transfer the MaMiCo source code to the remote host.
        """
        need_ls1 = self.settings.get('need_ls1', False)
        need_openfoam = self.settings.get('need_openfoam', False)
        rich_print(
            Panel(
                f"Please wait until the source code of MaMiCo"\
                f"{', ls1-mardyn' if need_ls1 else ''}"\
                f" is copied to {env.host}.",
                title=f"Transferring Source Code"\
                    f"{ ' & ls1-mardyn' if need_ls1 else '' }",
                border_style="pink1",
                expand=False
            )
        )
        # Set which files to exclude
        exclude = ['.git/', '.github/', '.gitignore', '.gitmodules']
        if need_ls1:
            exclude += ['ls1/.git/']

        # Copy MaMiCo to the remote machine
        rsync_project(
            local_dir=self.local_mamico_path,
            remote_dir=os.path.join(env.mamico_dir, env.mamico_checksum),
            exclude=['.git/', '.github/', '.gitignore', '.gitmodules'],
            delete=True,
            quiet=True
        )
        if need_openfoam:
            rsync_project(
                local_dir=self.local_openfoam_path,
                remote_dir=env.openfoam_dir,
                delete=True,
                quiet=True
            )
        # put(
        #     src=self.local_mamico_path,
        #     dst=os.path.join(env.mamico_dir, env.mamico_checksum),
        # )
        # Print success message
        rich_print(
            Panel(
                f"MaMiCo"\
                f"{', ls1-mardyn' if need_ls1 else ''}"\
                f"{', OpenFOAM' if need_openfoam else ''}"\
                f" was successfully copied to {os.path.join(env.mamico_dir, env.mamico_checksum)}.",
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
            txt += " -DMAMICO_COUPLING=ON -DMAMICO_SRC_DIR='..'"
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
