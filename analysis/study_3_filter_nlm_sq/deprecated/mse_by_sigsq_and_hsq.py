import glob
import os

import numpy as np
import pandas as pd

from matplotlib import cm
from matplotlib import pyplot as plt
from typing import *
from vtk import *

from plugins.FabMaMiCo.analysis.readers import get_df_from_filter_csv

plt.style.use('tableau-colorblind10')

script_path = os.path.dirname(os.path.abspath(__file__))

RESULTS_FOLDER = r"/media/jo/Jojos SSD/FabMaMiCo_results"
LOAD_DATA_FROM_CSV_FILES = True
SHOW_PLOTS = True

if __name__ == "__main__":
    scenarios = [30]
    oscillations = [2]

    wall_velocities = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]

    sigsq_rel = np.linspace(0.0, 1.0, 11)
    hsq_rel = np.linspace(0.0, 1.0, 11)
    tws = 5
    
    for sc in scenarios:
        for osc in oscillations:

            # wv, sigsq, hsq
            res = np.zeros((len(wall_velocities), len(sigsq_rel), len(hsq_rel)))

            if LOAD_DATA_FROM_CSV_FILES:
                for k, wv in enumerate(wall_velocities):
                    CONFIG_NF = f"fabmamico_study_3_filter_multimd_MD{sc}_hsuper_1600"
                    RUN_NF    = f"MD{sc}_{osc}osc_wv{str(round(wv,1)).replace('.', '')}"
                    FOLDER_NF = os.path.join( RESULTS_FOLDER, CONFIG_NF, "RUNS", RUN_NF )

                    # Read NoFilter: nofilter.csv
                    nofilter_raw = get_df_from_filter_csv(FOLDER_NF, "0_nofilter.csv")

                    for i, sigsq in enumerate(sigsq_rel):
                        for j, hsq in enumerate(hsq_rel):
                            CONFIG_F  = f"fabmamico_study_3_filter_nlm_sq_MD{sc}_hsuper_1"
                            RUN_F     = f"nlm_MD{sc}_{osc}osc_wv{str(round(wv,1)).replace('.', '')}_sigsqrel{sigsq:.4f}_hsqrel{hsq:.4f}_tws0{tws}".replace(".", "")
                            FOLDER_F  = os.path.join( RESULTS_FOLDER, CONFIG_F, "RUNS", RUN_F)

                            print("+---------------------------------------------------------------------------------")
                            print(f"| Processing RUN '{RUN_F}'")
                            print("+---------------------------------------------------------------------------------")

                            folder = os.path.join(script_path, "RUNS", FOLDER_F)

                            nlm_f = get_df_from_filter_csv(folder, "0_postfilter.csv")

                            diff = np.square(nofilter_raw['mom_x'].to_numpy() - nlm_f['mom_x'].to_numpy()).mean()
                            res[k,i,j] = diff
                            print(sigsq, hsq, diff)

                np.save(script_path + f"/data/results_MD{sc}_{osc}osc.npy", res)
            else:
                res = np.load(script_path + f"/data/results_MD{sc}_{osc}osc.npy")

            fig = plt.figure(figsize=(20, 12))

            for k, wv in enumerate(wall_velocities):
                ax1 = fig.add_subplot(3, 3, k+1, projection='3d')
                ax1.set_xlabel('σ² rel')
                ax1.set_ylabel('h² rel')
                ax1.set_zlabel('MSE')
                ax1.set_title(f"wall-velocity={wv}")
                X, Y = np.meshgrid(sigsq_rel, hsq_rel)
                print(X, Y)
                print(res[k])
                ax1.plot_surface(X, Y, res[k].T, cmap=cm.coolwarm, antialiased=False)
            fig.suptitle(f"Mean Squared Error with NLM filtering\ntime-window-size=5\nMD{sc} | oscillations={osc}", fontsize=16)
            fig.tight_layout(rect=[0, 0, 1, 0.97])
            fig.savefig(os.path.join(script_path, f"plots/results_nlm_sq_MD_{sc}_{osc}osc.pdf"), format="pdf")
            if SHOW_PLOTS:
                plt.show(block=True)