import io
import os
import json
import yaml
import shutil
import subprocess
import hashlib

from rich import print as rich_print
from rich.panel import Panel

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from fabsim.base.networks import *

class MaMiCoSetup():
    def __init__(self, plugin_path: str, config: str):
        """
        Set up class variable 'plugin_filepath' and read the user
        configuration file 'mamico_user_config.yml'.

        Args:
            plugin_filepath (str): The absolute filepath to the plugin's root directory
        """
        self.plugin_path = plugin_path
        self.config = config
        self.tmp_path = os.path.join(plugin_path, 'tmp')
        self.mamico_local_path = os.path.join(self.plugin_path, 'tmp', 'MaMiCo')
        self.config_mamico = None


    def read_config(self):
        """
        Read the user configuration files `config_mamico.yml` and
        `config_simulation.yml` and store them in class variables.

        Returns:
            None
        """
        # Read the config_mamico.yml
        config_mamico_path = os.path.join(self.plugin_path, 'config_files', self.config, 'config_mamico.yml')
        with open(config_mamico_path, 'r') as config_mamico_file:
            try:
                self.config_mamico = yaml.safe_load(config_mamico_file)
            except yaml.YAMLError as exception:
                print(exception)


    def download_src_code(self):
        """
        Download MaMiCo from github if not already available locally.
        Check out the given branch/tag/commit.
        Optionally download ls1-mardyn if instructed by the user-configuration.
        Check out the given branch/tag/commit for ls1-mardyn.

        Returns:
            None
        """
        # Check if the user specified a branch/tag/commit for MaMiCo, otherwise use 'master'
        mamico_branch_tag_commit = self.config_mamico.get('mamico_branch_tag_commit', 'master')
        # Check if the user wants to use ls1-mardyn
        need_ls1 = self.config_mamico.get('need_ls1', False)
        if need_ls1:
            # If the user wants to use ls1-mardyn, check if the user specified
            #   a branch/tag/commit for ls1-mardyn, otherwise use default
            ls1_branch_tag_commit = self.config_mamico.get('ls1_branch_tag_commit', None)

        # Check whether MaMiCo folder is already available locally
        if not os.path.isdir(self.mamico_local_path):
            # Download MaMiCo and checkout the given branch/tag/commit
            rich_print(
                Panel(
                    f"Please wait until branch/tag/commit '{mamico_branch_tag_commit} "\
                    f"is available locally.",
                    title="[pink1]Downloading MaMiCo[/pink1]",
                    border_style="pink1",
                    expand=False,
                )
            )
            # Clone MaMiCo from GitHub
            try:
                subprocess.run(
                    [f"git clone https://github.com/HSU-HPC/MaMiCo.git {self.mamico_local_path}"],
                    shell=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise e
            try:
                subprocess.run(
                    ["git", "checkout", mamico_branch_tag_commit],
                    cwd=self.mamico_local_path,
                    text=True,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Determine the latest commit hash
            mamico_commit = self.get_latest_commit(directory=self.mamico_local_path)
            self.config_mamico.update({
                'mamico_branch_tag_commit': mamico_commit
            })
            detail_text = ""
            if mamico_commit != mamico_branch_tag_commit:
                detail_text = f"\n - commit: '{mamico_commit}'."
            rich_print(
                Panel(
                    f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}' was "\
                    f"successfully cloned to {self.mamico_local_path}."\
                    f"{detail_text}",
                    title="[green]MaMiCo Download successful[/green]",
                    border_style="green",
                    expand=False,
                )
            )
        else:
            # MaMiCo is already downloaded locally
            # Checkout to master to be able to pull latest changes
            #   (this is not possible with checked out tags/commits)
            try:
                subprocess.run(
                    ["git", "checkout", "master"],
                    cwd=self.mamico_local_path,
                    text=True,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Pull the latest changes and all branches/tags/commits
            try:
                subprocess.run(
                    ["git", "pull"],
                    cwd=self.mamico_local_path,
                    text=True,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Checkout the given branch/tag/commit
            try:
                subprocess.run(
                    ["git", "checkout", mamico_branch_tag_commit],
                    cwd=self.mamico_local_path,
                    text=True,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Determine the latest commit hash
            mamico_commit = self.get_latest_commit(directory=self.mamico_local_path)
            self.config_mamico.update({
                'mamico_branch_tag_commit': mamico_commit
            })
            detail_text = ""
            if mamico_commit != mamico_branch_tag_commit:
                detail_text = f"\n - commit: '{mamico_commit}'."
            # Print a message that MaMiCo is up-to-date
            rich_print(
                Panel(
                    f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}' is up-to-date."\
                    f"{detail_text}",
                    title="[green]MaMiCo is now locally available[/green]",
                    border_style="green",
                    expand=False,
                )
            )

        # Check if the user want to use ls1-mardyn
        if need_ls1:
            if len(os.listdir(os.path.join(self.mamico_local_path, "ls1"))) == 0:
                rich_print(
                    Panel(
                        f"Please wait until branch/tag/commit "\
                        f"'{ls1_branch_tag_commit}' is available locally.\n"\
                        f"This may take a while.""",
                        title="[pink1]Downloading ls1-mardyn[/pink1]",
                        border_style="pink1",
                        expand=False,
                    )
                )
            # Pull ls1 whether locally already available or not
            # This also checks out the default branch/tag/commit that is given in the MaMiCo repository
            try:
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--recursive"],
                    cwd=self.mamico_local_path,
                    text=True,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Check if using a specific branch/tag/commit for ls1-mardyn
            if ls1_branch_tag_commit is not None:
                try:
                    subprocess.run(
                        ["git", "checkout", ls1_branch_tag_commit],
                        cwd=os.path.join(self.mamico_local_path, "ls1"),
                        text=True,
                        capture_output=True,
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(e.stderr)
                    return
            rich_print(
                Panel(
                    f"ls1-mardyn branch/tag/commit '{ls1_branch_tag_commit}' is up-to-date.",
                    title="[green]ls1-mardyn is now locally available[/green]",
                    border_style="green",
                    expand=False,
                )
            )
            self.config_mamico.update({
                'ls1_branch_tag_commit': self.get_latest_commit(directory=os.path.join(self.mamico_local_path, "ls1"))
            })
        else:
            # Remove ls1 folder if not needed
            shutil.rmtree(os.path.join(self.mamico_local_path, "ls1"), ignore_errors=True)
            # Recreate empty folder ls1
            os.makedirs(os.path.join(self.mamico_local_path, "ls1"), exist_ok=True)

    def determine_md5(self):
        """
        Determine the MD5 checksum of the user configuration content and print it to the command line.

        Returns:
            str: The MD5 checksum
        """
        checksum = self._determine_md5(self.config_mamico)
        rich_print(
            Panel(
                "{}".format(checksum),
                title=f"[green]MD5 Checksum:[/green]",
                border_style="green",
                expand=False,
            )
        )
        return checksum

    def _determine_md5(self, input_data):
        """
        Determine the MD5 checksum of the input data.

        Args:
            input_data (dict): The user configuration content
        
        Returns:
            str: The MD5 checksum
        """
        # TODO: maybe clean up the configuration?
        string_stream = io.StringIO()
        yaml.dump(self.config_mamico, string_stream, sort_keys=True, indent=2)
        checksum = hashlib.md5(string_stream.getvalue().encode('utf-8')).hexdigest()
        self.config_mamico.update({ 'mamico_checksum': checksum })
        env.update({ "mamico_checksum": checksum })
        os.makedirs(os.path.join(self.plugin_path, 'tmp', 'checksum_files'), exist_ok=True)
        with open(os.path.join(self.plugin_path, 'tmp', 'checksum_files', f'{checksum}.yml'), 'w') as f:
            f.write(string_stream.getvalue())
        return checksum

    def check_mamico_availability(self, output=True):
        """
        Check whether MaMiCo is already available on the remote machine.

        Returns:
            bool: True if MaMiCo is already available, False otherwise
        """
        try:
            run(
                f'test -d {env.mamico_dir}/{env.mamico_checksum}/build',
                capture=True
            )
            run(
                f'[ -e {env.mamico_dir}/{env.mamico_checksum}/build/couette ]',
                capture=True
            )
            if output:
                rich_print(
                    Panel(
                        f"The MaMiCo source code and executable are already available here:\n" \
                        f"{env.mamico_dir}/{env.mamico_checksum}",
                        title=f"[green]MaMiCo is available on {env.host}[/green]",
                        border_style="green",
                        expand=False,
                    )
                )
            return True
        except Exception as e:
            return False


    def get_latest_commit(self, directory: str = None):
        """
        Get the latest commit hash of the given directory.

        Args:
            directory (str): The directory to get the latest commit hash from
        
        Returns:
            str: The latest commit hash
        """
        res = subprocess.run(["git rev-parse HEAD"],
                        cwd=directory, capture_output=True, shell=True, check=True)
        return res.stdout.decode('utf-8').strip()


    def transfer_to_remote_host(self):
        """
        Transfer the MaMiCo source code to the remote host.
        """
        need_ls1 = self.config_mamico.get('need_ls1', False)
        rich_print(
            Panel(
                f"Please wait until the source code of MaMiCo"\
                f"{ ' and ls1-mardyn are' if need_ls1 else ' is' }"\
                f" copied to {env.host}.",
                title=f"[pink1]Transferring MaMiCo"\
                    f"{ ' & ls1-mardyn' if need_ls1 else '' }[/pink1]",
                border_style="pink1",
            )
        )
        # Copy MaMiCo to the remote machine
        rsync_project(
            local_dir=self.mamico_local_path,
            remote_dir=os.path.join(env.mamico_dir, env.mamico_checksum),
            exclude=['.git/', '.github/', '.gitignore', '.gitmodules'],
            delete=True,
            quiet=True
        )
        # Print success message
        rich_print(
            Panel(
                f"MaMiCo{' and ls1-mardyn were' if need_ls1 else ' was'} "\
                f"successfully copied to {os.path.join(env.mamico_dir, env.mamico_checksum)}.",
                title=f"[green]Transfer to {env.host} succeeded[/green]",
                border_style="green"
            )
        )

    def generate_compile_command(self):
        """
        Generate the command to compile MaMiCo.

        Returns:
            str: The command to compile MaMiCo
        """
        txt = ""
        txt += f"cd {os.path.join(env.mamico_dir, env.mamico_checksum)}\n"
        txt += "cmake -S. -Bbuild"
        if self.config_mamico.get('use_mpi', False):
            txt += " -DBUILD_WITH_MPI=ON"
        if self.config_mamico.get('need_ls1', False):
            txt += " -DMD_SIM='LS1_MARDYN'"
        txt += "\n"
        txt += f"cmake --build build -- -j{env.compile_threads}"
        return txt

    def save_config_yml(self):
        """
        Transfer the config file to the remote machine.

        Returns:
            None
        """
        local(
            f"scp -q -o LogLevel=QUIET {os.path.join(self.plugin_path, 'tmp/checksum_files', f'{env.mamico_checksum}.yml')} "\
            f"{env.host}:{os.path.join(env.mamico_dir, env.mamico_checksum, 'compilation_info.yml')}"
        )
