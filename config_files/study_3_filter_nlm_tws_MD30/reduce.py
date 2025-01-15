import argparse
import os

import numpy as np
import pandas as pd

from typing import *
from vtk import *


def get_df_from_filter_csv(filename, min=100, max=1000, step=10):
    """
    Reads the (filter output) csv file in current working directory and creates an indexed dataframe.
    Only iterations >= 100, <= 1000, and every 10th iteration are considered.
    The dataframe is sorted by iteration and x,y,z indices.

    Args:
        filename (str): The name of the csv file.

    Returns:
        pd.DataFrame: The indexed dataframe.
    """
    ########################################
    # Load the data
    df = pd.read_csv(
        filepath_or_buffer=filename,
        header=None,
        delimiter=";",
        names=["iteration", "mass", "mom_x", "mom_y", "mom_z"],
        usecols=[i for i in range(5)],
        dtype={"iteration": np.int32, "mass": float, "mom_x": float, "mom_y": float, "mom_z": float},
    )

    ########################################
    # Filter iterations >= 100, <= 1000, and every 10th iteration
    df = df[(df["iteration"] >= min) & (df["iteration"] <= max) & (df["iteration"] % step == 0)]

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

    df['vel_x'] = df['mom_x'] / df['mass']
    df['vel_y'] = df['mom_y'] / df['mass']
    df['vel_z'] = df['mom_z'] / df['mass']

    return df


def get_df_from_cfd_vtk(scenario=30, min=100, max=1000, step=10):
    """
    Reads the vtk files in the current working directory and creates an indexed dataframe.
    Only iterations >= 100, <= 1000, and every 10th iteration are considered.
    The dataframe is sorted by iteration and x,y,z indices.

    Args:
        scenario (int): The scenario number.

    Returns:
        pd.DataFrame: The indexed dataframe.
    """

    ########################################
    # Set factor to convert from vtk units
    # to mamico units
    factor = 10
    # explanation:
    # MD30: dt_md = 0.005                \
    #       dt_lb = dt_md * n_time_steps |
    #             = 0.005 * 50           |>  v_mamico = v_vtk * dx_lb / dt_lb = v_vtk * 10
    #             = 0.25                 |
    #       dx_lb = 2.5                  /

    # MD60: dt_md = 0.005                \
    #       dt_lb = dt_md * n_time_steps |
    #             = 0.005 * 100          |>  v_mamico = v_vtk * dx_lb / dt_lb = v_vtk * 10
    #             = 0.5                  |
    #       dx_lb = 5.0                  /


    ########################################
    # Find and sort the vtk files
    vtk_files = [f for f in os.listdir(os.getcwd()) if f.endswith(".vtk")]
    vtk_files.sort()
    # extract number from e.g. 'LBCouette_r0_c1000.vtk'
    iteration = lambda f: int(f.split("_")[2][1:-4])
    vtk_files = [(iteration(f), f) for f in vtk_files if iteration(f) >= min and iteration(f) <= max and iteration(f) % step == 0]

    ########################################
    # Create an empty numpy array
    # 6x6x6 cells * 91 coupling cycles x 8 quantities (it, dens, v_x, v_y, v_z, idx_x, idx_y, idx_z)
    numpy_array = np.zeros((6*6*6*len(vtk_files),8))

    # Row counter for final result-array
    row = 0

    ########################################
    # Iterate over the vtk files and extract the data
    for i, f in sorted(vtk_files):
        reader : vtkStructuredGridReader = vtkStructuredGridReader()
        reader.SetFileName(os.path.join(os.getcwd(), f))
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
                numpy_array[row] =  [i] + list(densities.GetTuple(cell)) \
                                        + list(velocities.GetTuple(cell)) \
                                        + [pos[0] - min_x, pos[1] - min_y, pos[2] - min_z]
                row += 1

    df = pd.DataFrame(
        numpy_array,
        columns=["iteration", "density", "vel_x", "vel_y", "vel_z", "idx_x", "idx_y", "idx_z"],
    )
    df = df.astype({"iteration": np.int32, "density": float, "vel_x": float, "vel_y": float, "vel_z": float, "idx_x": np.int32, "idx_y": np.int32, "idx_z": np.int32})
    df = df.sort_values(["iteration", "idx_z", "idx_y", "idx_x"], ascending=[True, True, True, True])

    df['vel_x_mamico'] = df['vel_x'] * factor
    df['vel_y_mamico'] = df['vel_y'] * factor
    df['vel_z_mamico'] = df['vel_z'] * factor

    return df


def calc_diffs(scenario):
    print(f"Calculating differences for {os.getcwd().split('/')[-1]}")
    df_vtk = get_df_from_cfd_vtk(scenario)
    df_postfilter = get_df_from_filter_csv(filename="0_postfilter.csv")

    diff1 = np.square( df_vtk['vel_x_mamico'].to_numpy() - df_postfilter['vel_x'].to_numpy()).mean()

    with open("res_postfilter.diff", "w") as f:
        f.write(str(diff1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', type=int, help='Scenario number')
    args = parser.parse_args()
    calc_diffs(args.scenario)
