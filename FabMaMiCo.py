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
def mamico_lmod_overview(**args) -> None:
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
def mamico_lmod_available(query: str = "", **args) -> None:
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
def mamico_lmod_keyword(keyword: str = None, **args) -> None:
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
@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_lmod_test_WIP(template_script: str, **args):
    """
    Check if the modules from machines.yml/machines_user.yml are available.
    """
    update_environment()
    print(env.modules[template_script])
#################


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
    update_environment(args)
    with_config(config)
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

    # print the settings
    settings.print()

    checksum = settings.determine_md5()
    update_environment({ "mamico_checksum": checksum })

    env.mamico_dir = template(env.mamico_dir_template)

    # if MaMiCo is already installed, skip the installation
    is_available = mamico_setup.check_mamico_availability(output=True)
    if only_check:
        return is_available
    if is_available:
        print("MaMiCo is already installed.")
        return True

    update_environment({ "cores": 1 })

    # transfer files from config_files to remote machine
    execute(put_configs, config)

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
    installations = run(f"ls {template(env.mamico_dir)}", capture=True)

    # get compilation info from each installation
    if args.get("verbose", False):
        verbose_info = []
        for installation in installations.split():
            a = run(f"cat {template(env.mamico_dir)}/{installation}/build/compilation_info.yml", capture=True)
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
            table.add_row(installation, "\n".join(verbose_info.pop(0).split("\n")[:-1]))
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
            f"test -d {installation_dir}",
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
    except Exception as e:
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
    update_environment(args)
    with_config(config)
    execute(put_configs, config)

    env.mamico_dir = template(env.mamico_dir_template)

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
    update_environment(args)

    generate_sweep()

    # make sure MaMiCo is installed
    mamico_install(config, **args)

    env.mamico_dir = template(env.mamico_dir_template)

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
        "squeue --me --format='%.10i %.80j' | grep fabmamico_ | awk '{print $1}' | tail -n+2 | xargs -n 1 scancel",
        capture=True
    )
    print(output)
    print("All MaMiCo jobs have been canceled.")



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
    update_environment(args)
    args.update({
        "cores": 1 ,
        "job_wall_time": "00:05:00",
        "partition_name": "small_shared"
    })
    mamico_run_ensemble(config, **args)

    ## MD60
    config = "study_3_filter_nlm_sq_MD60"
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
def mamico_study_1(*machines, **args):
    """
    Please run this on localhost!

    1. Run `fabsim <machine> mamico_install:study_1_wall_time` on all machines.
    2. Run `fabsim <machine> mamico_run:study_1_wall_time` on all machines.
    3. Wait for all jobs to finish.
    4. Run `fabsim <machine> mamico_postprocess study_1_wall_time` on all machines.
    5. Collect the results.
    6. Run postprocess script.
    """
    if env.host != "localhost":
        rich_print(
            Panel(
                "Please run this task on [bold]localhost[/bold].",
                title="Wrong host",
                border_style="red",
                expand=False,
            )
        )
        return

    config = "study_1_wall_time"

    #######################################
    ## 1. Install MaMiCo on all machines ##
    #######################################

    # check if each machine is configured in the machines.yml/machines_user.yml
    for machine in machines:
        if machine not in env.avail_machines.keys():
            rich_print(
                Panel(
                    f"The machine [bold]{machine}[/bold] is not configured.\n" \
                    "Please check your [italic]machines.yml/machines_user.yml[/italic] files.",
                    title="Machine not found",
                    border_style="red",
                    expand=False,
                )
            )
            return

    for machine in machines:
        local(f"fabsim {machine} mamico_install:{config}")
        # local(f"fabsim {machine} mamico_run:study_1_wall_time,cores=8,corespernode=8,replicas=50")
        # local(f"fabsim {machine} mamico_run:study_1_wall_time,cores=8,corespernode=4,replicas=50")


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_postprocess_study_3_filter_gauss(**args):
    """
    Postprocess the results of the study_3_filter_gauss (MD30 & MD60).

    Please adjust the parameters in the function calls to match your specific case study setup.
    """

    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_gauss.postprocess_all import generate_plots

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    generate_plots(
        scenario=30,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        results_dir_gauss=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD30_hsuper_1"),
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD30_hsuper_1600"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD30_hsuper_1", "postprocess"),
        from_npy=args.get("from_npy", False)
    )

    generate_plots(
        scenario=60,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        results_dir_gauss=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD60_hsuper_1"),
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD60_hsuper_1600"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD60_hsuper_1", "postprocess"),
        from_npy=args.get("from_npy", False)
    )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_postprocess_study_3_filter_gauss_vel():
    """
    Postprocess the velocity results of the study_3_filter_gauss (MD30 & MD60).

    Please adjust the parameters in the function calls to match your specific case study setup.
    """

    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_gauss.postprocess_vel import plot_over_time

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    plot_over_time(
        scenario=30,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        results_dir_gauss=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD30_hsuper_1"),
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD30_hsuper_1600"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD30_hsuper_1", "postprocess")
    )

    plot_over_time(
        scenario=60,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        results_dir_gauss=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD60_hsuper_1"),
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD60_hsuper_1600"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD60_hsuper_1", "postprocess")
    )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_postprocess_study_3_filter_gauss_vel_singlecell():
    """
    Postprocess the velocity results of the study_3_filter_gauss (MD30 & MD60).

    Please adjust the parameters in the function calls to match your specific case study setup.
    """

    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_gauss.postprocess_vel_singlecell import plot_over_time

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    plot_over_time(
        scenario=30,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD30_hsuper_1600"),
        results_dir_gauss=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD30_hsuper_1"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD30_hsuper_1", "postprocess")
    )

    plot_over_time(
        scenario=60,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD60_hsuper_1600"),
        results_dir_gauss=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD60_hsuper_1"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_gauss_MD60_hsuper_1", "postprocess")
    )

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_postprocess_study_3_filter_pod(**args):
    """
    Postprocess the results of the study_3_filter_pod (MD30 & MD60).

    Please adjust the parameters in the function calls to match your specific case study setup.
    """

    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_pod.postprocess_all import generate_plots

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    generate_plots(
        scenario=30,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        time_window_sizes=[10, 20, 30, 40, 50, 60, 70, 80],
        k_maxs=[1, 2, 3],
        results_dir_pod=os.path.join(env.local_results, "fabmamico_study_3_filter_pod_MD30_hsuper_1"),
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD30_hsuper_1600"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_pod_MD30_hsuper_1", "postprocess"),
        from_npy=args.get("from_npy", False)
    )

    # TODO: Add MD60


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_postprocess_study_3_filter_nlm_sq(**args):
    """
    Postprocess the results of the study_3_filter_nlm (MD30 & MD60).

    Please adjust the parameters in the function calls to match your specific case study setup.
    """

    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_nlm_sq.postprocess_all import generate_plots

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    generate_plots(
        scenario=30,
        oscillations=[2],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        sigsq_rel=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        hsq_rel=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        tws=5,
        results_dir_nlm_sq=os.path.join(env.local_results, "fabmamico_study_3_filter_nlm_sq_MD30_hsuper_1"),
        results_dir_multimd=os.path.join(env.local_results, "fabmamico_study_3_filter_multimd_MD30_hsuper_1600"),
        output_dir=os.path.join(env.local_results, "fabmamico_study_3_filter_nlm_sq_MD30_hsuper_1", "postprocess"),
        from_npy=args.get("from_npy", False)
    )

    # TODO: Add MD60



##################################################################################################


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
def mamico_study_3_filter_multimd(**args):
    """
    Parameters are set for execution on HSUper.

    """

    scenarios = [
        {"domain": 30, "job_wall_time": "01:00:00" },
        {"domain": 60, "job_wall_time": "12:00:00" },
    ]

    for scenario in scenarios:

        config = f"study_3_filter_multimd_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print(f"Please install MaMiCo first for {config}.")

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1600,
            "corespernode": 72,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "medium",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_gauss(**args):

    scenarios = [
        # {"domain": 30, "job_wall_time": "01:00:00" },
        # {"domain": 60, "job_wall_time": "00:05:00" },
    ]

    for scenario in scenarios:
        config = f"study_3_filter_gauss_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print("Please install MaMiCo first.")
            return

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1,
            "corespernode": 1,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "small_shared",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_gauss_plot(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_gauss.plot import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30, 60]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            results_dir_gauss=os.path.join(env.local_results, f"fabmamico_study_3_filter_gauss_MD{scenario}_hsuper"),
            results_dir_multimd=os.path.join(env.local_results, f"fabmamico_study_3_filter_multimd_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study_3_filter_gauss_MD{scenario}_hsuper", "plots")
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_pod(**args):

    scenarios = [
        # {"domain": 30, "job_wall_time": "00:40:00" },
        {"domain": 60, "job_wall_time": "12:00:00" },
    ]

    for scenario in scenarios:
        config = f"study_3_filter_pod_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print("Please install MaMiCo first.")
            return

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1,
            "corespernode": 1,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "small_shared",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_pod_plot(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_pod.plot import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30, 60]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            time_window_sizes=[10, 20, 30, 40, 50, 60, 70, 80],
            k_maxs=[1, 2, 3],
            results_dir_pod=os.path.join(env.local_results, f"fabmamico_study_3_filter_pod_MD{scenario}_hsuper"),
            results_dir_multimd=os.path.join(env.local_results, f"fabmamico_study_3_filter_multimd_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study_3_filter_pod_MD{scenario}_hsuper", "plots")
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_pod_plot_selected(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_pod.plot_selected import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            time_window_sizes=[10, 20, 30, 40, 50, 60, 70, 80],
            k_maxs=[1, 2, 3],
            results_dir_pod=os.path.join(env.local_results, f"fabmamico_study_3_filter_pod_MD{scenario}_hsuper"),
            results_dir_multimd=os.path.join(env.local_results, f"fabmamico_study_3_filter_multimd_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study_3_filter_pod_MD{scenario}_hsuper", "plots")
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_nlm_tws(**args):

    scenarios = [
        # {"domain": 30, "job_wall_time": "01:00:00" },
        {"domain": 60, "job_wall_time": "12:00:00" },
    ]

    for scenario in scenarios:
        config = f"study_3_filter_nlm_tws_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print("Please install MaMiCo first.")
            return

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1,
            "corespernode": 1,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "small_shared",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_nlm_tws_plot(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_nlm_tws.plot import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            hsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            sigsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            tws=5,
            results_dir_nlm_sq=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_tws_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_tws_MD{scenario}_hsuper", "plots")
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_nlm_sq(**args):

    scenarios = [
        # {"domain": 30, "job_wall_time": "01:00:00" },
        {"domain": 60, "job_wall_time": "12:00:00" },
    ]

    for scenario in scenarios:
        config = f"study_3_filter_nlm_sq_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print("Please install MaMiCo first.")
            return

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1,
            "corespernode": 1,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "small_shared",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_3_filter_nlm_sq_plot(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_nlm_sq.plot import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            hsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            sigsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            tws=5,
            results_dir_nlm_sq=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_sq_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_sq_MD{scenario}_hsuper", "plots")
        )
