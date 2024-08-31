# STUDY-3: No Filters - MD30


## Description
This case study investigates the influence of no filters on the simulation results.
We are using a **MD30** scenario here, with **wall-velocities 0.2, 0.4, 0.6, 0.8, and 1.0**.
The moving wall is located at the bottom of the domain and performs 2 harmonic oscillations during the 1,000 coupling cycles.

The MD domain is initialized with 10,000 equilibration steps.


## Steps to reproduce

1. Generate the input files for the case study by running the `generate_ensemble.py`-script.
It will place 5 configurations in the `SWEEP`-directory.
The `template_gauss.xml`-file serves as a template.

    ```bash
    python3 generate_ensemble.py
    ```

5. Submit the jobs as an ensemble to the remote machine.
<br>
    ```bash
    fabsim <remote-machine> mamico_run_ensemble:study_3_filter_nofilter_MD30_2osc
    ```

6. Fetch the results from the remote machine.
<br>
    ```bash
    fabsim <remote-machine> fetch_results:regex="*study_3_filter_nofilter_MD30_2osc*"
    ```


## Runtime

The simulation runs for about TODO hours/minutes.
