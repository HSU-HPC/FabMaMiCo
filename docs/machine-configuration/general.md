# Machine Configuration

## General Information

To set up remote machines for FabSim3, you need to understand how FabSim3 handles machine configurations.

By default, FabSim3 uses two different machine configuration files:

- machine-specific configuration file: `FabSim3/fabsim/deploy/machines.yml`
    - This file is part of the *FabSim3* repository
    - It contains the default settings like remote url, job scheduler-dependent commands, number of nodes, etc.
    - You should not need to change this file
- user-specific configuration file: `FabSim3/fabsim/deploy/machines_user.yml`
    - This file is not part of *FabSim3* repository
    - It contains user-specific settings like username, partition, account, etc.
    - You should change this file to match your personal remote machine settings

There is one more file that you can use to alter the default settings.  
This file is part of the FabMaMiCo plugin and is called `machines_FabMaMiCo_user.yml`.
It contains settings for individual simulation runs, like the number of nodes, the number of cores per node, or the time to be allocated for the job.

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
│     └─ (machines_FabMaMiCo_user_example.yml)
```

## Set up a Remote Machine

Please follow the steps to configure your remote machine for FabSim3:

1. User-specific configuration file: `FabSim3/fabsim/deploy/machines_user.yml`
    - Change the settings in `machines_user.yml` to match your personal remote machine settings
    - An example is given here:

    === "HSUper"

        ```yaml
        hsuper:
            username: "<your-username>"
            job_name_template: '${config}_${machine_name}_${cores}_${task}'
            max_job_name_chars: 36
            fabric_dir: "FabSim" # The remote directory where FabSim3 is installed under the home directory
        ```

2. We will take care of the simulation-agnostic settings in the `machines_FabMaMiCo_user.yml` file later.