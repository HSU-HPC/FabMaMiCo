import os

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from typing import *
from vtk import *


def get_df_from_filter_csv(folder, filename):
    ########################################
    # Load the data
    df = pd.read_csv(
        filepath_or_buffer=os.path.join(folder, filename),
        header=None,
        delimiter=";",
        names=["iteration", "mass", "mom_x", "mom_y", "mom_z"],
        usecols=[i for i in range(5)],
        dtype={"iteration": np.int32, "mass": float, "mom_x": float, "mom_y": float, "mom_z": float},
    )

    ########################################
    # Filter iterations >= 100, <= 1000, and every 10th iteration
    df = df[(df["iteration"] >= 100) & (df["iteration"] <= 1000) & (df["iteration"] % 10 == 0)]

    ########################################
    # Extract scenario values
    iterations = len(df["iteration"].unique())
    cells_in_each_dim = 6

    ########################################
    # Add the indices for each iteration
    ix = np.tile(np.arange(0, cells_in_each_dim), cells_in_each_dim ** 2)
    iy = np.tile(np.repeat(np.arange(0, cells_in_each_dim), cells_in_each_dim), cells_in_each_dim)
    iz = np.repeat(np.arange(0, cells_in_each_dim), cells_in_each_dim ** 2)
    # populate the dataframe with indices for each iteration
    df["idx_x"] = np.tile(ix, iterations)
    df["idx_y"] = np.tile(iy, iterations)
    df["idx_z"] = np.tile(iz, iterations)

    ########################################
    # Sort by iteration and indices
    df = df.sort_values(["iteration", "idx_z", "idx_y", "idx_x"], ascending=[True, True, True, True])

    return df


def get_df_from_cfd_vtk(folder, shape, scenario=30):
    ########################################
    # Create an empty numpy array
    numpy_array = np.zeros(shape)

    # Row counter for final result-array
    row = 0

    ########################################
    # Find and sort the vtk files
    vtk_files = [f for f in os.listdir(folder) if f.endswith(".vtk")]
    vtk_files.sort()
    # extract number from e.g. 'LBCouette_r0_c1000.vtk'
    iteration = lambda f: int(f.split("_")[2][1:-4])
    vtk_files = [(iteration(f), f) for f in vtk_files if iteration(f) >= 100 and iteration(f) <= 1000]

    ########################################
    # Iterate over the vtk files and extract the data
    for i, f in sorted(vtk_files):
        index = i // 10 - 10
        reader : vtkStructuredGridReader = vtkStructuredGridReader()
        reader.SetFileName(os.path.join(folder, f))
        reader.ReadAllScalarsOn()
        reader.Update()

        # Get the structured grid
        grid : vtkStructuredGrid = reader.GetOutput()

        # Get the dimensions of the grid
        dims = [-1, -1, -1]
        grid.GetDimensions(dims)

        # Get the number of cells
        n_cells = grid.GetNumberOfCells()

        # Set the number of MD cells and the offsets
        md_cells = [6, 6, 6]
        md_cell_offsets = [8, 8, 5]

        # Get the density and velocity arrays
        densities  : vtkDataArray = grid.GetCellData().GetScalars("density")
        velocities : vtkDataArray = grid.GetCellData().GetVectors("velocity")

        # Get the indices of the MD cell
        min_x, max_x = md_cell_offsets[0], md_cell_offsets[0] + md_cells[0] - 1
        min_y, max_y = md_cell_offsets[1], md_cell_offsets[1] + md_cells[1] - 1
        min_z, max_z = md_cell_offsets[2], md_cell_offsets[2] + md_cells[2] - 1

        offset = 2.5 if scenario == 30 else 5

        # Iterate over inner MD cells (6x6x6)
        for cell in range(n_cells):
            pos = ((np.array(grid.GetCell(cell).GetBounds()) + offset) / offset).astype(int)[::2]
            if min_x <= pos[0] <= max_x and min_y <= pos[1] <= max_y and min_z <= pos[2] <= max_z:
                # print(f"Cell {cell}: {n} - {list(densities.GetTuple(cell)) + list(velocities.GetTuple(cell))}")
                numpy_array[row] = [i] + list(densities.GetTuple(cell)) + list(velocities.GetTuple(cell)) + [pos[0] - min_x, pos[1] - min_y, pos[2] - min_z]
                row += 1
        # row should be 216 (6x6x6)

    df = pd.DataFrame(
        numpy_array,
        columns=["iteration", "density", "vel_x", "vel_y", "vel_z", "idx_x", "idx_y", "idx_z"],
    )
    df = df.astype({"iteration": np.int32, "density": float, "vel_x": float, "vel_y": float, "vel_z": float, "idx_x": np.int32, "idx_y": np.int32, "idx_z": np.int32})
    df = df.sort_values(["iteration", "idx_z", "idx_y", "idx_x"], ascending=[True, True, True, True])

    return df
