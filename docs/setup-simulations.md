# Setting up Simulations

## Introduction

After setting up your remote machine for FabSim3, FabMaMiCo simulations can be set up to be run on the remote machine.

The plugin's directory structure contains these important files and folders:

```
FabMaMiCo
├─ config_files/
│  ├─ simA/
│  │  ├─ CheckpointSimpleMD_10000_reflecting_0.checkpoint
│  │  ├─ settings.yml
│  │  └─ couette.xml
│  └─ simB/
│     ├─ CheckpointSimpleMD_10000_reflecting_0.checkpoint
│     ├─ settigns.yml
│     └─ couette.xml
├─ docs/
├─ helpers/
├─ scripts/
├─ templates/
├─ utils/
├─ ...
├─ FabMaMiCo.py
├─ ...
├─ machines_FabMaMiCo_user_example.yml
├─ ...
```

### `config_files/`

Here, different folders contain different MaMiCo simulation setups.
Each folder contains a `settings.yml` file, which specifies the configuration for the MaMiCo compilation.
Additionally, the folder contains the simulation-specific files, like the `couette.xml` file, which is used for the couette flow example, or some checkpoint files.

### `docs/`

This folder contains the documentation for the FabMaMiCo plugin.

### `scripts/`

This folder contains most of the logic for the FabMaMiCo plugin.

### `templates/`

This folder contains batch script templates.
Those templates are used to populate the batch script templates.

### `FabMaMiCo.py`

This is the main file of the FabMaMiCo plugin.
It defines the available tasks that can be executed through FabSim3.

### `machines_FabMaMiCo_user_example.yml`

This file contains simulation-agnostic settings for individual simulation runs.
Copy or rename this file to `machines_FabMaMiCo_user.yml` and adjust the settings to your needs.
