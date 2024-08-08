import os
from itertools import product

from plugins.FabMaMiCo.utils.alter_xml import alter_xml

script_dir_path = os.path.dirname(os.path.abspath(__file__))
n_writes = 0


############################
### SCENARIO DEFINITIONS ###
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

nlm_configs = [
    {
        "name": "nlm",
        "template": "template_nlm.xml",
        "filter-pipeline/post-multi-instance/nlm-junction/NLM/sigsq_rel": 0.05,
        "filter-pipeline/post-multi-instance/nlm-junction/NLM/hsq_rel": 0.1,
        "filter-pipeline/post-multi-instance/nlm-junction/NLM/time-window-size": [3, 5, 10, 20, 80]
    },
    {
        "name": "nlm",
        "template": "template_nlm.xml",
        "filter-pipeline/post-multi-instance/nlm-junction/NLM/sigsq_rel": [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1],
        "filter-pipeline/post-multi-instance/nlm-junction/NLM/hsq_rel": [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1],
        "filter-pipeline/post-multi-instance/nlm-junction/NLM/time-window-size": 5
    }
]

nlm_configs_all = []
for nlm in nlm_configs:
    for key in nlm.keys():
        if not isinstance(nlm[key], list):
            nlm[key] = [nlm[key]]
        keys, values = zip(*nlm.items())
    nlm_configs_all += [dict(zip(keys, v)) for v in product(*values)]

###############################################################################
## WRITE XML FILES
###############################################################################

os.makedirs(os.path.join(script_dir_path, "SWEEP"), exist_ok=True)

# pod:
for sc, filt in product(scenarios, nlm_configs_all):
    combined_dict = {
        **sc,
        **filt,
        "name": f"{filt['name']}_{sc['name']}_"\
                f"sigsq{filt['filter-pipeline/post-multi-instance/nlm-junction/NLM/sigsq_rel']:.2f}_"\
                f"hsq{filt['filter-pipeline/post-multi-instance/nlm-junction/NLM/hsq_rel']:.2f}_"\
                f"tw{filt['filter-pipeline/post-multi-instance/nlm-junction/NLM/time-window-size']:02d}"
    }
    combined_dict['name'] = combined_dict['name'].replace(".", "")
    dest_filepath = os.path.join(script_dir_path, "SWEEP", combined_dict['name'])
    alter_xml(script_dir_path, combined_dict, write=dest_filepath)
    n_writes += 1

print(n_writes)
