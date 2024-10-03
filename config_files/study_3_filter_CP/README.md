# STUDY-3: Filters - Checkpoint Generation


## Description

There are two scenarios, MD30 and MD60, which are based on the same initial configuration.
For both of the scenarios, the scripts will create a checkpoint file, which will be used in the case studies.

## Information

The simulation will only perform equilibration steps and generate a checkpoint file.

| Configuration                                                           | Value for MD30              | Value for MD60              |
|-------------------------------------------------------------------------|-----------------------------|-----------------------------|
| couette-test/domain/channelheight                                       | 50                          | 100                         |
| mamico/macroscopic-cell-configuration/cell-size                         | "2.5 ; 2.5 ; 2.5"           | "5.0 ; 5.0 ; 5.0"           |
| mamico/macroscopic-cell-configuration/linked-cells-per-macroscopic-cell | "1 ; 1 ; 1"                 | "2 ; 2 ; 2"                 |
| molecular-dynamics/simulation-configuration/number-of-timesteps         | 50                          | 100                         |
| molecular-dynamics/domain-configuration/molecules-per-direction         | "28 ; 28 ; 28"              | "56 ; 56 ; 56"              |
| molecular-dynamics/domain-configuration/domain-size                     | "30.0 ; 30.0 ; 30.0"        | "60.0 ; 60.0 ; 60.0"        |
| molecular-dynamics/domain-configuration/domain-offset                   | "10.0 ; 10.0 ; 2.5"         | "20.0 ; 20.0 ; 5.0"         |
| couette-test/microscopic-solver/equilibration-steps                     | 10001                       | 20001                       |
| molecular-dynamics/checkpoint-configuration/filename                    | "CheckpointSimpleMD30"      | "CheckpointSimpleMD60"      |
| molecular-dynamics/checkpoint-configuration/write-every-timestep        | 10000                       | 20000                       |


## Steps to reproduce

1. Run the `generate_ensemble.py`-script to generate the input files for the two scenarios MD30 and MD60.
   This creates the `SWEEP`-directory with the configurations.
<br>
    ```bash
    python generate_ensemble.py
    ```

2. Submit a job ensemble to the remote machine.
   This will generate the checkpoint file for each scenario `CheckpointSimpleMD30_10000_0.checkpoint` and `CheckpointSimpleMD60_20000_0.checkpoint`.
<br>
    ```bash
    fabsim hsuper mamico_run_ensemble:study_3_filter_gauss:CP
    ```

3. Fetch the results from the remote machine, amongst which is the checkpoint-file.
<br>
    ```bash
    fabsim hsuper fetch_results regex="*study_3_filter_CP*"
    ```

4. Place the checkpoint files into other configuration directories - they are already included as part of the repository.
