# FabMaMiCo Commands

FabMaMiCo offers the following commands to set up and run MaMiCo simulations.

### Install MaMiCo

```sh
fabsim <machine> mamico_install:<config>
```

This downloads the source code of MaMiCo, transfers it to the remote machine and compiles it according to the configuration specified in `plugins/FabMaMiCo/config_files/config_mamico.yml`.

On hsuper, we want to compile on the login node, so this might take a while, as the local shell shows the progress of the compilation.

### Run MaMiCo Simulation

```sh
fabsim <machine> mamico_run:<config>
```

This command makes sure, the MaMiCo executable is available and runs the simulation.  
The couette flow example is used as a default example.
It requires the three files contained in the example configuration folder `plugins/FabMaMiCo/config_files/simA`.

Here, the command returns after the job has been submitted to the job scheduler.

### Check Job Status

The output of the `mamico_run`-command contains the job ID of the submitted job.
You can check the status of the job using the following command:

```sh
fabsim <machine> stat:<job_id>
```

### Wait for Job to Finish

If you want to wait for all submitted jobs to finish, you can use the following command:

```sh
fabsim <machine> wait_complete
```

### Retrieve Simulation Results

After the job has finished, you can retrieve the simulation results using the following command:

```sh
fabsim <machine> fetch_results
```

You can find the results in the `results` folder on your local machine, defined in `fabsim/deploy/machines_user.yml` under the key `local_results`.