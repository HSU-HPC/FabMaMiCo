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
        "name": "MD60",
        "template": "template_multimd.xml",
        # domain:
        "couette-test/domain/channelheight": 100,
        "mamico/macroscopic-cell-configuration/cell-size": "5.0 ; 5.0 ; 5.0",
        "mamico/macroscopic-cell-configuration/linked-cells-per-macroscopic-cell": "2 ; 2 ; 2",
        "molecular-dynamics/simulation-configuration/number-of-timesteps": 100,
        "molecular-dynamics/domain-configuration/molecules-per-direction": "56 ; 56 ; 56",
        "molecular-dynamics/domain-configuration/domain-size": "60.0 ; 60.0 ; 60.0",
        "molecular-dynamics/domain-configuration/domain-offset": "20.0 ; 20.0 ; 5.0",
    },
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

wall_vel = np.arange(0.2, 1.9, 0.2) # up to 1.8 (inclusive)
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
