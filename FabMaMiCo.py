# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabDummy.

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
    # ... add more templates here (if necessary)
    update_environment(data)



@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_install(config: str, **args):
    """
    Transfer the MaMiCo source code to the remote machine and compile it with all its dependencies.
    This task downloads the MaMiCo source code from the MaMiCo repository and optionally ls1-mardyn.
    It checks out the given branch/commit/tag and transfers the code to the remote machine.
    It then compiles the code on the remote machine, either on the login node or on a compute node.
    """
    populate_env_templates()
    update_environment(args)
    with_config(config)
    settings = Settings(FabMaMiCo_path, config)
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
    # need_openfoam = settings.get('need_openfoam', False)
    # openfoam_commit = mamico_setup.prepare_openfoam_locally(need_openfoam=need_openfoam)
    # if len(openfoam_commit) > 0:
    #     settings.update({ "openfoam_commit": openfoam_commit })
    # settings.delete("openfoam_branch_tag_commit")

    checksum = settings.determine_md5()
    update_environment({ "mamico_checksum": checksum })

    # transfer files from config_files to remote machine
    execute(put_configs, config)

    # prepare installation directory for MaMiCo
    run(f"mkdir -p {env.mamico_dir}")

    if mamico_setup.check_mamico_availability(output=True):
        return

    # transfer MaMiCo to remote host
    mamico_setup.transfer_to_remote_host()

    # save the configuration file
    mamico_setup.save_config_yml()

    # generate the command for compilation
    compile_command_ls1 = mamico_setup.generate_compile_command_ls1()
    compile_command_mamico = mamico_setup.generate_compile_command_mamico()

    update_environment({
        "compilation_command_ls1": compile_command_ls1,
        "compilation_command_mamico": compile_command_mamico
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
        update_environment({
            "job_dispatch": "bash",
            "job_name_template": "fabmamico_${config}_${machine_name}_${task}"
        })
        # execute batch script with bash: `bash <config>_<machine>_1_mamico_install.sh`
        job(dict(script='compile'), args)
        # reset job_dispatch to its original value (for possible subsequent jobs)
        update_environment({
            "job_dispatch": old_job_dispatch,
            "job_name_template": old_job_name_template
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

    # make sure MaMiCo is installed
    mamico_install(config, **args)

    path_to_config = find_config_file_path(config)
    print(f"local config file path at: {path_to_config}")
    sweep_dir = os.path.join(path_to_config, "SWEEP")
    env.script = 'run'
    with_config(config)
    run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_stat(**args):
    """
    Show the queue of FabMaMiCo-jobs on the remote machine.
    Calls `squeue` and filters the output for FabMaMiCo-jobs.
    """
    populate_env_templates()
    update_environment(args)
    output = run(f"squeue --format='%.10i %.9P %.62j %.10u %.8T %.13M %.9l %.6D %R' --me", capture=True)
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
    output = run("squeue --me | awk '{print $1}' | tail -n+2 | xargs -n 1 scancel", capture=True)
    print(output)
    print("All MaMiCo jobs were canceled.")


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_list_installations(**args):
    """
    List all MaMiCo installations on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    rich_print(
            Panel(
            f"Please wait until the MaMiCo installations on {env.host} are listed.",
            title="[pink1]Listing MaMiCo installations[/pink1]",
            border_style="pink1",
            expand=False,
        )
    )
    # list all directories in the MaMiCo directory
    installations = run(f"ls {env.mamico_dir}", capture=True)

    # get compilation info from each installation
    verbose_info = []
    if args.get("verbose", False):
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
def mamico_remove_installation(checksum: str, **args):
    """
    Clean up a specific MaMiCo installation directory on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    env["mamico_checksum"] = checksum
    dir_to_remove = os.path.join(env.mamico_dir, env.mamico_checksum)
    rich_print(
        Panel(
            f"Please wait until the MaMiCo installation {env.mamico_checksum} is removed.",
            title=f"[pink1]Cleaning MaMiCo installation on {env.host}[/pink1]",
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
    Clean up all MaMiCo installations on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    rich_print(
        Panel(
            f"Please confirm the removal of all MaMiCo installations on {env.host} by entering 'y'.",
            title="[pink1]Cleaning MaMiCo installations[/pink1]",
            border_style="pink1",
            expand=False,
        )
    )
    confirmation = input("Y[es] or N[o]: ").lower()
    if confirmation != "y":
        rich_print(
            Panel(
                f"Aborted the removal of MaMiCo installations on {env.host}.",
                title="[red]Aborted[/red]",
                border_style="red",
                expand=False
            )
        )
        return
    output = run(f"rm -rf {env.mamico_dir}/*", capture=True)
    print(output)
    rich_print(
        Panel(
            f"There are no more MaMiCo installations on {env.host}.",
            title="[green]All cleaned up[/green]",
            border_style="green",
            expand=False
        )
    )
