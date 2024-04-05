import os
import yaml
import shutil
import subprocess

from rich import print as rich_print
from rich.panel import Panel

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *


class MaMiCoSetup():
    def __init__(self, plugin_filepath: str, config: str):
        """
        Set up class variable 'plugin_filepath' and read the user configuration file 'mamico_user_config.yml'.

        Args:
            plugin_filepath (str): The absolute filepath to the plugin's root directory
        """
        self.plugin_filepath = plugin_filepath
        self.config = config
        self.mamico_local_path = f"{plugin_filepath}/tmp/MaMiCo"


    def read_user_config(self):
        with open(f"{self.plugin_filepath}/config_files/{self.config}/mamico_user_config.yml", 'r') as config_file:
            try:
                self.user_config = yaml.safe_load(config_file)
            except yaml.YAMLError as exception:
                print(exception)


    def download_mamico(self):
        """
        Dependent on the user's configuration, (download and) set the given branch/tag/commit.
        """
        # Check if the user specified a branch/tag/commit for MaMiCo, otherwise use 'master'
        try:
            mamico_branch_tag_commit = self.user_config['mamico_branch_tag_commit']
        except KeyError:
            print("No branch/tag/commit specified for MaMiCo: using 'master' as default.")
            mamico_branch_tag_commit = "master"

        # Check if the user want to use ls1-mardyn
        try:
            need_ls1 = self.user_config['need_ls1']
        except KeyError:
            need_ls1 = False

        # Check if the user specified a branch/tag/commit for ls1-mardyn, otherwise use 'master'
        if need_ls1:
            try:
                ls1_branch_tag_commit = self.user_config['ls1_branch_tag_commit']
            except KeyError:
                print("No branch/tag/commit specified for ls1-mardyn: using the default given in MaMiCo repository.")
                ls1_branch_tag_commit = None


        # Check whether MaMiCo folder is already available locally
        if not os.path.isdir(f"{self.plugin_filepath}/tmp/MaMiCo"):
            # Download MaMiCo and checkout the given branch/tag/commit
            rich_print(
                Panel(
                    "{}".format(f"Please wait until branch/tag/commit '{mamico_branch_tag_commit}' is available locally."),
                    title="[pink1]Downloading MaMiCo[/pink1]",
                    border_style="pink1",
                    expand=False,
                )
            )
            # Clone MaMiCo from GitHub
            try:
                subprocess.run(
                    [f"git clone https://github.com/HSU-HPC/MaMiCo.git {self.mamico_local_path}"],
                    shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            try:
                subprocess.run(
                    ["git", "checkout", mamico_branch_tag_commit],
                    cwd=self.mamico_local_path, capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            rich_print(
                Panel(
                    f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}' was successfully cloned to {self.plugin_filepath}/tmp/MaMiCo.",
                    title="[green]MaMiCo Download successful[/green]",
                    border_style="green",
                    expand=False,
                )
            )

        else:
            # MaMiCo is already downloaded locally
            # Checkout to master to be able to pull latest changes (this is not possible with checked out tags/commits)
            try:
                subprocess.run(["git", "checkout", "master"],
                               cwd=self.mamico_local_path, text=True, capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Pull the latest changes and all branches/tags/commits
            try:
                subprocess.run(["git", "pull"],
                               cwd=self.mamico_local_path, text=True, capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Checkout the given branch/tag/commit
            try:
                subprocess.run(["git", "checkout", f"{mamico_branch_tag_commit}"],
                               cwd=self.mamico_local_path, text=True, capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return

            rich_print(
                Panel(
                    f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}' is up-to-date.",
                    title="[green]MaMiCo is now locally available[/green]",
                    border_style="green",
                    expand=False,
                )
            )

        # Check if the user want to use ls1-mardyn
        if need_ls1:
            if len(os.listdir(f"{self.mamico_local_path}/ls1/")) == 0:
                rich_print(
                    Panel(
                        "{}".format(f"Please wait until branch/tag/commit '{ls1_branch_tag_commit}' is available locally."),
                        title="[pink1]Downloading ls1-mardyn[/pink1]",
                        border_style="pink1",
                        expand=False,
                    )
                )
            # Pull ls1 in whether locally already available or not
            # This also checks out the default branch/tag/commit that is given in the MaMiCo repository
            try:
                subprocess.run(["git submodule update --init --recursive"],
                                cwd=self.mamico_local_path, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Check if using a specific branch/tag/commit for ls1-mardyn
            if ls1_branch_tag_commit is not None:
                print(f"{self.mamico_local_path}/ls1/")
                try:
                    subprocess.run(["git", "checkout", f"{ls1_branch_tag_commit}"],
                                    cwd=f"{self.mamico_local_path}/ls1/", text=True, capture_output=True, check=True)
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
        else:
            # Remove ls1 folder if not needed
            shutil.rmtree(f"{self.mamico_local_path}/ls1/", ignore_errors=True)
            # Rereate empty folder ls1
            os.makedirs(f"{self.mamico_local_path}/ls1/")

    def transfer_to_remote_host(self):
        """
        Transfer the MaMiCo source code to the remote host.
        """
        rich_print(
            Panel(
                "{}".format(f"Please wait until the source code of MaMiCo{ ' and ls1-mardyn are' if self.user_config['need_ls1'] else ' is'} copied to remote machine."),
                title=f"[pink1]Transferring MaMiCo{ ' & ls1-mardyn' if self.user_config['need_ls1'] else '' }[/pink1]",
                border_style="pink1",
                expand=False,
            )
        )
        rsync_project(
            local_dir=self.mamico_local_path,
            remote_dir=f"/beegfs/home/m/michaelj/FabSim/MaMiCo/",
            exclude=['.git/', '.github/', '.gitignore', '.gitmodules'],
            delete=True,
            quiet=True
        )
        rich_print(
            Panel(
                f"MaMiCo{' and ls1-mardyn were' if self.user_config['need_ls1'] else ' was'} successfully copied to the remote machine.",
                title="[green]Transfer succeeded[/green]",
                border_style="green",
                expand=False
            )
        )

    def load_dependencies(self):
        """
        Load the dependencies for MaMiCo.
        """
