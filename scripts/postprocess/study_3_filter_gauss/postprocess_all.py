import argparse
import os

import numpy as np

from matplotlib import pyplot as plt
from typing import *
from vtk import *

from plugins.FabMaMiCo.scripts.postprocess.readers import get_df_from_filter_csv, get_df_from_cfd_vtk


def generate_plots(
        scenario: int,
        oscillations: List[int],
        wall_velocities: List[float],
        results_dir_gauss: str,
        results_dir_multimd: str,
        output_dir: str,
        from_npy: bool = True
    ):

    # initialize results array
    res = np.zeros((2, len(wall_velocities), 4))
    # create figure
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))
    # iterate over oscillations and wall velocities
    if not from_npy:
        for i, osc in enumerate(oscillations):
            for k, wv in enumerate(wall_velocities):
                RUN_F = f"gauss_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
                FOLDER_F  = os.path.join( results_dir_gauss, "RUNS", RUN_F)
                RUN_MI = f"MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
                FOLDER_MI = os.path.join( results_dir_multimd, "RUNS", RUN_MI )

                print("+---------------------------------------")
                print(f"| Processing RUN '{RUN_F}'")
                print("+---------------------------------------")

                # Load data from files
                md_raw      = get_df_from_filter_csv(FOLDER_F,  "0_raw-md.csv"  )
                my_gauss_2d = get_df_from_filter_csv(FOLDER_F,  "0_gauss-2d.csv")
                my_gauss_3d = get_df_from_filter_csv(FOLDER_F,  "0_gauss-3d.csv")
                md_mimd     = get_df_from_filter_csv(FOLDER_MI, "0_nofilter.csv")

                cfd = get_df_from_cfd_vtk(FOLDER_F, length=md_raw.shape[0], scenario=scenario)

                # Calculate mean squared differences
                diff1 = np.square( cfd['vel_x_mamico'].to_numpy() -      md_raw['vel_x'].to_numpy()).mean()
                diff2 = np.square( cfd['vel_x_mamico'].to_numpy() - my_gauss_2d['vel_x'].to_numpy()).mean()
                diff3 = np.square( cfd['vel_x_mamico'].to_numpy() - my_gauss_3d['vel_x'].to_numpy()).mean()
                diff4 = np.square( cfd['vel_x_mamico'].to_numpy() -     md_mimd['vel_x'].to_numpy()).mean()

                # Store results in array
                res[i, k]  = [diff1, diff2, diff3, diff4]

                print(f"Mean difference between CFD and Raw: {diff1}")
                print(f"Mean difference between CFD and Gauss-2D: {diff2}")
                print(f"Mean difference between CFD and Gauss-3D: {diff3}")
                print(f"Mean difference between CFD and Multi-Instance MD: {diff4}")

        # Store results in file
        np.save(os.path.join(output_dir, f"study_3_filter_gauss_MSE_MD{scenario}_all.npy"), res)
    else:
        res = np.load(os.path.join(output_dir, f"study_3_filter_gauss_MSE_MD{scenario}_all.npy"))

    # Plot results
    for i, osc in enumerate(oscillations):
        axs[i].plot(wall_velocities, res[i, :, 0], label="Single-Instance: Unfiltered MD", marker='o')
        axs[i].plot(wall_velocities, res[i, :, 1], label="Single-Instance: Gauss filtered 2D", marker='o')
        axs[i].plot(wall_velocities, res[i, :, 2], label="Single-Instance: Gauss filtered 3D", marker='o')
        axs[i].plot(wall_velocities, res[i, :, 3], label="Multi-Instance (200): Unfiltered MD", marker='o')
        axs[i].set_xlabel("Wall velocity")
        axs[i].set_ylabel("Mean Squared Difference")
        axs[i].set_title(f"{osc} oscillations")
        axs[i].legend(loc='center')
        axs[i].set_xticks(wall_velocities)
        axs[i].grid(True)
    marge = np.max(res) - np.min(res)
    axs[0].set_ylim([np.min(res) - 0.1*marge, np.max(res) + 0.1*marge])
    axs[1].set_ylim([np.min(res) - 0.1*marge, np.max(res) + 0.1*marge])
    fig.suptitle(f"MSE between CFD and MD\n"\
                 f"MD{scenario} | cellwise in x-direction, averaged over 1000 iterations",
                 fontsize=16
                )
    fig.tight_layout()
    output_file = os.path.join(output_dir, f"study_3_filter_gauss_MSE_MD{scenario}_all.pdf")
    fig.savefig(output_file, format="pdf")
    plt.close(fig)
    print(f"Saved figure to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', type=int, help='Scenario number')
    parser.add_argument('--results_dir_gauss', type=str, help='Folder containing the results from the ensemble run with Gaussian filtering')
    parser.add_argument('--results_dir_multimd', type=str, help='Folder containing the results from Multi-MD simulation')
    parser.add_argument('--output_dir', type=str, help='Folder to save the plot')
    args = parser.parse_args()
    generate_plots(
        scenario=args.scenario,
        oscillations=[2, 5],
        wall_velocities=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8],
        results_dir_gauss=args.results_dir_gauss,
        results_dir_multimd=args.results_dir_multimd,
        output_dir=args.output_dir
    )