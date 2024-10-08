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

# Add local script, blackbox and template path.
add_local_paths("FabMaMiCo")

FabMaMiCo_path = get_plugin_path("FabMaMiCo")


def populate_env_templates():
    """
    Populate the environment variable templates.
    """
    data = {}
    data["mamico_dir"] = template(env.mamico_dir_template)
    data["mamico_venv"] = template(env.mamico_venv_template)
    data["openfoam_dir"] = template(env.openfoam_dir_template)
    update_environment(data)


##################################################################################################
############################# Plugin Installation Verification ###################################
##################################################################################################

@task
def mamico_test_plugin(**args):
    """
    Test the FabMaMiCo plugin installation.
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
def mamico_ml_overview():
    """
    Retrieve an overview of available modules.
    """
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
def mamico_ml_available(query: str = ""):
    """
    List available modules with an optional query.
    """
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
def mamico_ml_keyword(keyword: str = None):
    """
    Search modules by a keyword.
    """
    if keyword is None:
        rich_print(
            Panel(
                f"Please provide a keyword to search for:\n"\
                 "  $ fabsim <machine> mamico_ml_keyword:<keyword>",
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


@task
def mamico_ml(command: str = None):
    """
    Run a custom module command.
    """
    if command is None:
        rich_print(
            Panel(
                f"Please provide a module command:\n"\
                 '  $ fabsim <machine> mamico_ml:"<command>"',
                title="No command provided",
                border_style="red",
                expand=False,
            )
        )
        return
    cmd = f"module --redirect {command} 2>&1"
    output = run(cmd, capture=True)
    rich_print(
        Panel(
            f"'module {command}' returned the following on {env.host}:",
            title="Module",
            border_style="blue",
            expand=True,
        )
    )
    print(output)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_ml_test_WIP():
    """
    Check if the modules from machines.yml are available.
    """
    populate_env_templates()
    update_environment()
    print(env.modules)


##################################################################################################
################################### MaMiCo simulations ###########################################
##################################################################################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_install(config: str, **args):
    """
    Transfers the MaMiCo source code to the remote machine and compiles it with all its dependencies.
    Downloads the MaMiCo source code from the MaMiCo repository and optionally ls1-mardyn and OpenFOAM.
    Checks out the given branch/commit/tag and transfers the source code to the remote machine.
    Then compiles the code on the remote machine, either on the login node or on a compute node.
    """
    populate_env_templates()
    update_environment(args)
    update_environment({ "cores": 1 })
    # read the settings from the config_dir/settings.yml
    settings = Settings(FabMaMiCo_path, config)
    # create instance of MaMiCoSetup (includes setup functionalities)
    mamico_setup = MaMiCoSetup(FabMaMiCo_path, config, settings)

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

    # prepare open-foam locally
    need_openfoam = settings.get('need_openfoam', False)
    openfoam_version = mamico_setup.prepare_openfoam_locally(need_openfoam=need_openfoam)
    if len(openfoam_version) > 0:
        settings.update({ "openfoam_version": openfoam_version })

    checksum = settings.determine_md5()
    update_environment({ "mamico_checksum": checksum })

    # transfer files from config_files to remote machine
    execute(put_configs, config)

    # prepare installation directory for MaMiCo
    run(f"mkdir -p {env.mamico_dir}")

    # if MaMiCo is already installed, skip the installation
    if mamico_setup.check_mamico_availability(output=True):
        return

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
    with_config(config)

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


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_run(config: str, **args):
    """
    Run a single MaMiCo simulation.
    This task makes sure that the MaMiCo code is installed and compiled on the remote machine.
    It then copies the necessary input files to the build folder and submits the job.
    """
    populate_env_templates()
    update_environment(args)
    with_config(config)
    execute(put_configs, config)

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
    populate_env_templates()
    update_environment(args)

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

    # make sure MaMiCo is installed
    mamico_install(config, **args)

    path_to_config = find_config_file_path(config)
    print(f"local config file path at: {path_to_config}")
    sweep_dir = os.path.join(path_to_config, "SWEEP")
    env.script = 'run'
    with_config(config)
    run_ensemble(config, sweep_dir, **args)


##################################################################################################
################################## MaMiCo postprocessing #########################################
##################################################################################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_install_venv_WIP(**args):
    """
    Create a virtual environment for Python and install the required packages.
    """
    populate_env_templates()
    # create the config_files directory and copy the requirements_remote.txt file there
    config = "venv_setup"
    local(f"mkdir -p {env.localplugins['FabMaMiCo']}/config_files/{config}")
    local(f"cp {env.localplugins['FabMaMiCo']}/requirements_remote.txt {env.localplugins['FabMaMiCo']}/config_files/{config}/requirements.txt")
    local(f"echo '*' > {env.localplugins['FabMaMiCo']}/config_files/{config}/.gitignore")
    update_environment(args)
    with_config(config)
    # transfer files from config_files to remote machine
    execute(put_configs, config)

    commands = [
        f"module load python/3.11",
        f"mkdir -p {env.mamico_venv}",
        f"python3 -m venv {env.mamico_venv}",
        f"source {env.mamico_venv}/bin/activate",
        f"pip install -r {env.job_config_path}/requirements.txt",
        # f"rm -rf {env.job_config_path}/"
    ]
    cmd = " && ".join(commands)
    run(cmd) ## alternatively, use job(dict(script='install_venv'), args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_postprocess(config: str, script: str = "postprocess.py", py_args: str = "", **args):
    """
    Run a postprocessing Pyhon script in the given config-directory.
    """
    populate_env_templates()
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
    populate_env_templates()
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
    populate_env_templates()
    update_environment(args)
    output = run("squeue --me | awk '{print $1}'", capture=True)
    output = len(output.split("\n")[1:-1])
    print(f"Currently having {output} jobs in the queue.")


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_jobs_cancel_all(**args):
    """
    Cancel all `fabmamico_`-jobs on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    output = run("squeue --me --format='%.10i %.80j' | grep fabmamico_ | awk '{print $1}' | tail -n+2 | xargs -n 1 scancel", capture=True)
    print(output)
    print("All MaMiCo jobs were canceled.")


##################################################################################################
############################ MaMiCo installation housekeeping ####################################
##################################################################################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_list_installations(**args):
    """
    List all MaMiCo installations on the remote machine.

    Args:
        verbose (bool): Show compilation settings for each installation. Default: False
    """
    populate_env_templates()
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
    installations = run(f"ls {env.mamico_dir}", capture=True)

    # get compilation info from each installation
    if args.get("verbose", False):
        verbose_info = []
        for installation in installations.split():
            a = run(f"cat {env.mamico_dir}/{installation}/build/compilation_info.yml", capture=True)
            verbose_info.append(a)

    # Print the installations as table
    num_installations = len(installations.split())
    title = f"\n[green]Found {num_installations} installation{ 's' if num_installations != 1 else '' } on {env.host}\n"\
        f"at[/green] [white]{env.mamico_dir}[/white]"
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
            table.add_row(installation, "\n".join(verbose_info.pop(0).split("\n")[:-1]))
        else:
            table.add_row(installation)
    console = Console()
    console.print(table)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_installation_available(checksum: str, **args):
    populate_env_templates()
    update_environment(args)
    env["mamico_checksum"] = checksum
    dir_to_remove = os.path.join(env.mamico_dir, env.mamico_checksum)
    run(
        f'test -d {dir_to_remove}',
        capture=True
    )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_remove_installation(checksum: str, **args):
    """
    Removes a specific MaMiCo installation directory on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    env["mamico_checksum"] = checksum
    dir_to_remove = os.path.join(env.mamico_dir, env.mamico_checksum)
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
            title="[green]Clean up successful[/green]",
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
    populate_env_templates()
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
    output = run(f"rm -rf {env.mamico_dir}/*", capture=True)
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
############################## WIP: Case Study specific tasks ####################################
##################################################################################################


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_nlm_sq(**args):
    """
    Parameters are set for execution on HSUper.
    """
    if env.host != "hsuper":
        print("Please run this task on HSUper or adapt the task to your needs.")
        return

    ## MD30
    config = "study_3_filter_nlm_sq_MD30"
    populate_env_templates()
    update_environment(args)
    args.update({
        "cores": 1 ,
        "job_wall_time": "00:05:00",
        "partition_name": "small_shared"
    })
    mamico_run_ensemble(config, **args)

    ## MD60
    config = "study_3_filter_nlm_sq_MD60"
    populate_env_templates()
    update_environment(args)
    args.update({
        "cores": 1 ,
        "job_wall_time": "00:10:00",
        "partition_name": "small_shared"
    })
    mamico_run_ensemble(config, **args)

    # transfer the postprocess script to the remote machine

    # generate the batch script to run the postprocess script

    # submit the job
    pass


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_1(**args):
    """
    Please run this on localhost!

    1. Run `fabsim <machine> mamico_install study_1_wall_time` on all machines.
    2. Run `fabsim <machine> mamico_run study_1_wall_time` on all machines.
    3. Wait for all jobs to finish.
    4. Run `fabsim <machine> mamico_postprocess study_1_wall_time` on all machines.
    5. Collect the results.
    6. Run postprocess script.
    """
    if env['host_string'] != "localhost":
        print("Please run this task on localhost.")
        return
    
    config = "study_1_wall_time"

    machines = ["hsuper", "cosma", "sofia", "ants"]

    for machine in machines:
        env['host_string'] = machine
        populate_env_templates()
        update_environment(args)
        
        mamico_install(config, **args)
        # optionally wait for installation to finish
        mamico_run(config, **args)
