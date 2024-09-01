import os

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


script_path = os.path.dirname(os.path.abspath(__file__))

wt_1 = np.loadtxt(script_path + "/hsuper_1.txt")
wt_2 = np.loadtxt(script_path + "/hsuper_2.txt")

data = {'Array': ['8 cores, 1 node'] * 50 + ['8 cores, 2 nodes'] * 50,
        'Walltime': list(wt_1) + list(wt_2),
        'Machine': ['HSUper'] * 100}

df = pd.DataFrame(data)

sns_plot = sns.boxplot(x='Machine', y='Walltime', hue='Array', data=df, palette='colorblind')
plt.title('Walltime Comparison')
plt.xlabel('Machine')
plt.ylabel('Walltime')
plt.legend()
plt.show()

sns_plot.figure.savefig('walltime_comparison.pdf', format='pdf')