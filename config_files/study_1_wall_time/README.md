BENCHMARKS: Hyperthreading aus

# Case Study 1: Walltime Variance

In this case study, the walltime variance of different remote machines is examined.

This simulation uses ls1-mardyn as microscopic solver.
On each machine, we trigger 50 replicas of short MaMiCo simulations (50 coupling cycles) with 8 MPI processes (runtime < 1 min).
The simulations are initialized with checkpoint files previously generated (see `checkpoint_generation`), 10001 equilibration steps.

Two setups are created:
1 node, 8 cores, 1 MPI process per core
2 nodes, 4 cores per node, 1 MPI process per core

- hsuper
/ minicluster
/ cosma
/ ants
/ sofia
/ fritz