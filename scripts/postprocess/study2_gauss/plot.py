import os

import numpy as np

from matplotlib import pyplot as plt
from typing import *
from vtk import *

rc_fonts = {
    "font.size": 11,
    "axes.prop_cycle": "(cycler('color', ['k', 'r', 'b', 'g']) + cycler('ls', ['-', '--', ':', '-.']))",
    # Set x axis
    "xtick.direction": "in",
    "xtick.major.size": 3,
    "xtick.major.width": 0.5,
    "xtick.minor.size": 1.5,
    "xtick.minor.width": 0.5,
    "xtick.minor.visible": False,
    "xtick.top": False,
    # Set y axis
    "ytick.direction": "in",
    "ytick.major.size": 3,
    "ytick.major.width": 0.5,
    "ytick.minor.size": 1.5,
    "ytick.minor.width": 0.5,
    "ytick.minor.visible": True,
    "ytick.right": True,
    # Set line widths
    "axes.linewidth": 0.5,
    "grid.linewidth": 0.5,
    "lines.linewidth": 1.0,
    # Remove legend frame
    # legend.frameon : False"
}

plt.rcParams.update(rc_fonts)

def create_plot(
    scenario: int,
    oscillations: List[int],
    wall_velocities: List[float],
    results_dir_gauss: str,
    results_dir_multimd: str,
    output_dir: str,
    show_plots: bool = False
):
    os.makedirs(output_dir, exist_ok=True)

    # initialize results array
    res = np.zeros(shape=(len(oscillations), len(wall_velocities), 4))

    # iterate over oscillations and wall velocities
    for i, osc in enumerate(oscillations):
        for k, wv in enumerate(wall_velocities):

            RUN_F = f"gauss_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_F  = os.path.join( results_dir_gauss, "RUNS", RUN_F)

            RUN_MI = f"multimd_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_MI = os.path.join( results_dir_multimd, "RUNS", RUN_MI )

            diff1 = float(open(os.path.join(FOLDER_F, "res_raw.diff"), "r").read())
            diff2 = float(open(os.path.join(FOLDER_F, "res_gauss_2d.diff"), "r").read())
            diff3 = float(open(os.path.join(FOLDER_F, "res_gauss_3d.diff"), "r").read())
            diff4 = float(open(os.path.join(FOLDER_MI, "res_multimd.diff"), "r").read())

            # Store results in array
            res[i, k]  = [diff1, diff2, diff3, diff4]

    # Plot results
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    for i, osc in enumerate(oscillations):
        axs[i].plot(wall_velocities, res[i, :, 0], label="single instance: unfiltered MD", marker='o')
        axs[i].plot(wall_velocities, res[i, :, 1], label="single instance: 2D Gauss filtered MD", marker='o')
        axs[i].plot(wall_velocities, res[i, :, 2], label="single instance: 3D Gauss filtered MD", marker='o')
        axs[i].plot(wall_velocities, res[i, :, 3], label="multi-instance (200): unfiltered MD", marker='s')
        axs[i].set_xlabel("wall velocity")
        axs[i].set_ylabel("mean squared error (MSE)")
        axs[i].set_title(f"{osc} oscillations")
        axs[i].legend(bbox_to_anchor=(0.5, 0.6), loc='center')
        axs[i].set_xticks(wall_velocities)
    marge = np.max(res) - np.min(res)
    # axs[0].set_ylim([np.min(res) - 0.1*marge, np.max(res) + 0.1*marge])
    # axs[1].set_ylim([np.min(res) - 0.1*marge, np.max(res) + 0.1*marge])
    fig.suptitle(f"MSE between CFD and (Gauss filtered) MD\n"\
                 f"MD{scenario}",
                 fontsize=16
                )
    fig.tight_layout()
    output_file = os.path.join(output_dir, f"study2_gauss_MSE_MD{scenario}.pdf")
    if show_plots:
        plt.show()
    fig.savefig(output_file, format="pdf")
    plt.close(fig)
    print(f"Saved plot to {output_file}")

    # add to caption: cellwise in x-direction, averaged over 1000 iterations [100:1000:10]
