import os

from itertools import product

from plugins.FabMaMiCo.utils.alter_xml import alter_xml


script_dir_path = os.path.dirname(os.path.abspath(__file__))
n_writes = 0


############################
### SCENARIO DEFINITIONS ###

domains = [
    {
        "name": "MD30",
        "couette-test/domain/channelheight": 50,
        "mamico/macroscopic-cell-configuration/cell-size": "2.5 ; 2.5 ; 2.5",
        "mamico/macroscopic-cell-configuration/linked-cells-per-macroscopic-cell": "1 ; 1 ; 1",
        "molecular-dynamics/simulation-configuration/number-of-timesteps": 50,
        "molecular-dynamics/domain-configuration/molecules-per-direction": "28 ; 28 ; 28",
        "molecular-dynamics/domain-configuration/domain-size": "30.0 ; 30.0 ; 30.0",
        "molecular-dynamics/domain-configuration/domain-offset": "10.0 ; 10.0 ; 2.5",
        "couette-test/microscopic-solver/equilibration-steps": 10001,
        "molecular-dynamics/checkpoint-configuration/filename": "CheckpointSimpleMDGauss30",
        "molecular-dynamics/checkpoint-configuration/write-every-timestep": 10000,
    },
    {
        "name": "MD60",
        "couette-test/domain/channelheight": 100,
        "mamico/macroscopic-cell-configuration/cell-size": "5.0 ; 5.0 ; 5.0",
        "mamico/macroscopic-cell-configuration/linked-cells-per-macroscopic-cell": "2 ; 2 ; 2",
        "molecular-dynamics/simulation-configuration/number-of-timesteps": 100,
        "molecular-dynamics/domain-configuration/molecules-per-direction": "56 ; 56 ; 56",
        "molecular-dynamics/domain-configuration/domain-size": "60.0 ; 60.0 ; 60.0",
        "molecular-dynamics/domain-configuration/domain-offset": "20.0 ; 20.0 ; 5.0",
        "couette-test/microscopic-solver/equilibration-steps": 20001,
        "molecular-dynamics/checkpoint-configuration/filename": "CheckpointSimpleMDGauss60",
        "molecular-dynamics/checkpoint-configuration/write-every-timestep": 20000,
    },
]

scenarios = domains


##########################
### FILTER DEFINITIONS ###

gauss_configs = [
    {
        "name": "gauss",
        "template": "template_gauss_CP.xml",
    }
]


###############################################################################
## WRITE XML FILES
###############################################################################

os.makedirs(os.path.join(script_dir_path, "SWEEP"), exist_ok=True)

for sc, filt in product(scenarios, gauss_configs):
    combined_dict = {
        **sc,
        **filt,
        "name": f"{filt['name']}_{sc['name']}"
    }
    dest_filepath = os.path.join(script_dir_path, "SWEEP", combined_dict['name'])
    alter_xml(script_dir_path, combined_dict, write=dest_filepath)
    n_writes += 1

print(n_writes)
