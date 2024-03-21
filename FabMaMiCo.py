# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabDummy.

try:
    from fabsim.base.fab import *
    from fabsim.VVP import vvp
except ImportError:
    from base.fab import *

from plugins.FabMaMiCo.scripts.setup_mamico import setup_mamico # ToDo: improve import (start with plugin-root)

# Add local script, blackbox and template path.
add_local_paths("FabMaMiCo")


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
    job(dict(script='test_installation', wall_time='0:15:0', memory='2G'), args)
