import argparse
import os

import numpy as np

from matplotlib import pyplot as plt
from typing import *
from vtk import *

from readers import get_df_from_filter_csv

script_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('results_dir_multimd', type=str, help='Folder containing the results from Multi-MD simulation')
    parser.add_argument('results_dir_gauss', type=str, help='Folder containing the results from filtering with Gauss')
    args = parser.parse_args()

    # SETUP
    sc = 60 # scenario
    wall_velocities = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]
    oscillations = [2, 5]

    res = np.zeros((2, len(wall_velocities), 3))


    fig, axs = plt.subplots(1, 2, figsize=(16, 7))
    for kig, osc in enumerate(oscillations):
        for kik, wv in enumerate(wall_velocities):
            RUN_F = f"gauss_MD{sc}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_F  = os.path.join( args.results_dir_gauss, "RUNS", RUN_F)
            RUN_NF = f"MD{sc}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_NF = os.path.join( args.results_dir_multimd, "RUNS", RUN_NF )

            print("+---------------------------------------")
            print(f"| Processing RUN '{RUN_F}'")
            print("+---------------------------------------")

            md_raw      = get_df_from_filter_csv(FOLDER_F,  "0_raw-md.csv"  )
            my_gauss_2d = get_df_from_filter_csv(FOLDER_F,  "0_gauss-2d.csv")
            my_gauss_3d = get_df_from_filter_csv(FOLDER_F,  "0_gauss-3d.csv")
            md_mimd = get_df_from_filter_csv(FOLDER_NF, "0_nofilter.csv")

            titles = ["Multi-Instance MD", "Pre-Gauss-Filter MD", "Gauss-2D-Filter MD", "Gauss-3D-Filter MD"]
            columns = ["mom_x", "mom_x", "mom_x", "mom_x"]

            diff1 = np.square(md_mimd['mom_x'].to_numpy() -      md_raw['mom_x'].to_numpy()).mean()
            diff2 = np.square(md_mimd['mom_x'].to_numpy() - my_gauss_2d['mom_x'].to_numpy()).mean()
            diff3 = np.square(md_mimd['mom_x'].to_numpy() - my_gauss_3d['mom_x'].to_numpy()).mean()

            res[kig, kik] = [diff1, diff2, diff3]

            print(f"Mean difference between MIMD and Raw: {diff1}")
            print(f"Mean difference between MIMD and Gauss-2D: {diff2}")
            print(f"Mean difference between MIMD and Gauss-3D: {diff3}")

        axs[kig].plot(wall_velocities, res[kig, :, 0], label="Unfiltered MD", marker='o')
        axs[kig].plot(wall_velocities, res[kig, :, 1], label="Gauss filtered 2D", marker='o')
        axs[kig].plot(wall_velocities, res[kig, :, 2], label="Gauss filtered 3D", marker='o')
        axs[kig].set_xlabel("Wall velocity")
        axs[kig].set_ylabel("Mean Squared Difference")
        axs[kig].set_title(f"{osc} oscillations")
        axs[kig].legend(loc='center')
        axs[kig].set_xticks(wall_velocities)
        axs[kig].grid(True)
    marge = np.max(res) - np.min(res)
    axs[0].set_ylim([np.min(res) - 0.1*marge, np.max(res) + 0.1*marge])
    axs[1].set_ylim([np.min(res) - 0.1*marge, np.max(res) + 0.1*marge])
    fig.suptitle(f"Mean Squared Difference between Multi-Instance MD and Gauss filtered MD | MD{sc}", fontsize=16)
    fig.tight_layout()
    fig.savefig(os.path.join(script_path, f"mean_square_difference_MD{sc}.pdf"), format="pdf")
    print("Saved figure.")
    plt.close(fig)
