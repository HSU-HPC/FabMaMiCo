import argparse
import os

import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LogNorm
from typing import *
from vtk import *

# plt.style.use('tableau-colorblind10')

rc_fonts = {
    "font.size": 11,
    "axes.prop_cycle": "(cycler('color', ['k', 'r', 'b', 'g']) + cycler('ls', ['-', '--', ':', '-.']))",
    # Set x axis
    # "xtick.direction": "in",
    # "xtick.major.size": 3,
    # "xtick.major.width": 0.5,
    # "xtick.minor.size": 1.5,
    # "xtick.minor.width": 0.5,
    # "xtick.minor.visible": False,
    # "xtick.top": False,
    # Set y axis
    # "ytick.direction": "in",
    # "ytick.major.size": 3,
    # "ytick.major.width": 0.5,
    # "ytick.minor.size": 1.5,
    # "ytick.minor.width": 0.5,
    # "ytick.minor.visible": True,
    # "ytick.right": True,
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
    hsq_rel: List[float],
    sigsq_rel: List[float],
    tws: int,
    results_dir_nlm_sq: str,
    output_dir: str,
    show_plots: bool = False
):
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over oscillations
    for i, osc in enumerate(oscillations):

        # initialize results array
        res = np.zeros(shape=(len(wall_velocities) * len(sigsq_rel) * len(hsq_rel), 4))

        for k, wv in enumerate(wall_velocities):

            RUN_F = f"nlm_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}"
            FOLDER_F  = os.path.join( results_dir_nlm_sq, "RUNS", RUN_F)

            for i, sigsq in enumerate(sigsq_rel):
                for j, hsq in enumerate(hsq_rel):
                    # Get data for NLM Filtered
                    RUN_F     = f"nlm_MD{scenario}_{osc}osc_wv{str(wv).replace('.', '')}_sigsqrel{sigsq:.4f}_hsqrel{hsq:.4f}_tws0{tws}".replace(".", "")
                    FOLDER_F  = os.path.join( results_dir_nlm_sq, "RUNS", RUN_F)

                    diff = float(open(os.path.join(FOLDER_F, "res_postfilter.diff"), "r").read())
                    res[k*len(sigsq_rel)*len(hsq_rel) + i*len(hsq_rel) + j] = [wv, sigsq, hsq, diff]

        ## Plot the results
        fig = plt.figure(figsize=(24, 16))

        # create a dataframe from the results array
        df = pd.DataFrame(res, columns=['wv', 'sigsq_rel', 'hsq_rel', 'MSE'])

        for k, wv in enumerate(wall_velocities):
            # create a subplot for each wall velocity
            ax1 = fig.add_subplot(3, 3, k+1)
            # extract the data for the current wall velocity from the dataframe
            wv_df = df[df['wv'] == wv]
            # create a pivot table for the heatmap
            df_pivot = wv_df.pivot(index='sigsq_rel', columns='hsq_rel', values='MSE')
            factor = 1
            while df_pivot.max().max() < 1:
                df_pivot *= 10
                factor += 1
            # print(f"\nWall velocity: {wv}:")
            # print(df_pivot)
            # customize the heatmap colormap
            vmin, vmax = df_pivot.min().min(), df_pivot.max().max()
            center = 0.008 * (vmax - vmin) + vmin
            norm = LogNorm(vmin=vmin, vmax=vmax)
            norm = TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)
            # norm = TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)
            # create the heatmap
            # ticks_a = np.linspace(vmin, center, 5)
            # ticks_b = np.linspace(center, vmax, 5)
            # ticks = np.concatenate((ticks_a, ticks_b[1:])).round(1).tolist()
            # print(ticks)
            a = sns.heatmap(data = df_pivot, annot=True, cmap="cividis", norm=norm) # cbar_kws=dict(ticks=ticks))
            # invert y axis to increase values from bottom to top
            a.invert_yaxis()
            # get the sigsq_rel and hsq_rel values for the minimum MSE
            ## min_mse_index = wv_df['MSE'].idxmin()
            ## min_mse_value_sigsq_rel = wv_df.loc[min_mse_index, 'sigsq_rel']
            ## min_mse_value_hsq_rel   = wv_df.loc[min_mse_index, 'hsq_rel']
            # get the corresponding index for the minimum MSE
            ## al = sigsq_rel.index(min_mse_value_sigsq_rel)
            ## bl = hsq_rel.index(min_mse_value_hsq_rel)
            # add a rectangle to the heatmap for the minimum MSE
            ## rect = ax1.add_patch(plt.Rectangle((bl, al), 1, 1, fc='none', ec='red', lw=4, clip_on=False))
            # add labels and title to the plot
            ## handles = [rect]
            ## labels = ['minimum MSE']
            ## ax1.legend(handles, labels, bbox_to_anchor=(1, 1.08), loc='upper right', borderaxespad=0.0)
            ax1.set_title(f"wall velocity={wv}   (MSE values in " + r"$10^{-" + str(factor) + r"}$)")
            # ax1.set_xlabel(r"hsq\textsubscript{rel}")
            # ax1.set_ylabel(r"sigsq\textsubscript{rel}")

        # add a title to the figure
        fig.suptitle(f"Mean Squared Error between CFD and NLM filtered MD\n"\
                     f"MD{scenario} | oscillations={osc}\n"\
                      "sigsq=10 | hsq=20\n"\
                     f"time-window-size={tws}", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        # save the figure to a pdf file
        output_file = os.path.join(output_dir, f"study2_nlm_MSE_MD{scenario}_{osc}osc.pdf")
        fig.savefig(output_file, format="pdf")
        print(f"Saved plot to {output_file}")
        if show_plots:
            plt.show(block=True)
