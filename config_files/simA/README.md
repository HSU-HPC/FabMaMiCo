# simA

This is a basic MaMiCo simulation setup.

## Files
`settings.yml` is required for compilation of MaMiCo.
It contains information about the source code branch and compilation flags.

`couette.xml` contains the configuration for a basic Couette flow simulation.

## How to use

#### Compilation
To compile MaMiCo on the remote machine, call:
```bash
fabsim <remote-machine> mamico_install:simA
```

#### Running
To run the simulation, call:
```bash
fabsim <remote-machine> mamico_run:simA
```
This also makes sure, a valid installation of MaMiCo is available.

#### Running with replicas
To run the simulation with 5 replicas, call:
```bash
fabsim <remote-machine> mamico_run:simA:replicas=5
```