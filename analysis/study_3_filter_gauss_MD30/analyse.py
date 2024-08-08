import os
from typing import *

import numpy as np
import pandas as pd
from vtk import *

script_path = os.path.dirname(os.path.abspath(__file__))


def get_np_from_filter_csv(folder, filename, output_filename=None):
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

    ########################################
    # Create 5D numpy array: [iteration, x, y, z]: [mass, mom_x, mom_y, mom_z]
    numpy_array = np.zeros((iterations, cells_in_each_dim, cells_in_each_dim, cells_in_each_dim, 4))
    for row in df.itertuples():
        numpy_array[row.iteration // 10 - 10, row.idx_x, row.idx_y, row.idx_z, :] = [row.mass, row.mom_x, row.mom_y, row.mom_z]

    ########################################
    # Write to file
    if output_filename is not None:
        df.to_csv(os.path.join(folder, output_filename), sep=";", index=False)

    return numpy_array

def get_np_from_cfd_vtk(folder, shape):
    ########################################
    # Create an empty numpy array
    numpy_array = np.zeros(shape)

    ########################################
    # Iterate over vtk files and extract the data
    vtk_files = [f for f in os.listdir(folder) if f.endswith(".vtk")]
    vtk_files.sort()
    # extract number from 'LBCouette_r0_c1000.vtk'
    iteration = lambda f: int(f.split("_")[2][1:-4])
    vtk_files = [(iteration(f), f) for f in vtk_files if iteration(f) >= 100]

    for i, f in sorted(vtk_files):
        it = iteration(f)
        index = it // 10 - 10
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
            raise ValueError("Scenario not implemented")

        # Get the cell data
        cell_data  : vtkCellData = grid.GetCellData()

        # Get the density and velocity arrays
        densities  : vtkDataArray = grid.GetCellData().GetScalars("density")
        velocities : vtkDataArray = grid.GetCellData().GetVectors("velocity")

        min_x, max_x = md_cell_offsets[0], md_cell_offsets[0] + md_cells[0] - 1
        min_y, max_y = md_cell_offsets[1], md_cell_offsets[1] + md_cells[1] - 1
        min_z, max_z = md_cell_offsets[2], md_cell_offsets[2] + md_cells[2] - 1

            # print("MD domain:")
            # print(f"  X: {min_x} - {max_x}")
            # print(f"  Y: {min_y} - {max_y}")
            # print(f"  Z: {min_z} - {max_z}")

        arr = np.zeros((md_cells[0], md_cells[1], md_cells[2], 4))

        md = 0
        for cell in range(n_cells):
            n = ((np.array(grid.GetCell(cell).GetBounds()) + 2.5) / 2.5).astype(int)[::2]
            if min_x <= n[0] <= max_x and min_y <= n[1] <= max_y and min_z <= n[2] <= max_z:
                # print(f"Cell {cell}: {n} - {list(densities.GetTuple(cell)) + list(velocities.GetTuple(cell))}")
                arr[n[0] - min_x, n[1] - min_y, n[2] - min_z] = list(densities.GetTuple(cell)) + list(velocities.GetTuple(cell))
                md += 1
        # print("MD Cells written to numpy-array:", md)

        numpy_array[index] = arr

    return numpy_array

if __name__ == "__main__":

    # scenarios = [30, 60]
    # wall_velocities = [0.2, 0.4, 0.6, 0.8, 1.0]

    # for scenario in scenarios:
    #     for wall_velocity in wall_velocities:
    #         RUN = f"gauss_MD{scenario}_wv{str(wall_velocity).replace('.', '')}"
    #         folder = os.path.join(script_path, "RUNS", RUN)

    #         md_raw = get_np_from_filter_csv(os.path.join(folder, "0_raw-md.csv"))
    #         md_2d  = get_np_from_filter_csv(os.path.join(folder, "0_my-gauss-2d.csv"))
    #         md_3d  = get_np_from_filter_csv(os.path.join(folder, "0_my-gauss-3d.csv"))

    # SETUP
    scenario = 30
    wall_velocity = 0.2

    RUN = f"gauss_MD{scenario}_wv{str(wall_velocity).replace('.', '')}"

    print("+---------------------------------------")
    print(f"| Processing RUN '{RUN}'")
    print("+---------------------------------------")

    folder = os.path.join(script_path, "RUNS", RUN)

    md_raw = get_np_from_filter_csv(folder, "0_raw-md.csv")
    md_2d  = get_np_from_filter_csv(folder, "0_my-gauss-2d.csv")
    md_3d  = get_np_from_filter_csv(folder, "0_my-gauss-3d.csv")
    cfd    = get_np_from_cfd_vtk(folder, shape=md_raw.shape)

    print(md_raw.shape)
    print(md_2d.shape)
    print(md_3d.shape)
    print(cfd.shape)

    err_raw_cdf = np.abs(md_raw - cfd)
    print(f"Error raw-cfd: {np.max(err_raw_cdf)}")

    err_2d_cdf = np.abs(md_2d - cfd)
    print(f"Error 2d-cfd: {np.max(err_2d_cdf)}")

    err_3d_cdf = np.abs(md_3d - cfd)
    print(f"Error 3d-cfd: {np.max(err_3d_cdf)}")

    sys.exit(0)
