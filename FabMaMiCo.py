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
def mamico_run(config: str, **args):
    """
    Run a single MaMiCo simulation.
    This task makes sure that the MaMiCo code is installed and compiled on the remote machine.
    It then copies the necessary input files to the build folder and submits the job.
    """
    populate_env_templates()
    mamico_install(config, **args)
    # copy the couette.xml file to the build folder
    run(f"cp {env.job_config_path}/couette.xml {env.mamico_dir}/{env.md5_checksum}/build/couette.xml")
    # copy the checkpoint files to the build folder
    run(f"cp {env.mamico_dir}/{env.md5_checksum}/examples/CheckpointSimpleMD_10000_periodic_0.checkpoint {env.mamico_dir}/{env.md5_checksum}/build/CheckpointSimpleMD_10000_periodic_0.checkpoint")
    run(f"cp {env.mamico_dir}/{env.md5_checksum}/examples/CheckpointSimpleMD_10000_reflecting_0.checkpoint {env.mamico_dir}/{env.md5_checksum}/build/CheckpointSimpleMD_10000_reflecting_0.checkpoint")
    # submit the job
    job(dict(script='run', job_wall_time='0:15:0'), args)


@task
def mamico_install(config: str, **args):
    """
    Transfer the MaMiCo source code to the remote machine and compile it with all its dependencies.
    This task downloads the MaMiCo source code from the MaMiCo repository and optionally ls1-mardyn.
    It checks out the given branch/commit/tag and transfers the code to the remote machine.
    It then compiles the code on the remote machine, either on the login node or on a compute node.
    """
    populate_env_templates()
    update_environment(args)
    mamico_setup = MaMiCoSetup(FabMaMiCo_path, config)
    mamico_setup.read_config()
    mamico_setup.download_mamico()
    mamico_setup.determine_md5()
    update_environment(mamico_setup.config_mamico) # jmToDo: decide if this is necessary
    with_config(config) # sets the config directory to be used locally and remotely
    execute(put_configs, config)

    # prepare installation directory for MaMiCo
    run(f"mkdir -p {env.mamico_dir}")
    
    if mamico_setup.check_mamico_availability():
        print("MaMiCo already installed.")
        return

    # transfer MaMiCo to remote host    
    mamico_setup.transfer_to_remote_host()

    # generate the command for compilation
    env["compilation_command"] = mamico_setup.generate_compile_command()

    # run/submit compilation job
    if env.get("compile_mamico_on_login_node", False):
        print("Compiling MaMiCo on login node:")
        # update job_dispatch to bash
        old_job_dispatch = env.get("job_dispatch")
        print(old_job_dispatch)
        update_environment({"job_dispatch": "bash"})
    # submit job to compile MaMiCo
    job(dict(script='compile', job_wall_time='0:15:0'), args)

    # reset job_dispatch to its original value
    if env.get("compile_mamico_on_login_node", False):
        update_environment({"job_dispatch": old_job_dispatch})


@task
def mamico_list_installations(**args):
    """
    List all MaMiCo installations on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    mamico_setup = MaMiCoSetup(FabMaMiCo_path, "")
    mamico_setup.list_installations()


@task
def mamico_clean_installation(checksum: str, **args):
    """
    Clean up a specific MaMiCo installation directory on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    env["md5_checksum"] = checksum
    mamico_setup = MaMiCoSetup(FabMaMiCo_path, "")
    mamico_setup.clean_installation()


@task
def mamico_clean_installations(**args):
    """
    Clean up all MaMiCo installations on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    mamico_setup = MaMiCoSetup(FabMaMiCo_path, "")
    mamico_setup.clean_installations()
