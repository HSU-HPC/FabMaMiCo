# Setting up Simulations

## Introduction

After setting up your remote machine for FabSim3, you can now set up your machine for FabMaMiCo simulations.

The plugin's directory structure contains these important files and folders:

```
FabMaMiCo
├─ config_files/
│  ├─ simA/
│  │  ├─ CheckpointSimpleMD_10000_periodic_0.checkpoint
│  │  ├─ CheckpointSimpleMD_10000_reflecting_0.checkpoint
│  │  ├─ config_mamico.yml
│  │  └─ couette.xml
│  └─ simB/
│     ├─ CheckpointSimpleMD_10000_periodic_0.checkpoint
│     ├─ CheckpointSimpleMD_10000_reflecting_0.checkpoint
│     ├─ config_mamico.yml
│     └─ couette.xml
├─ docs/
├─ helpers/
├─ scripts/
├─ templates/
├─ ...
├─ FabMaMiCo.py
├─ ...
├─ machines_FabMaMiCo_user_example.yml
├─ ...
```

### `config_files/`

Here, different folders contain different simulation setups.
Each folder contains a `config_mamico.yml` file, which specifies the configuration for the MaMiCo compilation.
Additionally, the folder contains the simulation-specific files, like the `couette.xml` file, which is used for the couette flow example.

### `docs/`

This folder contains the documentation for the FabMaMiCo plugin.

### `helpers/`

This folder contains helper functions for the FabMaMiCo plugin.
Amongst others, there are scripts to populate the `config_files`-directory.

### `scripts/`

This folder contains most of the logic for the FabMaMiCo plugin.

### `templates/`

This folder contains batch script templates.
Those templates are used to submit jobs to the job scheduler.

### `FabMaMiCo.py`

This is the main file of the FabMaMiCo plugin.
It defines the available tasks.

### `machines_FabMaMiCo_user_example.yml`

This file contains simulation-agnostic settings for individual simulation runs.
Copy or rename this file to `machines_FabMaMiCo_user.yml` and adjust the settings to your needs.
