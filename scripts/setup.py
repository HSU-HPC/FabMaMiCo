import os
import yaml
import shutil
import subprocess
import hashlib
import io

from rich import print as rich_print
from rich.panel import Panel

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from plugins.FabMaMiCo.scripts.utils.functions import *
from plugins.FabMaMiCo.scripts.main_configuration import MainConfiguration

class Setup():
    def __init__(self, plugin_filepath: str, config: str, configuration: MainConfiguration):
        """
        TODO: write docstring

        Args:
            plugin_filepath (str): The path to the plugin
            configuration (MainConfiguration): The main configuration object
        """
        self.plugin_filepath = plugin_filepath
        self.config = config
        self.configuration = configuration
        self.tmp_local_path = os.path.join(plugin_filepath, "tmp")
        self.mamico_local_path = os.path.join(self.tmp_local_path, "MaMiCo")

    def prepare_local(self):
        """
        Prepare the local machine for the MaMiCo installation.
        This includes reading the user configuration file, checking the configuration,
        downloading MaMiCo from GitHub, checking out the given branch/tag/commit,
        optionally downloading ls1-mardyn, checking out the given branch/tag/commit,
        determining the MD5 checksum of the cleaned user configuration,
        and updating the environment variables.

        Returns:
            None
        """
        # Make MaMiCo source code available on the local machine
        self._download_mamico()
        # Make ls1-mardyn source code available on the local machine
        if self.configuration.configs['MaMiCo'].get('use_ls1'):
            self._download_ls1()
        else:
            self._remove_ls1()
        # TODO: maybe prepare more dependencies here
        # self.dependencies = MaMiCoDependencies(self.plugin_filepath, self.conf)
        # self.dependencies.set_deps_from_conf()

    def prepare_remote(self):
        """
        Prepare the remote machine for the MaMiCo installation.
        This includes setting the environment paths, creating the necessary directories,
        copying the configuration files, checking if MaMiCo is already installed,
        and transferring MaMiCo to the remote machine.

        Returns:
            bool: True if MaMiCo is not yet available on the remote machine, False otherwise
        """
        # - set env paths (with_config(config))
        # - if not yet available, create scripts/, config_files/ and 
        #   results/ directories on remote host
        # - copy config_files directory to remote machine (entirely)
        execute(put_configs, self.config)
        # prepare installation directory for MaMiCo
        run(f"mkdir -p {env.mamico_dir}")
        # check if MaMiCo is already installed
        if self._check_mamico_availability(output=True):
            sys.exit(0)
        # transfer source code to remote host
        self._transfer_to_remote_host()
        return

    def compile(self, **args):
        """
        Compile MaMiCo on the remote machine.
        This includes generating the compilation command, updating the environment,
        submitting the compilation job, and putting the configuration yml-file to the
        remote build directory.
        """

        # compile ls1-mardyn if necessary
        if self.configuration.configs['MaMiCo'].get('use_ls1'):
            compile_command_ls1 = self._generate_ls1_compile_command()
            update_environment({ 'compilation_command_ls1': compile_command_ls1 })

        # generate the command for compilation
        compile_command = self._generate_mamico_compile_command()
        # add compilation command to env to be inserted into template script
        update_environment({ 'compilation_command_mamico': compile_command })

        # run/submit compilation job on login/compute node
        if env.get("compile_on_login_node", False):
            print_box(
                title="Compiling MaMiCo on login node",
                message="Please wait until MaMiCo is compiled on the login node."
            )
            # update job_dispatch to bash
            old_job_dispatch = env["job_dispatch"]
            update_environment({"job_dispatch": "bash"})

        # submit job to compile MaMiCo
        job(dict(script='compile'), args)

        # reset job_dispatch to its original value
        if env.get("compile_on_login_node", False):
            update_environment({"job_dispatch": old_job_dispatch})
        
        self._save_config_to_build_dir()

    def determine_md5(self):
        """
        Determine the MD5 checksum of the cleaned user configuration.
        Saves the MD5 checksum in the environment variable 'mamico_checksum'.
        Saves the cleaned user configuration to a file `<checksum>.yml` in the tmp folder.

        Returns:
            str: The MD5 checksum
        """
        # Write yaml to string
        string_stream = io.StringIO("")
        yaml.dump(self.conf.config, string_stream, sort_keys=True, indent=2)

        checksum = hashlib.md5(string_stream.getvalue().encode('utf-8')).hexdigest()
        env["mamico_checksum"] = checksum

        rich_print(
            Panel(
                f"{checksum}",
                title=f"[green]MD5 Checksum:[/green]",
                border_style="green",
                expand=False,
            )
        )

        with open(os.path.join(self.plugin_filepath, "tmp/", f"{checksum}.yml"), 'w') as f:
            f.write(string_stream.getvalue())
            print(f"Corresponding config file '{checksum}.yml' saved to tmp folder.\n")
        return checksum

    def _download_mamico(self):
        """
        Download MaMiCo from github if not already available locally.
        Check out the given branch/tag/commit.

        Returns:
            str: The commit hash of the checked out MaMiCo branch/tag/commit
        """
        mamico_commit = None
        mamico_branch_tag_commit = self.configuration.configs['MaMiCo'].get('mamico_branch_tag_commit')

        # Check whether MaMiCo folder is already available locally
        if not os.path.isdir(self.mamico_local_path):
            ##########
            ## Download MaMiCo and checkout the given branch/tag/commit
            ##########
            # Print message
            print_box(
                f"Please wait until branch/tag/commit '{mamico_branch_tag_commit}' "\
                f"is available locally.",
                title="Downloading MaMiCo",
                color="pink1"
            )
            # Clone MaMiCo from GitHub
            try:
                subprocess.run(
                    [f"git clone https://github.com/HSU-HPC/MaMiCo.git {self.mamico_local_path}"],
                    shell=True, # needed to see the output live
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error cloning MaMiCo repository to {self.mamico_local_path}:", e.stderr)
                raise e
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
                print(f"Error checking out MaMiCo '{mamico_branch_tag_commit}':", e.stderr)
                raise e
            # Get the latest commit hash and update the configuration
            mamico_commit = get_latest_commit_local(directory=self.mamico_local_path)
            self.configuration.configs['MaMiCo'].update({ 'mamico_branch_tag_commit': mamico_commit })
            # Print success message
            detail_text = ""
            if mamico_commit != mamico_branch_tag_commit:
                detail_text = f"\n - commit: '{mamico_commit}'."
            print_box(
                f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}'\n"\
                f"was successfully cloned to {self.mamico_local_path}."\
                f"{detail_text}",
                title="MaMiCo Download successful",
                color="green"
            )
        else:
            ##########
            ## MaMiCo is already downloaded locally
            ##########
            # Checkout master to pull latest changes
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
                print("Error checking out master branch of MaMiCo:", e.stderr)
                raise e
            # Pull the latest changes for all branches/tags/commits
            try:
                subprocess.run(
                    ["git", "pull"],
                    cwd=self.mamico_local_path,
                    text=True,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print("Error pulling latest changes of MaMiCo:", e.stderr)
                raise e
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
                print("Error checking out MaMiCo branch/tag/commit:", e.stderr)
                raise e
            # Get the latest commit hash and update the configuration
            mamico_commit = get_latest_commit_local(directory=self.mamico_local_path)
            self.configuration.configs['MaMiCo'].update({ 'mamico_branch_tag_commit': mamico_commit })
            # Print success message
            detail_text = ""
            if mamico_commit != mamico_branch_tag_commit:
                detail_text = f"\n - commit: {mamico_commit}"
            print_box(
                f"MaMiCo branch/tag/commit '{mamico_branch_tag_commit}' is up-to-date."\
                f"{detail_text}",
                title="MaMiCo is now locally available",
                color="green"
            )
        return mamico_commit

    def _download_ls1(self):
        """
        Download ls1-mardyn if instructed by the user-configuration.
        Check out the given branch/tag/commit for ls1-mardyn.
        """
        ls1_commit = None
        ls1_branch_tag_commit = self.configuration.configs['ls1-mardyn'].get('ls1_branch_tag_commit')

        # Check whether the ls1 folder contains any files already
        if len(os.listdir(f"{self.mamico_local_path}/ls1/")) == 0:
            print_box(
                f"Please wait until branch/tag/commit '{ls1_branch_tag_commit}' is available locally.\n"\
                f"This may take a while. Please be patient.",
                title="Downloading ls1-mardyn",
                color="pink1",
            )
        # Pull ls1 whether locally already available or not
        # If available, this checks out the default branch/tag/commit that is given in the MaMiCo repository
        try:
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=self.mamico_local_path,
                text=True,
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print("Error pulling ls1 source code:", e.stderr)
            raise e
        # Check if using a specific branch/tag/commit for ls1-mardyn
        if ls1_branch_tag_commit is not None:
            try:
                subprocess.run(
                    ["git", "checkout", ls1_branch_tag_commit],
                    cwd=f"{self.mamico_local_path}/ls1/",
                    text=True,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print("Error checking out the ls1 repository:", e.stderr)
                raise e
        ls1_commit = get_latest_commit_local(directory=f"{self.mamico_local_path}/ls1/")
        self.configuration.configs['ls1-mardyn'].update({ 'ls1_branch_tag_commit': ls1_commit })
        print_box(
            f"ls1-mardyn branch/tag/commit '{ls1_branch_tag_commit}' is up-to-date.\n"\
            f" - commit {ls1_commit}",
            title="ls1-mardyn is now locally available",
            color="green"
        )

    def _remove_ls1(self):
        """
        Remove the ls1-mardyn folder if it exists.
        """
        shutil.rmtree(f"{self.mamico_local_path}/ls1/", ignore_errors=True)
        # Recreate empty folder ls1
        os.makedirs(f"{self.mamico_local_path}/ls1/")

    def _check_mamico_availability(self, output=True):
        """
        Check whether MaMiCo build directory and the executable 'couette' 
        is already available on the remote machine.

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
                print_box(
                    f"The MaMiCo source code and executable are already available here:\n" \
                    f"{env.mamico_dir}/{env.mamico_checksum}",
                    title=f"MaMiCo is available on {env.host}",
                    color="green"
                )
            return True
        except Exception as e:
            return False

    def _transfer_to_remote_host(self):
        """
        Transfer the MaMiCo source code to the remote host.

        Returns:
            None
        """
        use_ls1 = self.configuration.configs['MaMiCo'].get('use_ls1')
        # Print message
        print_box(
            f"Please wait until the source code of MaMiCo"\
            f"{ ' and ls1-mardyn are' if use_ls1 else ' is' }"\
            f" copied to {env.host}.",
            title=f"Transferring MaMiCo"\
                  f"{ ' & ls1-mardyn' if use_ls1 else '' }",
            color="pink1",
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
        print_box(
            f"MaMiCo{' and ls1-mardyn were' if use_ls1 else ' was'} "\
            f"successfully copied to {os.path.join(env.mamico_dir, env.mamico_checksum)}.",
            title=f"Transfer to {env.host} succeeded",
            color="green"
        )

    def _generate_ls1_compile_command(self):
        """
        Generate the command to compile ls1-mardyn.

        Returns:
            str: The command to compile ls1-mardyn.
        """
        txt = ""
        txt += f"cd {env.mamico_dir}/{env.mamico_checksum}/ls1\n"
        txt += f"CC=gcc CXX=g++ cmake -S. -Bbuild"
        txt += f" -DMAMICO_SRC_DIR={env.mamico_dir}/{env.mamico_checksum}"
        txt += " -DMAMICO_COUPLING=ON"
        for key, value in self.configuration.configs['ls1-mardyn'].get_cleaned().items():
            if key in self.configuration.configs['ls1-mardyn'].non_cmake_flags: continue
            if type(value) == bool:
                txt += f" -D{key}={'ON' if value else 'OFF'}"
            else:
                txt += f" -D{key}={value}"
        txt += "\n"
        txt += f"cmake --build build -- -j{env.compile_threads}"
        return txt

    def _generate_mamico_compile_command(self):
        """
        Generate the command to compile MaMiCo.

        Returns:
            str: The command to compile MaMiCo.
        """
        txt = ""
        txt += f"cd {os.path.join(env.mamico_dir, env.mamico_checksum)}\n"
        txt += f"export MAKEFLAGS=-j{env.compile_threads}\n"
        txt += "cmake -S. -Bbuild"
        for key, value in self.configuration.configs['MaMiCo'].get_cleaned().items():
            if key in self.configuration.configs['MaMiCo'].non_cmake_flags: continue
            if type(value) == bool:
                txt += f" -D{key}={'ON' if value else 'OFF'}"
            else:
                txt += f" -D{key}={value}"
        txt += "\n"
        txt += f"cmake --build build -- -j{env.compile_threads}"
        return txt

    def _save_config_to_build_dir(self):
        """
        Transfer the config file to the remote machine.

        Returns:
            None
        """
        local(
            f"scp -q -o LogLevel=QUIET {os.path.join(self.plugin_filepath, 'tmp/checksum_files', f'{env.mamico_checksum}.yml')} "\
            f"{env.host}:{os.path.join(env.mamico_dir, env.mamico_checksum, 'build/compilation_info.yml')}"
        )
