#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

domain_size = 100

"""
30 parallel
"""

def couette_analytic(x_c, t_c):
    u_w = 0.5
    H = 100.0
    visc = 2.632106414
    sum = 0
    for step in np.arange(1,31):
        sum = sum + 1/step*np.sin(step*np.pi*x_c/H)*np.exp(-step*step*np.pi*np.pi*visc*t_c/H/H)
    u_c = u_w*(1-x_c/H) - 2*u_w/np.pi*sum
    return u_c

print_error = False

plt.figure(figsize=(10.08,7.56))

my_map = "Paired"
x_step = 5
x = np.arange(x_step/2,100,x_step) # [2.5, 7.5, ..., 97.5] (20 values)
x2 = np.arange(0,100) # [0 - 99] (100 values)

t_start = 100
t_end = 1900
t_step = 100

md_offset = 3

counter = 0

plot_cycles = (100,400,800,1200,1600)

for number in plot_cycles:
    a = couette_analytic(x2,number/4-0.25)
    plt.plot(x2, a, color=sns.color_palette(my_map,20)[2*counter], linewidth=1)
    c_0 = np.zeros(6)
    c_e = np.zeros(6)
    x_c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(0), dtype="int")
    y_c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(1), dtype="int")
    z_c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(2), dtype="int")
    c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(3), dtype="float")

    for i in np.arange(6):
        z_slice = []
        for k in np.arange(i*36,(i+1)*36):
            z_slice += [c[k]]
        c_0[i] = np.mean(z_slice)
        #print( str(len(z_slice)) +","+ str(np.mean(z_slice)) +","+ str(c_0[i-particle_start]) +","+ str(np.std(z_slice)))
        # c_e[i-particle_start] = np.std(z_slice)
    if print_error:
        plt.errorbar(x[md_offset+particle_start:md_offset+particle_end], c_0, c_e, color=sns.color_palette(my_map,10)[2*counter+1], label=str(number), linestyle='none', marker='x')
    else:
        plt.plot(x[4:10], c_0, color=sns.color_palette(my_map,20)[2*counter+1], label=str(number), linestyle='none', marker='x')
        pass
    counter = counter + 1
plt.xlim(0,domain_size)
plt.xlabel('Z position')
plt.ylabel('X velocity')
plt.legend(title='coupling cycles')
plt.savefig('plot.png', bbox_inches='tight')
plt.show()
