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

from plugins.FabMaMiCo.scripts.setup import MaMiCoSetup # ToDo: improve import (start with plugin-root)

# Add local script, blackbox and template path.
add_local_paths("FabMaMiCo")

FabMaMiCo_path = get_plugin_path("FabMaMiCo")


@task
def mamico_install(config: str, **args):
    """Install MaMiCo on the remote machine.
    This task will downlad MaMiCo from the GitHub repository and checkout the given branch/tag/commit.
    It will furthermore download the MaMiCo dependencies and transfer everything to the remote machine.
    It will then compile MaMiCo directly on the login node or trigger a job submission to compile MaMiCo on a compute node.
    config: config directory to use to define input files
    """
    print("++ Updating environment with args:", args)
    update_environment(args) # updates _lookupDict with every key-value pair in args
    print("++ With config:", config)
    with_config(config) # sets the config directory to be used locally and remotely
    print("++ Executing put_configs:", config)
    execute(put_configs, config) # copies the config files to the remote machine
    print("\n+++++++++++++++++++++++")
    print("++ Setting up MaMiCo ++")
    print("+++++++++++++++++++++++\n")
    mamico_setup = MaMiCoSetup(FabMaMiCo_path, config)
    mamico_setup.read_user_config()
    mamico_setup.download_mamico()
    mamico_setup.transfer_to_remote_host()
    mamico_setup.load_dependencies()
    # mamico_setup.compile_mamico()


@task
def mamico(config, **args):
    """Submit a MaMiCo job to the remote queue.
    The job results will be stored with a name pattern as defined in the environment,
    e.g. <config-name>-
    config : config directory to use to define input files, e.g. config=cylinder
    Keyword arguments:
            cores : number of compute cores to request
            images : number of images to take
            steering : steering session i.d.
            wall_time : wall-time job limit
            memory : memory per node
    """
    update_environment(args)
    with_config(config)
    execute(put_configs, config)
    # rsync_project(
    #     local_dir='/home/jo/repos/FabSim3/plugins/FabMaMiCo/tmp/MaMiCo/',
    #     remote_dir='/home/jo/MaMiCo/',
    #     exclude=['.git/'],
    #     delete=True
    # )
    # job(dict(script='test_installation', wall_time='0:15:0', memory='2G'), args)
