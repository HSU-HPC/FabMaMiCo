import os
from itertools import product

from plugins.FabMaMiCo.utils.alter_xml import alter_xml

script_dir_path = os.path.dirname(os.path.abspath(__file__))
n_writes = 0

############################
### SCENARIO DEFINITIONS ###
############################

domains = [
    {
        "name": "MD60",
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
        "name": f"{dm['name']}_{osc['name']}_{wv['name']}"
    }
    scenarios.append(combined_dict)


##########################
### FILTER DEFINITIONS ###
##########################

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
