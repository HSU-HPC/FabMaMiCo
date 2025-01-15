# simA

This is a basic MaMiCo simulation setup.

## Files
`settings.yml` is required for compilation of MaMiCo.
It contains information about the source code branch and compilation flags.

`couette.xml` contains the configuration for an exemplary couette flow simulation with 1000 initilization steps for 2 MD domains.

## How to use

#### Compilation
To compile MaMiCo on the remote machine, call:
```bash
fabsim <remote-machine> mamico_install:simA
```

#### Running
To run the simulation, call:
```bash
fabsim <remote-machine> mamico_run:simA,cores=2
```
This also makes sure, a valid installation of MaMiCo is available.

#### Running with replicas
To run the simulation with 5 replicas, call:
```bash
fabsim <remote-machine> mamico_run:simA:cores=2,replicas=5
```