# STUDY-3: No Filters - MD60 - 5 oscillations


## Description
This case study investigates the influence of no filters on the simulation results.
We are using a **MD60** scenario here, with **wall-velocities 0.2, 0.4, 0.6, 0.8, and 1.0**.
The moving wall is located at the bottom of the domain and performs **5 harmonic oscillations** during the 1,000 coupling cycles.

The MD domain is initialized with 20,000 equilibration steps.


## Steps to reproduce

1. Generate the input files for the case study by running the `generate_ensemble.py`-script.
It will place 5 configurations in the `SWEEP`-directory.
The `template_nofilter.xml`-file serves as a template.

    ```bash
    python3 generate_ensemble.py
    ```

2. Submit the jobs as an ensemble to the remote machine.
<br>
    ```bash
    fabsim <remote-machine> mamico_run_ensemble:study_3_filter_nofilter_MD60_5osc
    ```

3. Fetch the results from the remote machine.
<br>
    ```bash
    fabsim <remote-machine> fetch_results:regex="*study_3_filter_nofilter_MD60_5osc*"
    ```


## Run with

1600 cores (200 MD instances with 2;2;2 domain split)


## Runtime

The simulation runs for about 2.5 hours.