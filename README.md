# FabMaMiCo
FabMaMiCo is a [FabSim3](https://fabsim3.readthedocs.io/) plugin for automated [MaMiCo](https://github.com/HSU-HPC/MaMiCo) simulations.
It provides a simple setup for installing and running single jobs, job ensembles and replicas of MaMiCo simulations on remote machines.

## Documentation

Please refer to the [documentation](https://hsu-hpc.github.io/FabMaMiCo/).

--------------------------------------------------------------------

## Installation
Having FabSim3 installed on your local machine, you can install FabMaMiCo by running the following command in the FabSim3 directory:

```bash
fabsim localhost install_plugin:FabMaMiCo
```


## Development

Please be aware that this plugin is still under active development.

For development, please install the plugin locally by cloning the source code into the FabSim3-directory `plugins/FabMaMiCo`.

Also update your `plugins.yml` in `fabsim/deploy/` in order to not overwrite the changes when updating FabSim3-plugins.
```yml
FabMaMiCo:
  repository: <empty>
```


## Testing

```bash
isort --profile hug --skip plugins/FabMaMiCo/tmp --check --diff -l 80 plugins/FabMaMiCo 
pytest tests/test_fabsim.py  
```
