

## Execute MaMiCo on a remote machine

```bash
fabsim hsuMini00 mamico:test_installation # here <config> is test_installation
```

The folder `/home/jo` is given in `machines_user.yml` as `home_path_template`.
There, a folder `FabSim` is created, which serves as the main directory for FabMaMiCo.

A) Folders created:
- `/home/jo/FabSim/config_files`
  - `/home/jo/FabSim/config_files/<config>`
- `/home/jo/FabSim/results`
- `/home/jo/FabSim/scripts`

B) Copy the input files to the remote machine:
- `/home/jo/FabSim/config_files/<config>/`

C) Create jobs:
Create a script in local:`fabsim/deploy/<config>_<machine_name>_<cores><job_desc>.sh`.
This uses the template in `fabsim/deploy/templates/<batch_header>`, where `batch_header` is defined in `machines.yml`.

The following part of the script is taken from the template given in `plugins/FabMaMiCo/templates/<config>/<task>`.
The `$run_prefix` command loads the modules given in `machines.yml` and copies the config-files to the results folder for later reference (as defined in `fabsim/base/fab.py`).

Send the script to the remote machine in folder `/home/jo/FabSim/scripts`

D) Copy the inputs to the remote machine:
As we would like to save for later times what we have executed and what the environment looks like, we copy the input files to the remote machine.
Therefore, a folder `<config>_<machine_name>_<cores>` is created in `/home/jo/FabSim/results/` and the script and a snapshot of the environment (as `env.yml`) is placed there.

E) Submit all generated job scripts to the target machine
This basically just calls `sbatch <job-script>` (see `fabsim/base/fab.py:job_submission`).


## Explanation of files
* FabMaMiCo.py - main file containing the ```fabsim localhost mamico``` command implementation.
* config_files/test_installation - directory containing input data for the installation command.
* templates/test_installation - template file for running the test-installation command on the remote machine.

## Detailed Examples

Please, for now, refer to [FabDummy](https://github.com/djgroen/FabDummy).

## Adding a machine

1. To add a machine, you need to add a new entry to the `machines.yml` file.
The following lines serve as an example:

```yml
hsuMini00:
  remote: "minicluster00.unibw-hamburg.de"
  manual_sshpass: true
  batch_header: slurm-hsuMini00
  job_dispatch: "sbatch"
  stat: "squeue -u $username --noheader"
  cancel_job_command: 'scancel $jobID'
  job_info_command : 'squeue --jobs $jobID'
  run_command: "mpirun -np $cores"
  job_wall_time: "0-0:01:00"
  home_path_template: "/home/$username"
  temp_path_template: "$work_path/tmp"
  cores: 1 # 16 per default
  modules:
    # list of modules to be loaded on remote machine
    loaded: ["miniconda3/"]
```

2. You also need to add a new entry to the `machines_user.yml` file:

```yml
hsuMini00:
  local_results: # define where to locally load the results after computation
  username: # your username on the remote machine
  home_path_template: # the path to your home directory on the remote machine
  sshpass: # path a file containing the password for the remote machine
```

:warning: Please do not share or commit your password to any repository.
The file containing your password should strictly stay on your local machine.

3. Last but not least you need to add the machine's name to the list of machine in `lists/machines.txt`:

```txt
machines="[...] hsuMini00"
```


## Dependencies

### sshpass
To authenticate with remote machines using a password, you will need to install [sshpass](https://linux.die.net/man/1/sshpass) on your local machine.
