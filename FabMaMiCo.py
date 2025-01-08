# -*- coding: utf-8 -*-
#
# This file contains FabSim definitions specific to FabMaMiCo.

import os

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from rich.console import Console
from rich.panel import Panel
from rich.table import Table, box

from fabsim.deploy.templates import template
from plugins.FabMaMiCo.scripts.settings import Settings
from plugins.FabMaMiCo.scripts.setup import MaMiCoSetup

# from plugins.FabMaMiCo.scripts.spack_manager import SpackManager

# Add local script, blackbox and template path.
add_local_paths("FabMaMiCo")

FABMAMICO_PATH = get_plugin_path("FabMaMiCo")

# ToDo: Implement mechanism to let nested pairs of arguments overwrite each other
def load_args_from_config(config: str, overwrite_nested: bool = True) -> None:
    '''
    Load workflows specific arguments from the config directory's args.yml file, if it exists.
    '''

    path_to_config = find_config_file_path(config)
    path_to_config_args_file = os.path.join(path_to_config, "args.yml")
    if (os.path.exists(path_to_config_args_file)):
        args = yaml.safe_load(
            open(path_to_config_args_file)
        )
        update_environment(args)
        rich_print(
            Panel(
                f"Loaded arguments from {path_to_config_args_file}",
                title="Configuration specific arguments loaded",
                border_style="green",
                expand=False,
            )
        )



##################################################################################################
############################# Plugin Installation Verification ###################################
##################################################################################################

@task
def mamico_test_plugin(**args) -> None:
    """
    Tests the FabMaMiCo plugin installation.
    If this task is callable via `fabsim <machine> mamico_test_plugin`,
    the plugin is installed correctly.
    """
    update_environment(args)
    if env.task == "mamico_test_plugin":
        rich_print(
            Panel(
                f"FabMaMiCo is installed correctly and ready to use.",
                border_style="green",
                expand=False,
            )
        )
    else:
        rich_print(
            Panel(
                "The function 'mamico_test_plugin' was not called as a FabSim task.",
                title="FabMaMiCo is not installed correctly.",
                border_style="red",
                expand=False,
            )
        )


##################################################################################################
################################### Remote Host Probes ###########################################
##################################################################################################

@task
def mamico_mod_overview(**args) -> None:
    """
    Prints an overview of available modules.
    """
    update_environment(args)
    cmd = "module --redirect overview 2>&1"
    output = run(cmd, capture=True)
    rich_print(
        Panel(
            f"The following modules are available on {env.host}:",
            title="Module Overview",
            border_style="blue",
            expand=True,
        )
    )
    print(output)


@task
def mamico_mod_available(query: str = "", **args) -> None:
    """
    Prints a list of available modules.
    Optionally, a query can be provided to filter the list.
    """
    update_environment(args)
    cmd = f"module --redirect available {query} 2>&1"
    output = run(cmd, capture=True)
    box_text = f"The following modules are available on {env.host}:"
    box_text += f" (query: '{query}')" if len(query) > 0 else ""
    rich_print(
        Panel(
            box_text,
            title="Module Availability",
            border_style="blue",
            expand=True,
        )
    )
    print(output)


@task
def mamico_mod_keyword(keyword: str = None, **args) -> None:
    """
    Searches modules by a keyword, given as an argument.
    """
    update_environment(args)
    if keyword is None:
        rich_print(
            Panel(
                f"Please provide a keyword to search for:\n"\
                 "  $ fabsim <machine> mamico_lmod_keyword:<keyword>",
                title="No keyword provided",
                border_style="red",
                expand=False,
            )
        )
        return
    cmd = f"module --redirect keyword {keyword} 2>&1"
    output = run(cmd, capture=True)
    rich_print(
        Panel(
            f"The keyword search for '{keyword}' returned the following modules on {env.host}:",
            title="Module Overview",
            border_style="blue",
            expand=True,
        )
    )
    print(output)


###### WIP ######
# @task
# @load_plugin_env_vars("FabMaMiCo")
# def mamico_mod_test_WIP(template_script: str, **args):
#    """
#     Check if the modules from machines.yml/machines_user.yml are available.
#     """
#     update_environment()
#     print(env.modules[template_script])
#################



##################################################################################################
####################################### Spack tasks ##############################################
##################################################################################################
# @task
# @load_plugin_env_vars("FabMaMiCo")
# def mamico_spack_install(**args) -> None:
#     """
#     Install Spack on the remote machine.
#     """

#     update_environment(args)

#     update_environment({
#         "spack_dir": template(env.spack_dir),
#     })

#     spack_manager = SpackManager()
#     spack_manager.prepare_locally()
#     spack_manager.transfer_to_remote_host()

#     # Clone MaMiCo from GitHub
#     # local(
#     #     f"git clone https://github.com/HSU-HPC/MaMiCo.git {self.local_mamico_path}",
#     #     capture=True
#     # )

#     # download the Spack repository locally
#     # local(f"git clone --depth=2 --branch=releases/v0.23 https://github.com/spack/spack.git ~/spack")

#     # run(f"mkdir -p {spack_dir}")
#     # run(f"git clone --depth=2")


# @task
# @load_plugin_env_vars("FabMaMiCo")
# def mamico_spack_create_env(config, **args) -> None:
#     """
#     Create a Spack environment.
#     """
#     update_environment(args)
#     # spack_dir = template(env.spack_dir)
#     # run(f"mkdir -p {spack_dir}")
#     # run(f"git clone --depth=2

#     env.job_dispatch = "bash -l"

#     run("spack env create myenv spack.yaml")


##################################################################################################
############################ MaMiCo installation housekeeping ####################################
##################################################################################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_install(config: str, only_check: Optional[bool] = False, **args) -> bool:
    """
    Transfers the MaMiCo source code to the remote machine and compiles it with all its dependencies.
    Downloads the MaMiCo source code from the MaMiCo repository and optionally ls1-mardyn and OpenFOAM.
    Checks out the given branch/commit/tag and transfers the source code to the remote machine.
    Then compiles the code on the remote machine, either on the login node or on a compute node.
    """
    # ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # env.job_name_template = f"{env.job_name_template}_{ts}"
    # load_args_from_config(config)
    update_environment(args)
    with_config(config)
    # change job name
    # read the settings from the config_dir/settings.yml
    settings = Settings(FABMAMICO_PATH, config)
    # create instance of MaMiCoSetup (includes setup functionalities)
    mamico_setup = MaMiCoSetup(FABMAMICO_PATH, config, settings)

    # prepare MaMiCo locally
    mamico_commit = mamico_setup.prepare_mamico_locally()
    settings.update({ "mamico_commit": mamico_commit })
    settings.delete("mamico_branch_tag_commit")

    # prepare ls1-mardyn locally
    need_ls1 = settings.get('need_ls1', False)
    ls1_commit = mamico_setup.prepare_ls1_locally(need_ls1=need_ls1)
    if len(ls1_commit) > 0:
        settings.update({ "ls1_commit": ls1_commit })
    settings.delete("ls1_branch_tag_commit")

    # print the settings
    settings.print()

    checksum = settings.determine_md5()
    update_environment({ "mamico_checksum": checksum })

    env.mamico_dir = template(env.mamico_dir)

    # if MaMiCo is already installed, skip the installation
    is_available = mamico_setup.check_mamico_availability(output=True)
    if only_check:
        return is_available
    if is_available:
        print("MaMiCo is already installed.")
        return True

    update_environment({ "cores": 1 })

    # transfer files from config_files to remote machine
    execute(put_configs, config) # also calls with_config()

    # prepare installation directory for MaMiCo
    run(f"mkdir -p {template(env.mamico_dir)}")

    # transfer MaMiCo to remote host
    mamico_setup.transfer_to_remote_host()

    # save the configuration file
    mamico_setup.save_config_yml()

    # generate the command for compilation
    compile_command_ls1 = mamico_setup.generate_compile_command_ls1()
    compile_command_mamico = mamico_setup.generate_compile_command_mamico()
    compile_command_openfoam = mamico_setup.generate_compile_command_openfoam()

    update_environment({
        "compilation_command_openfoam": compile_command_openfoam,
        "compilation_command_ls1": compile_command_ls1,
        "compilation_command_mamico": compile_command_mamico,
    })

    # run/submit compilation job
    if env.get("compile_on_login_node", False):
        #########################
        # COMPILE ON LOGIN NODE #
        #########################
        print("Compiling on login node:")
        # update job_dispatch to bash
        old_job_dispatch = env['job_dispatch']
        old_job_name_template = env['job_name_template']
        old_task = env['task']
        update_environment({
            "task": "mamico_install",
            "job_dispatch": "",
        })
        # execute batch script with bash: `bash <config>_<machine>_1_mamico_install.sh`
        job(dict(script='compile'), args)
        # reset job_dispatch to its original value (for possible subsequent jobs)
        update_environment({
            "task": old_task,
            "job_dispatch": old_job_dispatch,
        })
    else:
        ###########################
        # COMPILE ON COMPUTE NODE #
        ###########################
        print("Compiling on compute node:")
        # submit job to compile MaMiCo
        job(dict(script='compile'), args)

    return True


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_list_installations(**args):
    """
    List all MaMiCo installations on the remote machine.

    Args:
        verbose (bool): Show compilation settings for each installation. Default: False
    """
    update_environment(args)
    rich_print(
            Panel(
            f"Please wait until the MaMiCo installations on {env.host} are listed.",
            title="Listing MaMiCo installations",
            border_style="pink1",
            expand=False,
        )
    )
    # list all directories in the MaMiCo directory
    if env.manual_ssh:
        installations = run(f"ls {template(env.mamico_dir)}", capture=True)
    else:
        installations = run(f"ls {template(env.mamico_dir)}", capture=True)
    
    # if manual_ssh is set, the return is a tuple of (stdout, stderr)
    if env.manual_ssh:
        installations = installations[0]

    # get compilation info from each installation
    if args.get("verbose", False):
        verbose_info = []

        if env.manual_ssh:
            for installation in installations.split():
                a = run(f"cat {template(env.mamico_dir)}/{installation}/build/compilation_info.yml || true", capture=True)
                v = a
                if env.manual_ssh:
                    if len(a[1]) > 0:
                        v = "[red]Compilation seems to have failed.\n" \
                            "No file 'compilation_info.yml' found.[/red]"
                    else:
                        v = a[0]
                verbose_info.append(v)
        else:
            for installation in installations.split():
                try:
                    a = run(f"cat {template(env.mamico_dir)}/{installation}/build/compilation_info.yml", capture=True)
                except Exception as e:
                    a = "[red]Compilation seems to have failed.\n" \
                        "No file 'compilation_info.yml' found.[/red]"
                # remove trailing newline characters
                while a.endswith(('\n', '\r\n')):
                    a = a[:-1]
                verbose_info.append(a)

    # Print the installations as table
    num_installations = len(installations.split())
    title = f"\n[green]Found {num_installations} installation{ 's' if num_installations != 1 else '' } on {env.host}\n"\
        f"at[/green] [white]{template(env.mamico_dir)}[/white]"
    table = Table(
        title=title,
        show_header=True,
        show_lines=args.get("verbose", False),
        box=box.ROUNDED,
        header_style="blue",
    )
    table.add_column("MD5 Checksum", style="white")
    if args.get("verbose", False):
        table.add_column("Compilation Settings", style="white")
    for installation in installations.split():
        if args.get("verbose", False):
            table.add_row(installation, verbose_info.pop(0))
        else:
            table.add_row(installation)
    console = Console()
    console.print(table)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_installation_available(checksum: str, **args):
    update_environment(args)
    env["mamico_checksum"] = checksum
    installation_dir = os.path.join(template(env.mamico_dir), env.mamico_checksum)
    try:
        run(
            f"test -d {installation_dir} && test -f {installation_dir}/build/compilation_info.yml",
            capture=True
        )
        rich_print(
            Panel(
                f"The MaMiCo installation {env.mamico_checksum} is available on {env.host}.",
                title="Installation available",
                border_style="green",
                expand=False,
            )
        )
    except Exception:
        rich_print(
            Panel(
                f"The MaMiCo installation {env.mamico_checksum} is not available on {env.host}.",
                title="Installation not found",
                border_style="red",
                expand=False,
            )
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_remove_installation(checksum: str, **args):
    """
    Removes a specific MaMiCo installation directory on the remote machine.
    """
    update_environment(args)
    env["mamico_checksum"] = checksum
    dir_to_remove = os.path.join(template(env.mamico_dir), env.mamico_checksum)
    # check if the directory exists:
    try:
        run(f"test -d {dir_to_remove}", capture=True)
    except Exception as e:
        rich_print(
            Panel(
                f"The MaMiCo installation {env.mamico_checksum} does not exist on {env.host}.",
                title="Installation not found",
                border_style="red",
                expand=False
            )
        )
        return
    rich_print(
        Panel(
            f"Please confirm the removal of the MaMiCo installation {env.mamico_checksum} on {env.host}.",
            title="Removing MaMiCo installation",
            border_style="pink1",
            expand=False,
        )
    )
    confirmation = input("Y[es] or N[o]: ").lower()
    if confirmation != "y":
        rich_print(
            Panel(
                f"Aborted the removal of MaMiCo installation {env.mamico_checksum} on {env.host}.",
                title="Aborted",
                border_style="red",
                expand=False
            )
        )
        return
    rich_print(
        Panel(
            f"Please wait until the MaMiCo installation {env.mamico_checksum} is removed.",
            title=f"Cleaning MaMiCo installation on {env.host}",
            border_style="pink1",
            expand=False,
        )
    )
    output = run(f"rm -rf {dir_to_remove}", capture=True)
    print(output)
    rich_print(
        Panel(
            f"{dir_to_remove} was removed from the remote machine.",
            title="Clean up successful",
            border_style="green",
            expand=False
        )
    )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_remove_all_installations(**args):
    """
    Removes all MaMiCo installations on the remote machine.
    """
    update_environment(args)
    rich_print(
        Panel(
            f"Please confirm the removal of all MaMiCo installations on {env.host}.",
            title="Removing MaMiCo installations",
            border_style="pink1",
            expand=False,
        )
    )
    confirmation = input("Y[es] or N[o]: ").lower()
    if confirmation != "y":
        rich_print(
            Panel(
                f"Aborted the removal of MaMiCo installations on {env.host}.",
                title="Aborted",
                border_style="red",
                expand=False
            )
        )
        return
    rich_print(
        Panel(
            f"Please wait until the MaMiCo installations are removed.",
            title=f"Removing MaMiCo installations on {env.host}",
            border_style="pink1",
            expand=False,
        )
    )
    output = run(f"rm -rf {template(env.mamico_dir)}/*", capture=True)
    print(output)
    rich_print(
        Panel(
            f"There are no more MaMiCo installations on {env.host}.",
            title="All cleaned up",
            border_style="green",
            expand=False
        )
    )


##################################################################################################
################################### MaMiCo simulations ###########################################
##################################################################################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_run(config: str, **args):
    """
    Run a single MaMiCo simulation.
    This task makes sure that the MaMiCo code is installed and compiled on the remote machine.
    It then copies the necessary input files to the build folder and submits the job.
    """
    load_args_from_config(config)
    update_environment(args)
    with_config(config)
    execute(put_configs, config)

    env.mamico_dir = template(env.mamico_dir)

    # make sure MaMiCo is installed
    mamico_install(config, **args)

    # submit the job
    job(dict(script='run'), args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_run_ensemble(config: str, **args):
    """
    Run an ensemble of MaMiCo simulations.
    This task makes sure that the MaMiCo code is installed and compiled on the remote machine.
    It then copies the necessary input files to the build folder and submits the job ensemble.
    """
    load_args_from_config(config)
    update_environment(args)

    generate_sweep()

    # make sure MaMiCo is installed
    mamico_install(config, **args)

    env.mamico_dir = template(env.mamico_dir)

    path_to_config = find_config_file_path(config)
    print(f"local config file path at: {path_to_config}")
    sweep_dir = os.path.join(path_to_config, "SWEEP")
    env.script = 'run' if args.get("script", None) is None else args.get("script")
    with_config(config)
    run_ensemble(config, sweep_dir, **args)


##################################################################################################
################################## MaMiCo postprocessing #########################################
##################################################################################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_install_venv(**args):
    """
    Create a virtual environment for Python and install the required packages.
    """
    # TODO: Add miniconda installation (?)
    # create the config_files directory and copy the requirements_remote.txt file there
    env['mamico_venv'] = template(env.mamico_venv_template)
    config = "venv_setup"
    local(f"mkdir -p {env.localplugins['FabMaMiCo']}/config_files/{config}")
    local(f"cp {env.localplugins['FabMaMiCo']}/requirements_remote.txt {env.localplugins['FabMaMiCo']}/config_files/{config}/requirements.txt")
    local(f"echo '*' > {env.localplugins['FabMaMiCo']}/config_files/{config}/.gitignore")
    update_environment(args)
    with_config(config)
    # transfer files from config_files to remote machine
    execute(put_configs, config)
    # set the commands for the virtual environment setup
    env['venv_setup_commands'] = "\n".join([
        f"python3 -m venv {env.mamico_venv}",
        f"source {env.mamico_venv}/bin/activate",
        f"pip install -r {env.job_config_path}/requirements.txt",
        # f"rm -rf {env.job_config_path}/"
    ])
    # submit the job
    # TODO: is it a requirement to install via job and not via bash?
    env['job_dispatch'] = "bash -l -c"
    job(dict(script='venv_setup'), args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_postprocess(config: str, script: str = "postprocess.py", py_args: str = "", **args):
    """
    Run a postprocessing Pyhon script in the given config-directory.
    """
    update_environment(args)

    if not os.path.exists(os.path.join(env.localplugins['FabMaMiCo'], "config_files", config, script)):
        rich_print(
            Panel(
                f"The postprocessing script '{script}' does not exist in the config directory '{config}'.",
                title="[red]Script not found[/red]",
                border_style="red",
                expand=False,
            )
        )
        return

    env.postprocess_args = py_args

    with_config(config)
    # execute(put_configs, config)
    # please only transfer the postprocess script
    put(os.path.join(env.localplugins['FabMaMiCo'], "config_files", config, script), env.job_config_path)

    # submit the job
    job_args = {
        'script': 'postprocess',
        'postprocess_script': script,
        'postprocess_args': py_args
    }
    job(job_args, args)


##################################################################################################
################################### MaMiCo monitoring ############################################
##################################################################################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_stat(**args):
    """
    Show the queue of FabMaMiCo-jobs on the remote machine.
    Calls `squeue` and filters the output for FabMaMiCo-jobs.
    """
    update_environment(args)
    output = run(f"squeue --format='%.10i %.9P %.70j %.10u %.8T %.13M %.9l %.6D %R' --me", capture=True)
    output = output.split("\n")
    output = output[0] + "\n" + "\n".join([line for line in output[1:] if "fabmamico_" in line])
    print(output)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_jobs_overview(**args):
    """
    Show the queue of FabMaMiCo-jobs on the remote machine.
    Calls `squeue` and filters the output for FabMaMiCo-jobs.
    """
    update_environment(args)
    output = run(f"squeue --me --noheader --format='%.10i %.70j'", capture=True)
    output = len([l for l in output.split("\n") if "fabmamico_" in l])
    print(f"The user {env.username} currently has {output} FabMaMiCo jobs in the queue.")


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_jobs_cancel_all(**args):
    """
    Cancel all `fabmamico_`-jobs on the remote machine.
    """
    update_environment(args)
    output = run(
        "squeue --me --format='%.10i %.80j' --noheader | grep fabmamico_ | awk '{print $1}' | tail -n+2 | xargs -n 1 scancel",
        capture=True
    )
    print(output)
    print("All MaMiCo jobs have been canceled.")


def generate_sweep(config):
    # populate SWEEP directory if a generate_ensemble.py script exists
    if os.path.exists(os.path.join(env.localplugins['FabMaMiCo'], "config_files", config, "generate_ensemble.py")):
        rich_print(
            Panel(
                f"Generating configurations in SWEEP directory for config '{config}'",
                title="Generating ensemble",
                border_style="blue",
                expand=False,
            )
        )
        local(f"python3 {os.path.join(env.localplugins['FabMaMiCo'], 'config_files', config, 'generate_ensemble.py')}")
        rich_print(
            Panel(
                f"Generated configurations in SWEEP directory for config '{config}'",
                title="Ensemble generation",
                border_style="green",
                expand=False,
            )
        )
    else:
        rich_print(
            Panel(
                f"No generate_ensemble.py script found for config '{config}'",
                title="No ensemble generation",
                border_style="red",
                expand=False,
            )
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_install_user_spack(**args):
    """
    Install Spack in the user's home directory.
    """
    update_environment(args)
    spack_dir = template(env.spack_dir)
    run(f"mkdir -p {spack_dir}")
#     run(f"git clone -c feature.manyFiles=true --depth=2 https://github.com/spack/spack.git {spack_dir}")
    run(f"./spack install cmake", cd=os.path.join(spack_dir, "bin"))


from plugins.FabMaMiCo.CaseStudies import *