#!/bin/bash

#SBATCH --time=06:00:00
#SBATCH --nodes=64
#SBATCH --ntasks-per-node=72
#SBATCH --cpus-per-task=1
#SBATCH --partition=medium
#SBATCH --job-name="mamico_scale"
#SBATCH --output="output"

ml mpi/2021.6.0

export OMP_NUM_THREADS=1

cd /beegfs/project/MaMiCo/mmcp24-hpcasia-2024/configurations/part2/filter64_1
srun /beegfs/project/MaMiCo/mmcp24-hpcasia-2024/MaMiCo/build/couette
