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
        # domain:
        "couette-test/domain/channelheight": 50,
        "mamico/macroscopic-cell-configuration/cell-size": "2.5 ; 2.5 ; 2.5",
        "mamico/macroscopic-cell-configuration/linked-cells-per-macroscopic-cell": "1 ; 1 ; 1",
        "molecular-dynamics/simulation-configuration/number-of-timesteps": 50,
        "molecular-dynamics/domain-configuration/molecules-per-direction": "28 ; 28 ; 28",
        "molecular-dynamics/domain-configuration/domain-size": "30.0 ; 30.0 ; 30.0",
        "molecular-dynamics/domain-configuration/domain-offset": "10.0 ; 10.0 ; 2.5",
    }
]

wall_velocities = [
    {
        "name": "wv02",
        "couette-test/domain/wall-velocity": "0.2 ; 0.0 ; 0.0",
    },
    {
        "name": "wv04",
        "couette-test/domain/wall-velocity": "0.4 ; 0.0 ; 0.0",
    },
    {
        "name": "wv06",
        "couette-test/domain/wall-velocity": "0.6 ; 0.0 ; 0.0",
    },
    {
        "name": "wv08",
        "couette-test/domain/wall-velocity": "0.8 ; 0.0 ; 0.0",
    },
    {
        "name": "wv10",
        "couette-test/domain/wall-velocity": "1.0 ; 0.0 ; 0.0",
    }
]

scenarios = []
for dm, wv in product(domains, wall_velocities):
    combined_dict = {
        **dm,
        **wv,
        "name": f"{dm['name']}_{wv['name']}"
    }
    scenarios.append(combined_dict)

##########################
### FILTER DEFINITIONS ###

gauss_configs = [
    {
        "name": "gauss",
        "template": "template_gauss.xml",
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

print(f"Generated {n_writes} XML-files in the SWEEP directory.")
