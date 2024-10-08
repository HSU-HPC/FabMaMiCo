# Machine Configuration

## General Information

FabSim3 includes a list of preconfigured machines.
The parameters for each machine are stored in `.yml` files.
While some parameters are globally valid, others are specific to the user or the simulation run.

FabSim3 thus uses three different machine configuration files:

- **machine-specific** configuration file: `FabSim3/fabsim/deploy/machines.yml`
    - This file is part of the public FabSim3 repository.
    - It contains the machine-agnostic settings like the remote url, job scheduler commands, etc.
    - You should not need to change this file.
- **user-specific** configuration file: `FabSim3/fabsim/deploy/machines_user.yml`
    - This file is not part of the FabSim3 repository, it is created during the installation of FabSim3.
    - It contains user-agnostic settings like username, account, etc.
    - You should change this file to match your personal remote machine settings once you have installed FabSim3.
- **plugin-specific** configuration file: `FabSim3/plugins/FabMaMiCo/machines_FabMaMiCo_user.yml`
    - This file is not part of the FabMaMiCo plugin, you need to create it manually by copying and renaming the exemplary file.
    - It contains plugin-specific parameters, like the remote installation path for MaMiCo, etc.
    - Adapt this file to your needs and even consider changing it for individual task executions.

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

Parameters that are defined multiple times are resolved in the following order:
1. **Plugin-specific** configuration file
2. **User-specific** configuration file
3. **Machine-specific** configuration file

This means a parameter defined in the plugin-specific configuration file will overwrite the same parameter defined in the user-specific configuration file, which in turn will overwrite the same parameter defined in the machine-specific configuration file.

Parameters can contain placeholders (`$placeholder`).
If specified, they are resolved in runtime.


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
            fabric_dir: "FabSim3" # The remote directory where FabSim3 is placing input and output files
        ```

3. Plugin-specific configuration file: `FabSim3/plugins/FabMaMiCo/machines_FabMaMiCo_user.yml`
    - Copy the exemplary file `machines_FabMaMiCo_user_example.yml` and rename it to `machines_FabMaMiCo_user.yml`
    - Change the settings in `machines_FabMaMiCo_user.yml` to match your personal plugin/simulation settings
    - An example is given here:
    === "HSUper"

        ```yaml
        hsuper:
            compile_on_login_node: yes
            cores: 1
            partition_name: "small_shared"
            job_name_template: 'fabmamico_${config}_${machine_name}_${cores}${job_desc}'
            max_job_name_chars: 80
            modules:
                compile: ["load gcc/13.2.0", "load cmake/3.27.9", "load openmpi/5.0.3-cuda", "load eigen/3.4.0"]
                run: ["load openmpi/5.0.3-cuda"]
                postprocess: ["load python/3.11"]
        ```

You can find a detailed explanation of the parameters on the [next page (Parameters)](/machine-configuration/parameters/).