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
    def __init__(self, plugin_filepath: str, config: str):
        """
        Set up class variable 'plugin_filepath' and read the user
        configuration file 'mamico_user_config.yml'.

        Args:
            plugin_filepath (str): The absolute filepath to the plugin's root directory
        """
        self.plugin_filepath = plugin_filepath
        self.config = config
        self.mamico_local_path = f"{plugin_filepath}/tmp/MaMiCo"


    def read_config(self):
        """
        Read the user configuration files `config_mamico.yml` and
        `config_simulation.yml` and store them in class variables.

        Returns:
            None
        """
        # Read the config_mamico.yml
        config_mamico_path = f"{self.plugin_filepath}/config_files/{self.config}/config_mamico.yml"
        with open(config_mamico_path, 'r') as config_mamico_file:
            try:
                self.config_mamico = yaml.safe_load(config_mamico_file)
            except yaml.YAMLError as exception:
                print(exception)
        # Read the config_simulation.yml
        # config_simulation_path = f"{self.plugin_filepath}/config_files/{self.config}/config_simulation.yml"
        # with open(config_simulation_path, 'r') as config_simulation_file:
        #     try:
        #         self.config_simulation = yaml.safe_load(config_simulation_file)
        #     except yaml.YAMLError as exception:
        #         print(exception)


    def download_mamico(self):
        """
        Download MaMiCo from github if not already available locally.
        Check out the given branch/tag/commit.
        Optionally download ls1-mardyn if instructed by the user-configuration.
        Check out the given branch/tag/commit for ls1-mardyn.

        Returns:
            None
        """
        # Check if the user specified a branch/tag/commit for MaMiCo, otherwise use 'master'
        try:
            mamico_branch_tag_commit = self.config_mamico['mamico_branch_tag_commit']
        except KeyError:
            print("No branch/tag/commit specified for MaMiCo: using 'master' as default.")
            mamico_branch_tag_commit = "master" # jmToDo: clarify if this will ever be changed to e.g. 'main'

        # Check if the user wants to use ls1-mardyn
        try:
            need_ls1 = self.config_mamico['need_ls1']
        except KeyError:
            need_ls1 = False

        if need_ls1:
            # If the user wants to use ls1-mardyn, check if the user specified
            #   a branch/tag/commit for ls1-mardyn, otherwise use 'master'
            try:
                ls1_branch_tag_commit = self.config_mamico['ls1_branch_tag_commit']
            except KeyError:
                print("No branch/tag/commit specified for ls1-mardyn: using \
                      the default value defined in the MaMiCo repository.")
                ls1_branch_tag_commit = None

        # Check whether MaMiCo folder is already available locally
        if not os.path.isdir(f"{self.plugin_filepath}/tmp/MaMiCo"):
            # Download MaMiCo and checkout the given branch/tag/commit
            rich_print(
                Panel(
                    f"Please wait until branch/tag/commit '{mamico_branch_tag_commit}' \
                        is available locally.",
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
                    f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}' was \
                        successfully cloned to {self.plugin_filepath}/tmp/MaMiCo.",
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
        
        self.config_mamico.update({
            'mamico_branch_tag_commit': self.get_latest_commit(directory=self.mamico_local_path)
        })

        # Check if the user want to use ls1-mardyn
        if need_ls1:
            if len(os.listdir(f"{self.mamico_local_path}/ls1/")) == 0:
                rich_print(
                    Panel(
                        f"""Please wait until branch/tag/commit \
                            '{ls1_branch_tag_commit}' is available locally.\n\
                            This may take a while.""",
                        title="[pink1]Downloading ls1-mardyn[/pink1]",
                        border_style="pink1",
                        expand=False,
                    )
                )
            # Pull ls1 whether locally already available or not
            # This also checks out the default branch/tag/commit that is given in the MaMiCo repository
            try:
                subprocess.run(["git submodule update --init --recursive"],
                                cwd=self.mamico_local_path, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                return
            # Check if using a specific branch/tag/commit for ls1-mardyn
            if ls1_branch_tag_commit is not None:
                try:
                    subprocess.run(["git", "checkout", f"{ls1_branch_tag_commit}"],
                                    cwd=f"{self.mamico_local_path}/ls1/",
                                    text=True,
                                    capture_output=True,
                                    check=True)
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
                'ls1_branch_tag_commit': self.get_latest_commit(directory=f"{self.mamico_local_path}/ls1/")
            })

        else:
            # Remove ls1 folder if not needed
            shutil.rmtree(f"{self.mamico_local_path}/ls1/", ignore_errors=True)
            # Rereate empty folder ls1
            os.makedirs(f"{self.mamico_local_path}/ls1/")
            # jmToDo: remove every variable related to ls1-mardyn or unused ones
            del self.config_mamico['ls1_branch_tag_commit']

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
        checksum = hashlib.md5(json.dumps(input_data, sort_keys=True).encode('utf-8')).hexdigest()
        self.config_mamico.update({'md5_checksum': checksum })
        env["md5_checksum"] = checksum
        return checksum

    def check_mamico_availability(self):
        """
        Check whether MaMiCo is already available on the remote machine.

        Returns:
            bool: True if MaMiCo is already available, False otherwise
        """
        try:
            run(f'test -d {env.mamico_dir}/{env.md5_checksum}/build', capture=True)
            rich_print(
                Panel(
                    f"""The MaMiCo source code and executables are already \
                        available here:\n{env.mamico_dir}/{env.md5_checksum}""",
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
        rich_print(
            Panel(
                f"Please wait until the source code of MaMiCo\
                    { ' and ls1-mardyn are' if self.config_mamico['need_ls1'] else ' is'} copied to {env.host}.",
                title=f"[pink1]Transferring MaMiCo{ ' & ls1-mardyn' if self.config_mamico['need_ls1'] else '' }[/pink1]",
                border_style="pink1",
                expand=False,
            )
        )
        rsync_project(
            local_dir=self.mamico_local_path,
            remote_dir=f"{env.mamico_dir}/{env.md5_checksum}/",
            exclude=['.git/', '.github/', '.gitignore', '.gitmodules'],
            delete=True,
            # quiet=True
        )
        rich_print(
            Panel(
                f"MaMiCo{' and ls1-mardyn were' if self.config_mamico['need_ls1'] else ' was'} \
                    successfully copied to {env.mamico_dir}/{env.md5_checksum}.",
                title=f"[green]Transfer to {env.host} succeeded[/green]",
                border_style="green",
                expand=False
            )
        )


    # def compile_mamico_on_login_node(self):
    #     """
    #     Calls the compile script and class to compile on login node.
    #     """
    #     # Copy the scripts remote directory to the remote machine
    #     rsync_project(
    #         local_dir=f"{self.plugin_filepath}/scripts/remote/",
    #         remote_dir=f"{env.scripts_path}/remote/",
    #         exclude=['__pycache__'],
    #         delete=True
    #     )

    #     print(self.config)
    #     # Copy the pickle file
    #     rsync_project(
    #         local_dir=f"{self.plugin_filepath}/tmp/configs",
    #         remote_dir=f"{env.scripts_path}/remote/configs",
    #         delete=True
    #     )

    #     compile_script_path = f"{env.scripts_path}/remote/compile.py"
    #     config_filepath = f"{env.scripts_path}/remote/configs/{self.config}.env.pkl"
    #     plugin_path = env.remote_path
    #     try:
    #         # jmToDo: we assume, python3 is callable by default
    #         output = run(f'''python3 {compile_script_path} --config={self.config} \
    #                      --config_filepath={config_filepath} --plugin_path={plugin_path}''',
    #                     cd=f"{env.scripts_path}/remote/",
    #                     capture=True)
    #         print(output)
    #     except Exception as e:
    #         print(e)
    #         raise e


    def generate_compile_command(self):
        """
        Generate the command to compile MaMiCo.

        Returns:
            str: The command to compile MaMiCo
        """
        txt = ""
        txt += f"cd {env.mamico_dir}/{env.md5_checksum}; "
        txt += "cmake -S. -Bbuild "
        # jmToDo: implement cmake flags etc.
        if self.config_mamico['use_mpi']:
            txt += "-DBUILD_WITH_MPI=ON "
        # ...
        txt += "; "
        txt += "cmake --build build; "
        return txt


    def list_installations(self):
        """
        List all MaMiCo installations on the remote machine.

        Returns:
            None
        """
        rich_print(
            Panel(
                "{}".format(f"Please wait until the MaMiCo installations on {env.host} are listed."),
                title="[pink1]Listing MaMiCo installations[/pink1]",
                border_style="pink1",
                expand=False,
            )
        )
        installations = run(f"ls {env.mamico_dir}", capture=True)
        rich_print(
            Panel(
                "\n".join(installations.split()),
                title=f"[green]Found {len(installations.split())} installations on {env.host}[/green]",
                border_style="green",
                expand=False
            )
        )


    def clean_installation(self):
        """
        Remove a single MaMiCo installation directory on the remote machine.

        Returns:
            None
        """
        mamico_dir = f"{env.mamico_dir}/{env.md5_checksum}"
        print(mamico_dir)
        rich_print(
            Panel(
                "{}".format(f"Please wait until the MaMiCo installation {env.md5_checksum} is removed."),
                title=f"[pink1]Cleaning MaMiCo installation on {env.host}[/pink1]",
                border_style="pink1",
                expand=False,
            )
        )
        output = run(f"rm -rf {env.mamico_dir}/{env.md5_checksum}", capture=True)
        print(output)
        rich_print(
            Panel(
                f"{env.mamico_dir}/{env.md5_checksum} was removed from the remote machine.",
                title="[green]Clean up successful[/green]",
                border_style="green",
                expand=False
            )
        )

    def clean_installations(self):
        """
        Remove the MaMiCo installation directory on the remote machine.

        Returns:
            None
        """
        rich_print(
            Panel(
                "{}".format(f"Please wait until all MaMiCo installations on {env.host} are removed."),
                title="[pink1]Cleaning MaMiCo installations[/pink1]",
                border_style="pink1",
                expand=False,
            )
        )
        output = run(f"rm -rf {env.mamico_dir}/*", capture=True)
        print(output)
        rich_print(
            Panel(
                f"MaMiCo was successfully removed from the remote machine.",
                title="[green]Clean up successful[/green]",
                border_style="green",
                expand=False
            )
        )
