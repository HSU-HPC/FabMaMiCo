import os

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from typing import *
from vtk import *

from plugins.FabMaMiCo.analysis.readers import get_df_from_filter_csv, get_df_from_cfd_vtk


script_path = os.path.dirname(os.path.abspath(__file__))

RESULTS_FOLDER = r"/media/jo/Jojos SSD/FabMaMiCo_results"
SHOW_PLOT = False


if __name__ == "__main__":
    # SETUP
    scenarios = [30, 60]
    wall_velocity = [0.2, 0.4, 0.6, 0.8, 1.0]
    oscillations = [2, 5]

    for sc in scenarios:
        for wv in wall_velocity:
            for osc in oscillations:
                RUN_F       = f"gauss_MD{sc}_wv{str(wv).replace('.', '')}"
                CONFIG_F    = f"fabmamico_study_3_filter_gauss_MD{sc}_{osc}osc_hsuper_1_72_mamico_run_ensemble"
                FOLDER_F    = os.path.join( RESULTS_FOLDER, CONFIG_F, "RUNS", RUN_F)
                RUN_MIMD    = f"MD{sc}_wv{str(wv).replace('.', '')}"
                CONFIG_MIMD = f"fabmamico_study_3_filter_nofilter_MD{sc}_{osc}osc_hsuper_1600_72_mamico_run_ensemble"
                FOLDER_MIMD = os.path.join( RESULTS_FOLDER, CONFIG_MIMD, "RUNS", RUN_MIMD )

                print("+-----------------------------------------------")
                print(f"| Processing RUN '{RUN_F}', {osc} oscillations")
                print("+-----------------------------------------------")

                md_raw      = get_df_from_filter_csv(FOLDER_F,    "0_raw-md.csv"  )
                my_gauss_2d = get_df_from_filter_csv(FOLDER_F,    "0_gauss-2d.csv")
                my_gauss_3d = get_df_from_filter_csv(FOLDER_F,    "0_gauss-3d.csv")
                md_mimd     = get_df_from_filter_csv(FOLDER_MIMD, "0_nofilter.csv")

                cfd_f  = get_df_from_cfd_vtk(FOLDER_F,  shape=md_raw.shape, scenario=sc)
                # cfd_nf = get_df_from_cfd_vtk(FOLDER_NF, shape=md_raw.shape)

                vtk_f  = cfd_f.groupby( ['iteration', 'idx_z'])['vel_x'].mean().reset_index()
                # vtk_nf = cfd_nf.groupby(['iteration', 'idx_z'])['vel_x'].mean().reset_index()

                md_raw['vel_x']      = md_raw['mom_x']      / md_raw['mass']
                my_gauss_2d['vel_x'] = my_gauss_2d['mom_x'] / my_gauss_2d['mass']
                my_gauss_3d['vel_x'] = my_gauss_3d['mom_x'] / my_gauss_3d['mass']
                md_mimd['vel_x']     = md_mimd['mom_x']     / md_mimd['mass']

                csv_raw = md_raw.groupby(      ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()
                csv_2d  = my_gauss_2d.groupby( ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()
                csv_3d  = my_gauss_3d.groupby( ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()
                csv_nf  = md_mimd.groupby(     ['iteration', 'idx_z'] )['vel_x'].mean().reset_index()

                fig, axs = plt.subplots(5, 1, figsize=(16, 18))
                iterations = np.arange(100, 1001, 10)

                diff = [-1, -1, -1]
                diff[0] = np.square(md_mimd['mom_x'].to_numpy() - md_raw['mom_x'].to_numpy()     ).mean()
                diff[1] = np.square(md_mimd['mom_x'].to_numpy() - my_gauss_2d['mom_x'].to_numpy()).mean()
                diff[2] = np.square(md_mimd['mom_x'].to_numpy() - my_gauss_3d['mom_x'].to_numpy()).mean()

                titles = ["Lattice-Boltzmann CFD 1", "Multi-Instance MD", "Pre-Gauss-Filter MD", "Gauss-2D-Filter MD", "Gauss-3D-Filter MD"]
                for k, d_f in enumerate([vtk_f, csv_nf, csv_raw, csv_2d, csv_3d]):
                    for i in range(6): # for each z-slice
                        z_vals = d_f[d_f['idx_z'] == i]['vel_x'].to_numpy()
                        axs[k].plot(iterations, z_vals, label=f"z_idx = {i}", color=f"C{i}")

                    axs[k].set_xlabel("Iteration")
                    axs[k].set_ylabel("Velocity")
                    title = titles[k]
                    if k > 1:
                        title += f" | Mean Squared Difference: {round(diff[k-2], 4)}"
                    axs[k].set_title(title)
                    axs[k].legend()
                fig.suptitle(f"Velocity in x-direction for averaged z-slices\nMD{sc} | wall-velocity={wv}", fontsize=16)
                fig.tight_layout(rect=[0, 0, 1, 0.97])
                if SHOW_PLOT:
                    plt.show()
                fig.savefig(os.path.join(script_path, "velocity_x_mean", f"MD{sc}_{osc}osc_wv{str(wv).replace('.','')}.pdf"), format="pdf")

                print(f"Mean difference between MIMD and Raw: {diff[0]}")
                print(f"Mean difference between MIMD and Gauss-2D: {diff[1]}")
                print(f"Mean difference between MIMD and Gauss-3D: {diff[2]}")

    sys.exit(0)
