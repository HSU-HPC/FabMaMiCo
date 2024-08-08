# Machine Configuration

## General Information

FabSim3 uses three different machine configuration files:

- machine-specific configuration file: `FabSim3/fabsim/deploy/machines.yml`
    - This file is part of the FabSim3 repository.
    - It contains the machine-agnostic settings like the remote url, job scheduler commands, etc.
    - You should not need to change this file.
- user-specific configuration file: `FabSim3/fabsim/deploy/machines_user.yml`
    - This file is not part of FabSim3 repository, it is created during the installation of FabSim3.
    - It contains user-agnostic settings like username, partition, account, etc.
    - You should change this file to match your personal remote machine settings once you have installed FabSim3.
- plugin-specific configuration file: `FabSim3/plugins/FabMaMiCo/machines_FabMaMiCo_user.yml`
    - This file is not part of the FabMaMiCo plugin, you need to create it manually by copying and renaming the exemplary file.
    - It contains settings for individual simulation runs, like the number of cores or the time to be allocated for the job.
    - Change this file for each simulation run to match your personal simulation settings.

```
.
├─ fabsim/
│  └─ deploy/
│     ├─ machines.yml
│     ├─ machines_user.yml
│     ├─ (machines_user_example.yml)
│     └─ (machines_user_backup.yml)
├─ plugins/
│  └─ FabMaMiCo/
│     ├─ machines_FabMaMiCo_user.yml
│     └─ (machines_FabMaMiCo_user_example.yml)
```

## Set up a Remote Machine

Please follow the steps to configure your remote machine for FabSim3:

1. Machine-specific configuration file: `FabSim3/fabsim/deploy/machines.yml`
    - Check if the remote machine you want to use is already listed in the `machines.yml` file

2. User-specific configuration file: `FabSim3/fabsim/deploy/machines_user.yml`
    - Change the settings in `machines_user.yml` to match your personal remote machine settings
    - An example is given here:
    === "HSUper"

        ```yaml
        hsuper:
            username: "<your-username>"
            home_path_template: "/beegfs/home/m/$username"
            fabric_dir: "FabSim3" # The remote directory where FabSim3 is installed under the home directory
        ```

3. Plugin-specific configuration file: `FabSim3/plugins/FabMaMiCo/machines_FabMaMiCo_user.yml`
    - Copy the exemplary file `machines_FabMaMiCo_user_example.yml` and rename it to `machines_FabMaMiCo_user.yml`
    - Change the settings in `machines_FabMaMiCo_user.yml` to match your personal simulation settings
    - An example is given here:
    === "HSUper"

        ```yaml
        hsuper:
            compile_on_login_node: yes
            mamico_dir_template: "$home_path/MaMiCo"
            job_wall_time: "0-1:00:00"
            compile_threads: 16
            cores: 1
            corespernode: 144
            job_name_template: 'fabmamico_${config}_${machine_name}_${cores}_${task}'
            max_job_name_chars: 62
            modules:
                loaded: ["gcc/12.1.0", "cmake/3.23.1", "mpi/2021.10.0", "eigen/3.4.0"]
        ```

You can find a detailed explanation of the parameters on the [next page](/machine-configuration/parameters/).