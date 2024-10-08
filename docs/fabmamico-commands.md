# FabMaMiCo Commands

FabMaMiCo offers the following tasks to set up and run MaMiCo simulations.

## Verify FabMaMiCo Plugin Installation

### mamico_test_plugin
```sh
fabsim <machine> mamico_test_plugin
```
This should output a message that the FabMaMiCo plugin is installed correctly.
The parameters `<machine>` is irrelevant for this command.

## Get System Information
The following commands make use of the remote lmod system to load modules.

### mamico_ml_overview
```sh
fabsim <machine> mamico_ml_overview
```
This lists an overview of available modules that can be loaded via lmod on the remote machine.

### mamico_ml_available
```sh
fabsim <machine> mamico_ml_available:<query>
```
This lists a more detailed overview of available modules that can be loaded via lmod on the remote machine.
The optional parameter `<query>` can be used to filter the list of available modules.

### mamico_ml_keyword
```sh
fabsim <machine> mamico_ml_keyword:<keyword>
```
This searches modules that can be loaded via lmod on the remote machine for a specific keyword.

### mamico_ml
```sh
fabsim <machine> mamico_ml:<command>
```
This executes a specific lmod command on the remote machine.
The parameter `<command>` can be any valid lmod command, e.g. `avail`, `spider`, etc.
It is prepended with `module` automatically.

## Handle MaMiCo Installations

### mamico_install
```sh
fabsim <machine> mamico_install:<config>
```
This downloads the source code of MaMiCo and optionally of ls1-mardyn and OpenFOAM, transfers it to the remote machine and compiles it according to the configuration specified in `plugins/FabMaMiCo/config_files/<config>/settings.yml`.

!!! Note
    The compilation process is submitted as a job.
    However, certain remote hosts like HSUper require compilation on the login node.
    The job script is thus executed via `bash`, and its completion might take a while as the local shell shows the progress of the remote compilation.

### mamico_list_installations
```sh
fabsim <machine> mamico_list_installations:verbose
```
This lists all MaMiCo installations on the remote machine.
The optional parameter `verbose` provides the settings of each installations.

### mamico_installation_available
```sh
fabsim <machine> mamico_installation_available:<checksum>
```
This checks if a specific MaMiCo installation is available on the remote machine.

### mamico_remove_installation
```sh
fabsim <machine> mamico_remove_installation:<checksum>
```
This removes a specific MaMiCo installation from the remote machine, if it exists.

### mamico_remove_all_installations
```sh
fabsim <machine> mamico_remove_all_installations
```
This removes all MaMiCo installations from the remote machine.


## Execute MaMiCo Simulations

### mamico_run
```sh
fabsim <machine> mamico_run:<config>
```
This command internally calls the `mamico_install`-task to make sure the MaMiCo executable is available.
It then transfers all config files to the remote machine, generates a batch script file and submits it to the scheduler.

!!! Note
    Here, the command returns after the job has been submitted to the job scheduler.

!!! Note
    You can append the parameter `replicas=<number>` to run multiple replicas of the simulation.

### mamico_run_ensemble
```sh
fabsim <machine> mamico_run_ensemble:<config>
```
This internally calls the `mamico_install`-task to make sure the MaMiCo executable is available.
It requires multiple folders inside a `SWEEP`-directory.
If a `generate_ensemble.py` script is available in the config directory, the script is executed to populate the SWEEP/ directory.
The task copies all config files to the remote machine and generates a batch script file for each simulation.
Finally, it submits all jobs to the scheduler.

## MaMiCo Post-Processing
!!! Note
    The remote postprocessing is still under development.

## MaMiCo Monitoring

### mamico_stat
```sh
fabsim <machine> mamico_stat
```
This shows the output of `squeue` on the remote machine for the user defined in `machines_user.yml`.

### mamico_jobs_overview
```sh
fabsim <machine> mamico_jobs_overview
```
This shows the number of jobs in the queue (planned, running) on the remote machine for the user defined in `machines_user.yml`.

### mamico_jobs_cancel_all
```sh
fabsim <machine> mamico_jobs_cancel_all
```
This cancels all jobs in the queue on the remote machine for the user defined in `machines_user.yml`.
