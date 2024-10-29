import argparse
import os

import numpy as np

from matplotlib import pyplot as plt
from typing import *
from vtk import *

from plugins.FabMaMiCo.scripts.postprocess.readers import get_df_from_filter_csv, get_df_from_cfd_vtk


def plot_over_time(
        scenario: int,
        oscillations: List[int],
        wall_velocities: List[float],
        results_dir_gauss: str,
        results_dir_multimd: str,
        output_dir: str
    ):

    for osc in oscillations:
        for wv in wall_velocities:
            RUN_F = f"gauss_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_F  = os.path.join( results_dir_gauss, "RUNS", RUN_F)
            RUN_MI = f"MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_MI = os.path.join( results_dir_multimd, "RUNS", RUN_MI )

            print("+-----------------------------------------------")
            print(f"| Processing RUN '{RUN_F}'")
            print("+-----------------------------------------------")

            md_raw      = get_df_from_filter_csv(FOLDER_F,  "0_raw-md.csv"  )
            my_gauss_2d = get_df_from_filter_csv(FOLDER_F,  "0_gauss-2d.csv")
            my_gauss_3d = get_df_from_filter_csv(FOLDER_F,  "0_gauss-3d.csv")
            md_mimd     = get_df_from_filter_csv(FOLDER_MI, "0_nofilter.csv")

            cfd_f  = get_df_from_cfd_vtk(FOLDER_F,  length=md_raw.shape[0], scenario=scenario)

            vtk_f  = cfd_f.groupby( ['iteration', 'idx_z'])['vel_x_mamico'].mean().reset_index()

            csv_raw = md_raw.groupby(      ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()
            csv_2d  = my_gauss_2d.groupby( ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()
            csv_3d  = my_gauss_3d.groupby( ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()
            csv_mi  = md_mimd.groupby(     ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()

            fig, axs = plt.subplots(5, 1, figsize=(12, 15))
            iterations = np.arange(100, 1001, 10)

            max_abs_val = 0.0

            titles = ["Lattice-Boltzmann CFD", "Pre-Gauss-Filter MD", "Gauss-2D-Filter MD", "Gauss-3D-Filter MD", "Multi-Instance MD"]
            columns = ["vel_x_mamico", "vel_x", "vel_x", "vel_x", "vel_x"]
            for k, d_f in enumerate([vtk_f, csv_raw, csv_2d, csv_3d, csv_mi]):
                for i in range(6): # for each z-slice
                    z_vals = d_f[d_f['idx_z'] == i][columns[k]].to_numpy()
                    axs[k].plot(iterations, z_vals, label=f"z_idx = {i}", color=f"C{i}")
                    max_abs_val = max(max_abs_val, np.abs(z_vals).max())

                axs[k].set_xlabel("Iteration")
                axs[k].set_ylabel("Velocity")
                title = titles[k]
                axs[k].set_title(title)
                axs[k].legend(loc='upper right')
            for ax in axs:
                ax.set_ylim(-max_abs_val, max_abs_val)
            fig.suptitle(f"Velocity in x-direction for averaged z-slices\nMD{scenario} | wall-velocity={wv}", fontsize=16)
            fig.tight_layout(rect=[0, 0, 1, 0.97])
            fig.savefig(os.path.join(output_dir, f"velocity_x_mean_MD{scenario}_{osc}osc_wv{str(wv).replace('.','')}.pdf"), format="pdf")
            plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', type=int, help='Scenario number')
    parser.add_argument('--results_dir_gauss', type=str, help='Folder containing the results from the ensemble run with Gaussian filtering')
    parser.add_argument('--results_dir_multimd', type=str, help='Folder containing the results from Multi-MD simulation')
    parser.add_argument('--output_dir', type=str, help='Folder to save the plot')
    args = parser.parse_args()
    plot_over_time(
        scenario=args.scenario,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0],
        results_dir_gauss=args.results_dir_gauss,
        results_dir_multimd=args.results_dir_multimd,
        output_dir=args.output_dir
    )
