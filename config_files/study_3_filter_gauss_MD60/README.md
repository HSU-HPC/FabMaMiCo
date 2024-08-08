# STUDY-3: Gauss filters



## Steps to reproduce

1. Submit a job to the remote machine with the `checkpoint_generation/couette.xml`-file.
This will generate the checkpoint file `CheckpointSimpleMDGauss_10000_0.checkpoint`.
<br>
    ```bash
    fabsim <remote-machine> mamico_run:study_3_filter_gauss
    ```

2. Fetch the results from the remote machine, amongst which is the checkpoint-file.
<br>
    ```bash
    fabsim <remote-machine> fetch_results
    ```

3. Place the checkpoint file into the configuration directory.
<br>
    ```bash
    cp <your-fabsim-installation-path>/results/fabmamico_study_3_filter_gauss_<remote-machine>_1_mamico_run/results/CheckpointSimpleMDGauss_0__10000_0.checkpoint .
    ```

4. Generate the input files for the case study by running the `populate.py`-script.
It will place 10 configurations in the `SWEEP`-directory.
The `template_gauss.xml`-file serves as a template and also contains the import of the previously generated checkpoint file.

    ```bash
    python populate.py
    ```

5. Submit the jobs as an ensemble to the remote machine.
<br>
    ```bash
    fabsim <remote-machine> mamico_run_ensemble:study_3_filter_gauss
    ```

6. Fetch the results from the remote machine.
<br>
    ```bash
    fabsim <remote-machine> fetch_results
    ```