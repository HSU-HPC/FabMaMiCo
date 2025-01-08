# STUDY-2: Gauss filters - MD60


## Description

This case study investigates the influence of Gauss filters on the simulation results.
We are using an **MD60** scenario, with **wall-velocities 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8**.
The moving wall is located at the bottom of the domain and performs **either 2 or 5 harmonic oscillations** during the 1,000 coupling cycles.

The MD domain is initialized with 20,000 equilibration steps.


## Steps to reproduce

1. Generate the input files for the case study by running the `generate_ensemble.py`-script.
It will place 18 (9x2) configurations in the `SWEEP`-directory.
The `template_gauss.xml`-file serves as a template.

    ```bash
    python3 generate_ensemble.py
    ```

2. Submit the jobs as an ensemble to the remote machine.
<br>
    ```bash
    fabsim hsuper mamico_run_ensemble:study2_gauss_MD60,cores=1,corespernode=1,job_wall_time="11:00:00",partition_name="small_shared",qos_name="many-jobs-small_shared"
    ```

3. Wait until all jobs have finished successfully.

4. Fetch the results from the remote machine.
<br>
    ```bash
    fabsim hsuper fetch_results:regex="*study2_gauss_MD60*",files="res_gauss_2d.diff;res_gauss_3d.diff;res_raw.diff"
    ```


## Running with

HSUper
1 core


## Runtime

The simulation runs for about 8 hours.