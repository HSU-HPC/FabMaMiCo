# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabDummy.

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from fabsim.deploy.templates import template

from plugins.FabMaMiCo.scripts.setup import MaMiCoSetup # ToDo: improve import (start with plugin-root)
import pickle as pkl
import copy

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
    execute(put_configs, config)
    mamico_setup = MaMiCoSetup(FabMaMiCo_path, config)
    mamico_setup.read_config()
    mamico_setup.download_src_code()
    mamico_setup.determine_md5()

    # prepare installation directory for MaMiCo
    run(f"mkdir -p {env.mamico_dir}")

    if mamico_setup.check_mamico_availability(output=True):
        return

    # transfer MaMiCo to remote host
    mamico_setup.transfer_to_remote_host()

    # save the configuration file
    mamico_setup.save_config_yml()

    # generate the command for compilation
    compile_command = mamico_setup.generate_compile_command()

    update_environment({
        "compilation_command": compile_command,
    })

    # run/submit compilation job
    if env.get("compile_on_login_node", False):
        #########################
        # COMPILE ON LOGIN NODE #
        #########################
        print("Compiling on login node:")
        # update job_dispatch to bash
        old_job_dispatch = env['job_dispatch']
        update_environment({
            "job_dispatch": "bash",
            "job_name_template": "${config}_${machine_name}_${task}"
        })
        # execute batch script with bash: `bash <config>_<machine>_1_mamico_install.sh`
        job(dict(script='compile'), args)
        # reset job_dispatch to its original value (for possible subsequent jobs)
        update_environment({
            "job_dispatch": old_job_dispatch
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
    # TODO: if compilation as job, wait for job to finish

    mamico_setup = MaMiCoSetup(FabMaMiCo_path, config)
    mamico_setup.read_config()

    print(env.cores)

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
    with_config(config)
    execute(put_configs, config)

    # make sure MaMiCo is installed
    mamico_install(config, **args)
    # TODO: if compilation as job, wait for job to finish

    mamico_setup = MaMiCoSetup(FabMaMiCo_path, config)
    mamico_setup.read_config()

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_scaling(config:str, **args):
    populate_env_templates()
    update_environment(args)
    with_config(config)
    execute(put_configs, config)

    mamico_install(config, **args)

    mamico_setup = MaMiCoSetup(FabMaMiCo_path, config)
    mamico_setup.read_config()

    # copy the checkpoint files to the build folder
    run(f"cp {env.mamico_dir}/{env.mamico_checksum}/examples/CheckpointSimpleMD_10000_periodic_0.checkpoint {env.mamico_dir}/{env.mamico_checksum}/build/CheckpointSimpleMD_10000_periodic_0.checkpoint")
    run(f"cp {env.mamico_dir}/{env.mamico_checksum}/examples/CheckpointSimpleMD_10000_reflecting_0.checkpoint {env.mamico_dir}/{env.mamico_checksum}/build/CheckpointSimpleMD_10000_reflecting_0.checkpoint")

    for i in [1, 2, 4, 8, 16, 32, 64, 128]:
        update_environment({"cores": i})
        # EDIT THE CONFIG FILE
        run(f"cp {env.job_config_path}/couette.xml {env.mamico_dir}/{env.mamico_checksum}/build/couette.xml")


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
    installations = run(f"ls {env.mamico_dir}", capture=True)
    rich_print(
        Panel(
            "\n".join(installations.split()),
            title=f"[green]Found {len(installations.split())} installations on {env.host}[/green]",
            border_style="green",
            expand=False
        )
    )


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
            f"Please wait until all MaMiCo installations on {env.host} are removed.",
            title="[pink1]Cleaning MaMiCo installations[/pink1]",
            border_style="pink1",
            expand=False,
        )
    )
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
