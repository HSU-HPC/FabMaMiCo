import glob
import os
import random

import numpy as np
from matplotlib import pyplot as plt

from plugins.FabMaMiCo.analysis.readers import \
    get_hsq_and_sigmasq_from_output_file

script_path = os.path.dirname(os.path.abspath(__file__))

RESULTS_FOLDER = r"/media/jo/Jojos SSD/FabMaMiCo_results"
SHOW_PLOT = True

random.seed(0)


if __name__ == "__main__":
    scenarios = [30]
    oscillations = [2, 5]

    wall_velocities = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]

    sigsq_rels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    hsq_rels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    tws = 5

    # select some random configuration
    sc        = random.choice(scenarios)
    osc       = random.choice(oscillations)
    wv        = random.choice(wall_velocities)
    sigsq_rel = random.choice(sigsq_rels)
    hsq_rel   = random.choice(hsq_rels)

    RUN_F = f"nlm_MD{sc}_{osc}osc_wv{str(wv).replace('.', '')}_sigsqrel{sigsq_rel:.4f}_hsqrel{hsq_rel:.4f}_tws0{tws}".replace(".", "")
    CONFIG_F  = f"fabmamico_study_3_filter_nlm_sq_MD{sc}_hsuper_1"
    FOLDER_F  = os.path.join( RESULTS_FOLDER, CONFIG_F, "RUNS", RUN_F)
    print("+---------------------------------------------------------------------")
    print(f"| Processing RUN '{RUN_F}'")
    print("+---------------------------------------------------------------------")
    folder = os.path.join(script_path, "RUNS", FOLDER_F)

    # load data
    output_files = glob.glob(os.path.join(folder, "*.out"))
    if len(output_files) != 1:
        raise ValueError(f"Expected exactly one output file, but found {len(output_files)}")
    output_file = output_files[0]

    # extract the sigsq and hsq values for each coupling cycle
    sigsq, hsq = get_hsq_and_sigmasq_from_output_file(output_file)

    # plot the values against the coupling cycles
    start, marker, end = 0, 100, 1001
    min = np.min( [np.min(sigsq), np.min(hsq)] )
    max = np.max( [np.max(sigsq), np.max(hsq)] )
    fig, axs = plt.subplots(1, 1, figsize=(16, 8))
    # plot the first values with lower alpha
    axs.plot(range(start,marker), sigsq[:marker], color="C0", alpha=0.4)
    axs.plot(range(start,marker), hsq[:marker],   color="C1", alpha=0.4)
    # plot the values with full alpha
    axs.plot(range(marker,end),   sigsq[marker:], color="C0", label="σ²")
    axs.plot(range(marker,end),   hsq[marker:],   color="C1", label="h²")
    # add vertical lines to indicate the analyzed coupling cycle interval
    axs.vlines( 100, ymin=min, ymax=max, ls="--", lw=3, color="grey")
    axs.vlines(1000, ymin=min, ymax=max, ls="--", lw=3, color="grey")
    # add labels, title and legend
    axs.set_xlabel("coupling cycle")
    axs.set_ylabel("filter parameter value")
    axs.set_xticks([i*100 for i in range(11)])
    fig.suptitle("        σ² and h² over coupling cycles", fontsize=16)
    axs.set_title(f"MD{sc} | oscillations={osc} | wall-velocity={wv}\n"\
                  f"sigsq=10 | hsq=20 | sigsq_rel={sigsq_rel} | hsq_rel={hsq_rel}\n"\
                  f"time-window-size={tws}")
    axs.grid(True)
    fig.tight_layout()
    axs.legend()
    # save the plot
    fig.savefig(os.path.join(script_path, f"plots/h_and_sigma_over_time__{RUN_F}.pdf"), format="pdf")
    # optionally show the plot
    if SHOW_PLOT:
        plt.show(block=True)
