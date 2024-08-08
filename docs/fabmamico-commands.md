# FabMaMiCo Commands

FabMaMiCo offers the following commands to set up and run MaMiCo simulations.

### Verify FabMaMiCo Installation

```sh
fabsim <machine> fabmamico_test_installation
```

This should output a message that the FabMaMiCo plugin is installed correctly.

### Install MaMiCo

```sh
fabsim <machine> mamico_install:<config>
```

This downloads the source code of MaMiCo, transfers it to the remote machine and compiles it according to the configuration specified in `plugins/FabMaMiCo/config_files/<config>/settings.yml`.

!!! Note
    On HSUper, we want to compile on the login node, so this might take a while, as the local shell shows the progress of the compilation.

### Run A Single MaMiCo Simulation

```sh
fabsim <machine> mamico_run:<config>
```

This command internally calls the `mamico_install`-task to make sure the MaMiCo executable is available.
It then transfers all config files to the remote machine, generates a batch script file and submits it to the scheduler.

!!! Note
    Here, the command returns after the job has been submitted to the job scheduler.

### Run Multiple Replicas of a MaMiCo Simulation

```sh
fabsim <machine> mamico_run:<config>,replicas=<number>
```

This command internally calls the `mamico_install`-task to make sure the MaMiCo executable is available.
It then creates multiple replicas of the simulation by submitting multiple jobs to the scheduler.
Use with e.g. the configuration `simA`.

### Run an Ensemble of MaMiCo Simulations

```sh
fabsim <machine> mamico_run_ensemble:<config>
```

This command internally calls the `mamico_install`-task to make sure the MaMiCo executable is available.
It requires multiple folders inside a `SWEEP`-directory.
The task copies all config files to the remote machine and generates a batch script file for each simulation.
Finally, it submits all jobs to the scheduler.


### Check How Many Jobs Are Running

```sh
fabsim <machine> mamico_jobs_overview
```

### Show Queue Status

```sh
fabsim <machine> mamico_stat
```

### Cancel All FabMaMiCo Jobs

```sh
fabsim <machine> mamico_jobs_cancel_all
```

### List MaMiCo installations

```sh
fabsim <machine> mamico_list_installations
```

### Remove a single MaMiCo installation

```sh
fabsim <machine> mamico_remove_installation:<checksum>
```

### Remove all MaMiCo installations

```sh
fabsim <machine> mamico_remove_all_installations
```
