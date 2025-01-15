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
    time_window_sizes: List[int],
    k_maxs: List[int],
    results_dir_pod: str,
    results_dir_multimd: str,
    output_dir: str,
    show_plots: bool = False
):
    os.makedirs(output_dir, exist_ok=True)

    # initialize results array
    res = np.zeros(shape=(len(oscillations), len(wall_velocities), len(time_window_sizes)+2, len(k_maxs)))

    # iterate over oscillations and wall velocities
    for i, osc in enumerate(oscillations):
        for k, wv in enumerate(wall_velocities):

            RUN_MI = f"multimd_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_MI = os.path.join( results_dir_multimd, "RUNS", RUN_MI )

            diff3 = float(open(os.path.join(FOLDER_MI, "res_multimd.diff"), "r").read())

            res[i, k, 1, 0] = diff3

            for l, tws in enumerate(time_window_sizes):
                for m, km in enumerate(k_maxs):
                    RUN_F = f"pod_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}_tws{tws}_kmax{km}"
                    FOLDER_F  = os.path.join( results_dir_pod, "RUNS", RUN_F)

                    diff1 = float(open(os.path.join(FOLDER_F, "res_raw.diff"), "r").read())
                    diff2 = float(open(os.path.join(FOLDER_F, "res_pod.diff"), "r").read())

                    res[i, k, l+2, m] = diff2
                    if m != 0:
                        assert diff1 == res[i, k, 0, 0]
                    else:
                        res[i, k, 0, 0] = diff1


    for i, osc in enumerate(oscillations):
        fig = plt.figure(figsize=(13, 14))

        markers = ['o', 's', 'x']

        for k, wv in enumerate(wall_velocities):
            ax1 = fig.add_subplot(3, 3, k+1)
            ax1.set_xlabel("time window size")
            ax1.set_ylabel("mean squared error (MSE)")
            ax1.set_title(f"wall velocity={wv}")
            ax1.plot([-10], [res[i, k, 0, 0]], label="no filter applied", color="C3", marker=markers[0])
            ax1.plot(  [0], [res[i, k, 1, 0]], label="multi-instance MD", color="C4", marker=markers[1])
            for l, km in enumerate(k_maxs):
                ax1.plot(time_window_sizes, res[i, k, 2:, l], label=f"POD, kmax={km}", color=f"C{l}", marker=markers[2])
            ax1.legend()
            ax1.set_xticks(time_window_sizes)
            ax1.grid(True)

            xticks = ax1.get_xticks()
            xticks = np.insert(xticks, 0, -10)
            xticks = np.insert(xticks, 0, 0)
            xticklabels = list(map(str, ax1.get_xticks()))
            xticklabels.insert(0, '/')
            xticklabels.insert(0, '/')
            _ = ax1.set_xticks(xticks, xticklabels)
            # ax1.tick_params(axis='x', labelrotation=45)

            ax1.set_ylim([0, np.max(res) * 1.02])

        fig.suptitle(f"MSE between CFD and (POD filtered) MD\nMD{scenario} | {osc} oscillations", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        output_file = os.path.join(output_dir, f"study2_pod_MSE_MD{scenario}_{osc}osc_all.pdf")
        fig.savefig(output_file, format="pdf")
        print(f"Saved plot to {output_file}")
        if show_plots:
            plt.show(block=True)

    # add to caption: cellwise in x-direction, averaged over 1000 iterations [100:1000:10]
