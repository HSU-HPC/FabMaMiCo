import glob
import os

import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm, TwoSlopeNorm
from typing import *
from vtk import *

from plugins.FabMaMiCo.analysis.readers import get_df_from_filter_csv

plt.style.use('tableau-colorblind10')

script_path = os.path.dirname(os.path.abspath(__file__))

RESULTS_FOLDER = r"/media/jo/Jojos SSD/FabMaMiCo_results"
LOAD_DATA_FROM_CSV_FILES = False
SHOW_PLOTS = False

if __name__ == "__main__":
    scenarios = [30]
    oscillations = [2, 5]

    wall_velocities = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]

    sigsq_rel = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    hsq_rel = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    tws = 5 # time-window-size of nlm filter
    
    for sc in scenarios:
        for osc in oscillations:
            ###################
            ## Read the data ##
            ###################

            # create a results array to store the mean squared errors with wv, sigsq_rel, hsq_rel and MSE
            res = np.zeros((len(wall_velocities) * len(sigsq_rel) * len(hsq_rel), 4))

            if LOAD_DATA_FROM_CSV_FILES:
                # load the data from the csv files
                for k, wv in enumerate(wall_velocities):                    
                    # Get data for MultiMD
                    CONFIG_MMD = f"fabmamico_study_3_filter_multimd_MD{sc}_hsuper_1600"
                    RUN_MMD    = f"MD{sc}_{osc}osc_wv{str(wv).replace('.', '')}"
                    FOLDER_MMD = os.path.join( RESULTS_FOLDER, CONFIG_MMD, "RUNS", RUN_MMD )
                    multimd_raw = get_df_from_filter_csv(FOLDER_MMD, "0_nofilter.csv")

                    for i, sigsq in enumerate(sigsq_rel):
                        for j, hsq in enumerate(hsq_rel):
                            # Get data for NLM Filtered
                            CONFIG_F  = f"fabmamico_study_3_filter_nlm_sq_MD{sc}_hsuper_1"
                            RUN_F     = f"nlm_MD{sc}_{osc}osc_wv{str(wv).replace('.', '')}_sigsqrel{sigsq:.4f}_hsqrel{hsq:.4f}_tws0{tws}".replace(".", "")
                            FOLDER_F  = os.path.join( RESULTS_FOLDER, CONFIG_F, "RUNS", RUN_F)
                            folder = os.path.join(script_path, "RUNS", FOLDER_F)
                            print("+--------------------------------------------------------------------------")
                            print(f"| Processing RUN '{RUN_F}'")
                            print("+--------------------------------------------------------------------------")
                            # Read NLM Filtered: postfilter.csv
                            nlm_f = get_df_from_filter_csv(folder, "0_postfilter.csv")
                            # calculate the mean squared error and store it in the results array
                            diff = np.square(multimd_raw['mom_x'].to_numpy() - nlm_f['mom_x'].to_numpy()).mean()
                            res[k*len(sigsq_rel)*len(hsq_rel) + i*len(hsq_rel) + j] = [wv, sigsq, hsq, diff]

                # save the data to a MSE numpy file
                np.save(script_path + f"/data/results_MD{sc}_{osc}osc.npy", res)
            else:
                # load the data from the MSE numpy file
                res = np.load(script_path + f"/data/results_MD{sc}_{osc}osc.npy")

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
                print(f"\nWall velocity: {wv}:")
                print(df_pivot)
                # customize the heatmap colormap
                vmin, vmax = df_pivot.min().min(), df_pivot.max().max()
                center = 0.01 * (vmax - vmin) + vmin
                norm = TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)
                # create the heatmap
                a = sns.heatmap(data = df_pivot, annot=True, cmap="cividis", norm=norm)
                # invert y axis to increase values from bottom to top
                a.invert_yaxis()
                # get the sigsq_rel and hsq_rel values for the minimum MSE
                min_mse_index = wv_df['MSE'].idxmin()
                min_mse_value_sigsq_rel = wv_df.loc[min_mse_index, 'sigsq_rel']
                min_mse_value_hsq_rel   = wv_df.loc[min_mse_index, 'hsq_rel']
                # get the corresponding index for the minimum MSE
                al = sigsq_rel.index(min_mse_value_sigsq_rel)
                bl = hsq_rel.index(min_mse_value_hsq_rel)
                # add a rectangle to the heatmap for the minimum MSE
                rect = ax1.add_patch(plt.Rectangle((bl, al), 1, 1, fc='none', ec='red', lw=4, clip_on=False))
                # add labels and title to the plot
                handles = [rect]
                labels = ['minimum MSE']
                legend = ax1.legend(handles, labels, bbox_to_anchor=(1, 1.08), loc='upper right', borderaxespad=0.0)
                ax1.set_title(f"wall-velocity={wv}")

            # add a title to the figure
            fig.suptitle(f"Mean Squared Error with NLM filtering\n"\
                         f"MD{sc} | oscillations={osc}\n"\
                          "sigsq=10 | hsq=20\n"\
                         f"time-window-size={tws}", fontsize=16)
            fig.tight_layout(rect=[0, 0, 1, 0.97])
            # save the figure to a pdf file
            fig.savefig(os.path.join(script_path, f"plots/results_nlm_sq_MD_{sc}_{osc}osc.pdf"), format="pdf")
            # optionally show the plot
            if SHOW_PLOTS:
                plt.show(block=True)
