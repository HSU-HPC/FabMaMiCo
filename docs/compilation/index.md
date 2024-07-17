# MaMiCo Compilation

## MPI

**`mpi: [True, False, String]`**

If `String`: execute the command to load MPI (this requires the user to know the environment of the remote host).

If `False`: Do not do anything, MPI is not required.

If `True`:

1. Check if `module load mpi` works.
2. If not, check if `module load openmpi` works.
3. If not, check if `module load mpich` works.
4. If not, check if `module load intelmpi` works.
5. If not, check if spack is installed
6. If spack is installed, check if `spack load mpi` works.
7. If not, install mpi with spack and load it.
8. If none of the above works, raise an error.

## Eigen

**`eigen: [True, False, String]`**

If `String`: execute the command to load Eigen (this requires the user to know the environment of the remote host).

If `False`: Do not do anything, Eigen is not required.

If `True`:

1. Check if `module load eigen` works.
2. If not, check if spack is installed
3. If spack is installed, check if `spack load eigen` works.
4. If not, install Eigen with spack and load it.
5. if none of the above works, clone git repository and install Eigen.
6. If none of the above works, raise an error.

## Pybind11

**`pybind11: [True, False, String]`**

If `String`: execute the command to load Pybind11 (this requires the user to know the environment of the remote host).

If `False`: Do not do anything, Pybind11 is not required.

If `True`:

1. Check if `module load pybind11` works.
2. Check if `module load py-pybind11` works.
3. If not, check if spack is installed
4. If spack is installed, check if `spack load pybind11` works.
5. If not, install Pybind11 with spack and load it.
6. If none of the above works, clone git repository and install Pybind11.
7. If none of the above works, raise an error.

## LS1

**`ls1: [True, False]`**

If `False`: Do not do anything, LS1 is not required.

If `True`:

The ls1-mardyn repository is cloned automatically and transferred to the remove host.
So we just need to compile it in-place.