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

# Generate all possible combinations of scenarios
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
##########################

pod_configs = [
    {
        "name": "pod",
        "template": "template_pod.xml",
        "filter-pipeline/per-instance/my-pod/POD/time-window-size": [10, 20, 30, 40, 50, 60, 70, 80],
        "filter-pipeline/per-instance/my-pod/POD/kmax": [1, 2, 3]
    }
]

# pod
pod_configs_all = []
for pod in pod_configs:
    for key in pod.keys():
        if not isinstance(pod[key], list):
            pod[key] = [pod[key]]
        keys, values = zip(*pod.items())
    pod_configs_all += [dict(zip(keys, v)) for v in product(*values)]


###############################################################################
## WRITE XML FILES
###############################################################################

os.makedirs(os.path.join(script_dir_path, "SWEEP"), exist_ok=True)

# pod:
for sc, filt in product(scenarios, pod_configs_all):
    combined_dict = {
        **sc,
        **filt,
        "name": f"{filt['name']}_{sc['name']}_tw{filt['filter-pipeline/per-instance/my-pod/POD/time-window-size']}_kmax{filt['filter-pipeline/per-instance/my-pod/POD/kmax']}"
    }
    dest_filepath = os.path.join(script_dir_path, "SWEEP", combined_dict['name'])
    alter_xml(script_dir_path, combined_dict, write=dest_filepath)
    n_writes += 1

print(f"Generated {n_writes} XML-files in the SWEEP directory.")
