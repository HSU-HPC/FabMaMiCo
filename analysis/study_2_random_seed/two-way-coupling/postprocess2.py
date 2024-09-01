#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
#from matplotlib import cm
import seaborn as sns

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
plt.rcParams['font.size'] = '14'
#plt.rcParams["font.weight"] = "bold"
#plt.rcParams["axes.labelweight"] = "bold"
my_map = "Paired"
x_step = 5
x = np.arange(x_step/2,100,x_step)
x2 = np.arange(0,100)
t_start = 100
t_end = 1120 #2805
t_step = 220
md_offset = 3
particle_start = 1 # choose zero to plot the first cell values 
particle_end = 7
particle_number_csv = 8
counter = 0
plot_cycles = (100,260,460,700,1900)
for number in plot_cycles:
    a = couette_analytic(x2,number/4-0.25)
    plt.plot(x2, a, color=sns.color_palette(my_map,10)[2*counter], linewidth=1)
    # f = np.genfromtxt("velocity_"+str(number)+".txt", usecols=(0), delimiter=',', dtype="float")
    #x_help = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]
    #x_help = [0,1,2,3,4,5,6,7,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]
    # x_help = [0,1,2,3,10,11,12,13,14,15,16,17,18,19]
    # plt.plot(x[x_help], f, linestyle ='none', marker='o', color=sns.color_palette(my_map,10)[2*counter+1])
    x_c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(0), dtype="int")
    y_c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(1), dtype="int")
    z_c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(2), dtype="int")
    c = np.genfromtxt("CouetteAvgMultiMDCells_0_0_"+str(number)+".csv", delimiter=';', usecols=(3), dtype="float")
    c_0 = np.zeros(particle_end-particle_start)
    c_e = np.zeros(particle_end-particle_start)
    helper = particle_number_csv*particle_number_csv
    for i in np.arange(particle_start, particle_end):
        z_slice = []
        for k in np.arange(i*helper,(i+1)*helper):
            if x_c[k] >= particle_start+md_offset and x_c[k] < particle_end+md_offset:
                if y_c[k] >= particle_start+md_offset and y_c[k] < particle_end+md_offset:
                    z_slice += [c[k]]
            if x_c[k]==7: 
                if y_c[k]==7:
                    c_0[i-particle_start] = c_0[i-particle_start]+c[k]
        #print( str(len(z_slice)) +","+ str(np.mean(z_slice)) +","+ str(c_0[i-particle_start]) +","+ str(np.std(z_slice)))
        c_e[i-particle_start] = np.std(z_slice)
    if print_error:
        plt.errorbar(x[md_offset+particle_start:md_offset+particle_end], c_0, c_e, color=sns.color_palette(my_map,10)[2*counter+1], label=str(number), linestyle='none', marker='x')
    else:
        plt.plot(x[md_offset+particle_start:md_offset+particle_end], c_0, color=sns.color_palette(my_map,10)[2*counter+1], label=str(number), linestyle='none', marker='x')
    counter = counter + 1 
plt.xlim(0,100)
plt.xlabel('Z position')
plt.ylabel('X velocity')
plt.legend(title='coupling cycles')
plt.savefig('plot.png', bbox_inches='tight')
plt.show()


 