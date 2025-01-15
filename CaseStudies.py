import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from fabsim.lib.fabsim3_cmd_api import fabsim

from plugins.FabMaMiCo.FabMaMiCo import mamico_install, generate_sweep


##########################################
## Case Study 1: Wall Time Variance     ##
##########################################

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_1_run(**args):
    """
    Run this task on localhost.
    Targeted machines are defined within the task.
    """

    MACHINES = [ 'hsuper', 'dine' ]

    for machine in MACHINES:
        input(f"Make sure that you are connected to a network with access to the machine {machine}. Press Enter to continue...")
        fabsim(task="mamico_run",machine=machine,arguments="config=study1_walltime,corespernode=8")
        fabsim(task="mamico_run",machine=machine,arguments="config=study1_walltime,corespernode=4")


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study1_walltime_plot(**args):

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    REPLICAS = 50
    MACHINES = [
        ('hsuper', 'HSUper'),
        ('cosma', 'DINE')
    ]
    NODE_CONFIGS = ['8_8', '8_4']

    def extract_walltime_from_out_file(filepath):
        with open(filepath, "r") as f:
            txt = f.readlines()
            for line in txt:
                if "Finished all coupling cycles after" in line:
                    seconds = line.split('after ')[-1].split(' ')[0]
                    return float(seconds)

    runtimes = np.empty((len(MACHINES), len(NODE_CONFIGS), REPLICAS))

    for i, machine in enumerate(MACHINES):
        for k, node_config in enumerate(NODE_CONFIGS):
            output_files = glob.glob(os.path.join(env.local_results, f"fabmamico_study_1_wall_time_{machine[0]}_{node_config}*/*.out"))
            for l, output_file in enumerate(output_files):
                runtimes[i, k, l] = extract_walltime_from_out_file(output_file)

    nc = (['8 cores, 1 node'] * REPLICAS + ['8 cores, 2 nodes'] * REPLICAS ) * len(MACHINES)
    walltimes = runtimes.flatten()
    machines = [ machine[1] for machine in MACHINES for _ in range(len(NODE_CONFIGS) * REPLICAS)]

    data = {'Node Config': nc, 'Walltime': walltimes, 'Machine': machines}

    for i, machine in enumerate(MACHINES):
        for k, node_config in enumerate(NODE_CONFIGS):
            print(f"{machine[1]}: {node_config}")
            print(f"Mean: {np.mean(runtimes[i, k])}")
            print(f"Std: {np.std(runtimes[i, k])}")
            print(f"Var: {np.var(runtimes[i, k])}")
            print("")

    df = pd.DataFrame(data)
    print(df)

    sns_plot = sns.boxplot(x='Machine', y='Walltime', hue='Node Config', data=df, showfliers=False)
    plt.title('Wall Time Variance Comparison')
    plt.xlabel('machine')
    plt.ylabel('wall time in seconds')
    plt.legend()

    OUTPUT_FILE = os.path.join(env.local_results, 'study_1_wall_time_plot.png')
    sns_plot.figure.savefig(OUTPUT_FILE, format='png')
    plt.show()


##########################################
## Case Study 2: Filter Parameter Study ##
##########################################

##########################################
# Multi-instance

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study_2_filter_multimd(**args):
    """
    Parameters are set for execution on HSUper.

    """

    scenarios = [
        {"domain": 30, "job_wall_time": "01:00:00" },
        {"domain": 60, "job_wall_time": "12:00:00" },
    ]

    for scenario in scenarios:

        config = f"study_3_filter_multimd_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print(f"Please install MaMiCo first for {config}.")

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1600,
            "corespernode": 72,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "medium",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


##########################################
# Gauss

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_gauss(**args):

    scenarios = [
        # {"domain": 30, "job_wall_time": "01:00:00" },
        # {"domain": 60, "job_wall_time": "00:05:00" },
    ]

    for scenario in scenarios:
        config = f"study_3_filter_gauss_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print("Please install MaMiCo first.")
            return

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1,
            "corespernode": 1,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "small_shared",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_gauss_plot(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study2_gauss.plot import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30, 60]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            results_dir_gauss=os.path.join(env.local_results, f"fabmamico_study2_gauss_MD{scenario}_hsuper"),
            results_dir_multimd=os.path.join(env.local_results, f"fabmamico_study2_multimd_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study2_gauss_MD{scenario}_hsuper", "plots")
        )

##########################################
# POD

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_pod(**args):

    scenarios = [
        # {"domain": 30, "job_wall_time": "00:40:00" },
        {"domain": 60, "job_wall_time": "12:00:00" },
    ]

    for scenario in scenarios:
        config = f"study_3_filter_pod_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print("Please install MaMiCo first.")
            return

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1,
            "corespernode": 1,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "small_shared",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_pod_plot(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study2_pod.plot import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30, 60]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            time_window_sizes=[10, 20, 30, 40, 50, 60, 70, 80],
            k_maxs=[1, 2, 3],
            results_dir_pod=os.path.join(env.local_results, f"fabmamico_study2_pod_MD{scenario}_hsuper"),
            results_dir_multimd=os.path.join(env.local_results, f"fabmamico_study2_multimd_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study2_pod_MD{scenario}_hsuper", "plots")
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_pod_plot_selected(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study2_pod.plot_selected import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30, 60]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 1.0, 1.8],
            time_window_sizes=[10, 20, 30, 40, 50, 60, 70, 80],
            k_maxs=[1, 2, 3],
            results_dir_pod=os.path.join(env.local_results, f"fabmamico_study2_pod_MD{scenario}_hsuper"),
            results_dir_multimd=os.path.join(env.local_results, f"fabmamico_study2_multimd_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study2_pod_MD{scenario}_hsuper", "plots")
        )

##########################################
# NLM time-window-size

# @task
# @load_plugin_env_vars("FabMaMiCo")
# def mamico_study_3_filter_nlm_tws(**args):

#     scenarios = [
#         # {"domain": 30, "job_wall_time": "01:00:00" },
#         {"domain": 60, "job_wall_time": "12:00:00" },
#     ]

#     for scenario in scenarios:
#         config = f"study_3_filter_nlm_tws_MD{scenario['domain']}"

#         # 1. Make sure there is an existing installation of MaMiCo
#         if not mamico_install(config, only_check=True):
#             print("Please install MaMiCo first.")
#             return

#         # 2. Update the environment
#         update_environment(args)
#         update_environment({
#             "mamico_dir": template(env.mamico_dir_template)
#         })
#         # Please be aware that this configuration is specific to HSUper!
#         update_environment({
#             "cores": 1,
#             "corespernode": 1,
#             "job_wall_time": scenario["job_wall_time"],
#             "partition_name": "small_shared",
#             "qos_name": "many-jobs-small_shared"
#         })

#         # 3. Generate the sweep directory
#         generate_sweep(config)

#         # 4. Transfer the configuration files to the remote machine
#         with_config(config)
#         execute(put_configs, config)

#         # 5. Update the environment for the postprocessing
#         update_environment({
#             "mamico_venv": template(env.mamico_venv_template),
#             "reduce_command": "python3",
#             "reduce_script": "reduce.py",
#             "reduce_args": f"--scenario={scenario['domain']}",
#         })

#         # 6. Run the ensemble
#         path_to_config = find_config_file_path(config)
#         sweep_dir = os.path.join(path_to_config, "SWEEP")
#         env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
#         run_ensemble(config, sweep_dir, **args)


# @task
# @load_plugin_env_vars("FabMaMiCo")
# def mamico_study_3_filter_nlm_tws_plot(**args):
#     from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_nlm_tws.plot import create_plot

#     if (env.host != "localhost"):
#         print("Please run this task on localhost.")
#         return

#     scenarios = [30]

#     for scenario in scenarios:
#         create_plot(
#             scenario=scenario,
#             oscillations=[2, 5],
#             wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
#             hsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
#             sigsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
#             tws=5,
#             results_dir_nlm_sq=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_tws_MD{scenario}_hsuper"),
#             output_dir=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_tws_MD{scenario}_hsuper", "plots")
#         )


# @task
# @load_plugin_env_vars("FabMaMiCo")
# def mamico_study_3_filter_nlm_tws_plot_selected(**args):
#     from plugins.FabMaMiCo.scripts.postprocess.study_3_filter_nlm_tws.plot import create_plot

#     if (env.host != "localhost"):
#         print("Please run this task on localhost.")
#         return

#     scenarios = [30]

#     for scenario in scenarios:
#         create_plot(
#             scenario=scenario,
#             oscillations=[2, 5],
#             wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
#             hsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
#             sigsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
#             tws=5,
#             results_dir_nlm_sq=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_tws_MD{scenario}_hsuper"),
#             output_dir=os.path.join(env.local_results, f"fabmamico_study_3_filter_nlm_tws_MD{scenario}_hsuper", "plots")
#         )


##########################################
# NLM hsq and sigsq

@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_nlm(**args):

    scenarios = [
        # {"domain": 30, "job_wall_time": "01:00:00" },
        {"domain": 60, "job_wall_time": "12:00:00" },
    ]

    for scenario in scenarios:
        config = f"study_3_filter_nlm_sq_MD{scenario['domain']}"

        # 1. Make sure there is an existing installation of MaMiCo
        if not mamico_install(config, only_check=True):
            print("Please install MaMiCo first.")
            return

        # 2. Update the environment
        update_environment(args)
        update_environment({
            "mamico_dir": template(env.mamico_dir_template)
        })
        # Please be aware that this configuration is specific to HSUper!
        update_environment({
            "cores": 1,
            "corespernode": 1,
            "job_wall_time": scenario["job_wall_time"],
            "partition_name": "small_shared",
            "qos_name": "many-jobs-small_shared"
        })

        # 3. Generate the sweep directory
        generate_sweep(config)

        # 4. Transfer the configuration files to the remote machine
        with_config(config)
        execute(put_configs, config)

        # 5. Update the environment for the postprocessing
        update_environment({
            "mamico_venv": template(env.mamico_venv_template),
            "reduce_command": "python3",
            "reduce_script": "reduce.py",
            "reduce_args": f"--scenario={scenario['domain']}",
        })

        # 6. Run the ensemble
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, "SWEEP")
        env.script = 'run_and_reduce' if args.get("script", None) is None else args.get("script")
        run_ensemble(config, sweep_dir, **args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_nlm_plot(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study2_nlm.plot import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30, 60]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
            hsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            sigsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            tws=5,
            results_dir_nlm_sq=os.path.join(env.local_results, f"fabmamico_study2_nlm_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study2_nlm_MD{scenario}_hsuper", "plots")
        )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_study2_nlm_plot_selected(**args):
    from plugins.FabMaMiCo.scripts.postprocess.study2_nlm.plot_selected import create_plot

    if (env.host != "localhost"):
        print("Please run this task on localhost.")
        return

    scenarios = [30, 60]

    for scenario in scenarios:
        create_plot(
            scenario=scenario,
            oscillations=[2, 5],
            wall_velocities=[0.2, 0.8, 1.4, 1.8],
            hsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            sigsq_rel=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            tws=5,
            results_dir_nlm_sq=os.path.join(env.local_results, f"fabmamico_study2_nlm_MD{scenario}_hsuper"),
            output_dir=os.path.join(env.local_results, f"fabmamico_study2_nlm_MD{scenario}_hsuper", "plots")
        )
