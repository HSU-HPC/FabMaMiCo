import os
from itertools import product

import numpy as np
from plugins.FabMaMiCo.utils.alter_xml import alter_xml

script_dir_path = os.path.dirname(os.path.abspath(__file__))
n_writes = 0

############################
### SCENARIO DEFINITIONS ###
############################

domains = [
    {
        "name": "MD30",
        "template": "template_multimd.xml",
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

oscillations = [
    {
        "name": "2osc",
        "couette-test/domain/wall-oscillations": 2
    },
    {
        "name": "5osc",
        "couette-test/domain/wall-oscillations": 5
    }
]

wall_vel = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]
wall_velocities = [
    {
        "name": f"wv{str(round(wv,1)).replace('.','')}",
        "couette-test/domain/wall-velocity": f"{round(wv,1)} ; 0.0 ; 0.0",
    } for wv in wall_vel
]

# Generate all possible combinations of scenarios
scenarios = []
for dm, osc, wv in product(domains, oscillations, wall_velocities):
    combined_dict = {
        **dm,
        **osc,
        **wv,
        "name": f"multimd_{dm['name']}_{osc['name']}_{wv['name']}"
    }
    scenarios.append(combined_dict)


###############################################################################
## WRITE XML FILES
###############################################################################

os.makedirs(os.path.join(script_dir_path, "SWEEP"), exist_ok=True)

for sc in scenarios:
    dest_filepath = os.path.join(script_dir_path, "SWEEP", sc['name'])
    alter_xml(script_dir_path, sc, write=dest_filepath)
    n_writes += 1

print(f"Generated {n_writes} XML-files in the SWEEP directory.")
