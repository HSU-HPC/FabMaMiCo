# STUDY-2: POD filters - MD30


## Description

This case study investigates the influence of POD filters on the simulation results.
We are using an **MD30** scenario, with **wall-velocities 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8**.
The moving wall is located at the bottom of the domain and performs **either 2 or 5 harmonic oscillations** during the 1,000 coupling cycles.

The MD domain is initialized with 10,000 equilibration steps.


## Steps to reproduce

1. Generate the input files for the case study by running the `generate_ensemble.py`-script.
It will place 432 (9x2x8x3) configurations in the `SWEEP`-directory.
The `template_gauss.xml`-file serves as a template.

    ```bash
    python3 generate_ensemble.py
    ```

2. Submit the jobs as an ensemble to the remote machine.
<br>
    ```bash
    fabsim hsuper mamico_run_ensemble:study2_pod_MD30,cores=1,corespernode=1,job_wall_time="01:00:00",partition_name="small_shared",qos_name="many-jobs-small_shared"
    ```

3. Wait until all jobs have finished successfully.

4. Fetch the results from the remote machine.
<br>
    ```bash
    fabsim hsuper fetch_results:regex="*study2_pod_MD30*",files="res_pod.diff;res_raw.diff"
    ```


## Run with

HSUper
1 core


## Runtime

The simulation runs for about 30 minutes.