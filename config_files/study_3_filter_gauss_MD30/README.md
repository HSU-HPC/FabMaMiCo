# STUDY-3: Gauss filters - MD30


## Description
This case study investigates the influence of Gauss filters on the simulation results.
We are using a **MD30** scenario here, with **wall-velocities 0.2, 0.4, 0.6, 0.8, and 1.0**.

The checkpoint has been generated before (see `study_3_filter_CP`).


## Steps to reproduce

1. Generate the input files for the case study by running the `populate.py`-script.
It will place 5 configurations in the `SWEEP`-directory.
The `template_gauss.xml`-file serves as a template and also contains the import of the previously generated checkpoint file.

    ```bash
    python populate.py
    ```

5. Submit the jobs as an ensemble to the remote machine.
<br>
    ```bash
    fabsim <remote-machine> mamico_run_ensemble:study_3_filter_gauss_MD30
    ```

6. Fetch the results from the remote machine.
<br>
    ```bash
    fabsim <remote-machine> fetch_results
    ```


## Runtime

The simulation runs for about 30 minutes.