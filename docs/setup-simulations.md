# Setting up Simulations

## Introduction

After setting up your remote machine for **FabSim3**, **FabMaMiCo** simulations can be set up to be run on the remote machine.

The plugin's directory structure contains these important files and folders:

```
FabMaMiCo
├─ config_files/
│  ├─ simA/
│  │  ├─ CheckpointSimpleMD_10000_reflecting_0.checkpoint
│  │  ├─ settings.yml
│  │  └─ couette.xml
│  └─ simB/
│  │  ├─ CheckpointSimpleMD_10000_reflecting_0.checkpoint
│  │  ├─ settigns.yml
│  │  └─ couette.xml
│  └─ [...]
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
Each folder contains a `settings.yml` file, which specifies the MaMiCo compilation.
Compilation flags as well as parameters related to other solvers like ls1-mardyn or OpenFOAM are defined here.
Additionally, the folder contains the simulation-specific files, like the `couette.xml` file, which is used for the couette flow example, or some checkpoint files.
If this configuration is intended to run a job ensemble (multiple simulations with different input), the folder `SWEEP/` is used to store the different configurations.
An example is given in the `config_files/study_3_filter_nlm_sq_MD30` folder.
In this configuration, there is also a Python script `generate_ensemble.py`, which can be used to generate the different configurations for the job ensemble.

### `docs/`

This folder contains the documentation for the FabMaMiCo plugin.
The documentation is written in Markdown and can be viewed in the browser.
For convenience, mkdocs is used to generate a static website from the Markdown files.
The documentation is generating these very pages.

### `scripts/`

This folder contains most of the logic for the FabMaMiCo plugin.
There are scripts for the different tasks that can be executed through FabSim3.
Among others, the logic for MaMiCo compilation is implemented in `scripts/setup.py`, and a reader for the `settings.yml` file is implemented in `scripts/settings.py`.

### `templates/`

This folder contains batch script templates.
Those templates are appended to the machine-specific batch script header.
The templates are used to define the commands executed in specific tasks.
They usually contain placeholders that are populated with the actual values during task execution.
After the placeholders are replaced, the batch script is written to the remote machine and executed.

### `FabMaMiCo.py`

This is the main file of the FabMaMiCo plugin.
It defines the available tasks that can be executed through FabSim3.

### `machines_FabMaMiCo_user_example.yml`

This file contains plugin-agnostic parameters.
Copy or rename this file to `machines_FabMaMiCo_user.yml` and adjust the settings to your needs.
