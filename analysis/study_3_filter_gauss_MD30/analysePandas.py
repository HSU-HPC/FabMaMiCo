import os
from typing import *

import numpy as np
import pandas as pd
from vtk import *

script_path = os.path.dirname(os.path.abspath(__file__))


def get_df_from_filter_csv(folder, filename):
    print(f"Processing '{filename}'")

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
    # Filter iterations >= 100
    df = df[df["iteration"] >= 100]
    # Filter by every 10th iteration
    df = df[df["iteration"] % 10 == 0]

    ########################################
    # Extract scenario values
    iterations = len(df["iteration"].unique())
    cells_per_iteration = len(df[df["iteration"] == 100].index)
    cells_in_each_dim = round(cells_per_iteration ** (1. / 3))
        # print(f"Iterations: {iterations}")
        # print(f"Cells per iteration: {cells_per_iteration}")
        # print(f"Cells in each dimension: {cells_in_each_dim}")

    ########################################
    # Add the indices
    # indices for each iteration
    ix = np.tile(np.arange(0, cells_in_each_dim), cells_in_each_dim ** 2)
    iy = np.tile(np.repeat(np.arange(0, cells_in_each_dim), cells_in_each_dim), cells_in_each_dim)
    iz = np.repeat(np.arange(0, cells_in_each_dim), cells_in_each_dim ** 2)
    # populate dataframe with indices for each iteration
    df["idx_x"] = np.tile(ix, iterations)
    df["idx_y"] = np.tile(iy, iterations)
    df["idx_z"] = np.tile(iz, iterations)

    # df = df.sort_values(["iteration", "idx_z", "idx_y", "idx_x"], ascending=[True, True, True, True])

    return df


def get_df_from_cfd_vtk(folder, shape):
    ########################################
    # Create an empty numpy array
    
    numpy_array = np.zeros(shape)

    row = 0

    ########################################
    # Iterate over vtk files and extract the data
    vtk_files = [f for f in os.listdir(folder) if f.endswith(".vtk")]
    vtk_files.sort()
    # extract number from 'LBCouette_r0_c1000.vtk'
    iteration = lambda f: int(f.split("_")[2][1:-4])
    vtk_files = [(iteration(f), f) for f in vtk_files if iteration(f) >= 100]

    for i, f in sorted(vtk_files):
        index = i // 10 - 10
        print(f"Processing '{f}' with index {index}")

        reader : vtkStructuredGridReader = vtkStructuredGridReader()
        reader.SetFileName(os.path.join(folder, f))
        reader.ReadAllScalarsOn()
        reader.Update()

        # Get the structured grid
        grid : vtkStructuredGrid = reader.GetOutput()

        # Get the dimensions of the grid
        dims = [-1, -1, -1]
        grid.GetDimensions(dims)
        nx, ny, nz = [int(d - 1) for d in dims]
            # print(f"Dimensions: {nx} x {ny} x {nz} cells")

        # Get the number of cells
        n_cells = grid.GetNumberOfCells()
            # print(f"Number of cells: {n_cells}")

        if scenario == 30:
            md_cells = [6, 6, 6]
            md_offsets = [10, 10, 2.5]
            md_cell_offsets = [8, 8, 5]
        elif scenario == 60:
            md_cells = [12, 12, 12]
            md_offsets = [20, 20, 5]
            md_cell_offsets = [12, 12, 6]
        else:
            raise ValueError("Scenario not implemented - must be 30 or 60")

        # Get the density and velocity arrays
        densities  : vtkDataArray = grid.GetCellData().GetScalars("density")
        velocities : vtkDataArray = grid.GetCellData().GetVectors("velocity")

        min_x, max_x = md_cell_offsets[0], md_cell_offsets[0] + md_cells[0] - 1
        min_y, max_y = md_cell_offsets[1], md_cell_offsets[1] + md_cells[1] - 1
        min_z, max_z = md_cell_offsets[2], md_cell_offsets[2] + md_cells[2] - 1

            # print("MD domain:")
            # print(f"  X: {min_x} - {max_x}") 8-13
            # print(f"  Y: {min_y} - {max_y}") 8-13
            # print(f"  Z: {min_z} - {max_z}") 5-10

        # Iterate over inner MD cells (6x6x6 or 12x12x12)
        for cell in range(n_cells):
            pos = ((np.array(grid.GetCell(cell).GetBounds()) + 2.5) / 2.5).astype(int)[::2]
            if min_x <= pos[0] <= max_x and min_y <= pos[1] <= max_y and min_z <= pos[2] <= max_z:
                # print(f"Cell {cell}: {n} - {list(densities.GetTuple(cell)) + list(velocities.GetTuple(cell))}")
                numpy_array[row] = [i] + list(densities.GetTuple(cell)) + list(velocities.GetTuple(cell)) + [pos[0] - min_x, pos[1] - min_y, pos[2] - min_z]
                row += 1
        # row should be 216 (6x6x6) or 1728 (12x12x12)

    df = pd.DataFrame(
        numpy_array,
        columns=["iteration", "density", "mom_x", "mom_y", "mom_z", "idx_x", "idx_y", "idx_z"],
    )
    df = df.astype({"iteration": np.int32, "density": float, "mom_x": float, "mom_y": float, "mom_z": float, "idx_x": np.int32, "idx_y": np.int32, "idx_z": np.int32})
    # df = df.sort_values(["iteration", "idx_z", "idx_y", "idx_x"], ascending=[True, True, True, True])

    return df


if __name__ == "__main__":
    # SETUP
    scenario = 30
    wall_velocity = 0.2

    RUN = f"gauss_MD{scenario}_wv{str(wall_velocity).replace('.', '')}"

    print("+---------------------------------------")
    print(f"| Processing RUN '{RUN}'")
    print("+---------------------------------------")

    folder = os.path.join(script_path, "RUNS", RUN)

    md_raw = get_df_from_filter_csv(folder, "0_raw-md.csv")
    md_2d  = get_df_from_filter_csv(folder, "0_my-gauss-2d.csv")
    md_3d  = get_df_from_filter_csv(folder, "0_my-gauss-3d.csv")
    print(md_raw.shape) # (91*216, 8)
    print(md_2d.shape)  # (91*216, 8)
    print(md_3d.shape)  # (91*216, 8)

    md_raw.set_index(['iteration', 'idx_x', 'idx_y', 'idx_z'], inplace=True)
    md_raw = md_raw.reorder_levels(order=['iteration', 'idx_x', 'idx_y', 'idx_z'])
    print(md_raw)
    print(md_raw.loc[(100, 1, 0, 0)])

    # for i in range(100, 1000, 10):
    #     print(md_raw.loc[i])

    cfd = get_df_from_cfd_vtk(folder, shape=(19656,8))
    cfd.set_index(['iteration', 'idx_x', 'idx_y', 'idx_z'], inplace=True)
    cfd = cfd.reorder_levels(order=['iteration', 'idx_x', 'idx_y', 'idx_z'])
    print(cfd)

    # diff = md_raw - cfd
    # print(diff)

    sys.exit(0)
