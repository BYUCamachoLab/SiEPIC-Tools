import pya
import sys
import os
import numpy as np
import copy
import matplotlib.pyplot as plt
from scipy.stats import kde
from SiEPIC.ann import getSparams as gs
from SiEPIC.ann import cascade_netlist as cn
from scipy.io import savemat
import time

sys.stdout = sys.__stdout__

# optional timer
# change dispTime to True to print elapsed time upon termination
start = time.time()
dispTime = True

# number of MC simulations to run
num_sims = 100

# mean and standard deviation for width
mu_width = 0.5
sigma_width = 0.005
# random distribution for width
random_width = np.random.normal(mu_width, sigma_width, num_sims)

# mean and standard deviation for thickness
mu_thickness = 0.22
sigma_thickness = 0.002
# random distribution for thickness
random_thickness = np.random.normal(mu_thickness, sigma_thickness, num_sims)

# mean and standard deviation for length
mu_length = 0
sigma_length = 0.01
# random distribution for length change
random_deltaLength = np.random.normal(mu_length, sigma_length, num_sims)

# run simulation with mean width and thickness
mean_s, frequency = gs.getSparams(mu_width, mu_thickness, 0)
results_shape = np.append(np.asarray([num_sims]), mean_s.shape)
results = np.zeros([dim for dim in results_shape], dtype='complex128')

# run simulations with varied width and thickness
for sim in range(num_sims):
    results[sim, :, :, :] = gs.getSparams(random_width[sim], random_thickness[sim], random_deltaLength[sim])[0]
    if (sim % 10) == 0:
        print(sim)

# rearrange matrix so matrix indices line up with proper port numbers
p = gs.getPorts(random_width[0], random_thickness[0], 0)
p = [int(i) for i in p]
rp = copy.deepcopy(p)
rp.sort(reverse=True)
concatinate_order = [p.index(i) for i in rp]
temp_res = copy.deepcopy(results)
re_res = np.zeros(results_shape, dtype=complex)
i=0
for idx in concatinate_order:
    re_res[:,:,i,:]  = temp_res[:,:,idx,:]
    i += 1
temp_res = copy.deepcopy(re_res)
i=0
for idx in concatinate_order:
    re_res[:,:,:,i] = temp_res[:,:,:,idx]
    i+= 1    
results = copy.deepcopy(re_res)

# print elapsed time if dispTime is True
stop = time.time()
if dispTime == True:
    print('Total simulation time: ')
    print(stop-start)

# save MC simulation results to matlab file
#savemat('Desktop/mc_results.mat', {'freq':frequency, 'results':results})

# plot histogram of varied responses with ideal response overlayed
# for port 2->1 
res21 = results[:, :, 2, 0]
res21 = 10*np.log10(abs(res21)**2)
res21 = np.reshape(res21, (res21.shape[0]*res21.shape[1]))
freq = frequency
for sim in range(1, num_sims):
    freq = np.append(freq, frequency)

# p.s. mean_s wansn't rearranged...
mean_s21 = mean_s[:, 3, 0]
mean_s21 = 10*np.log10(abs(mean_s21)**2)

plt.hist2d(freq, res21, bins=500, cmap=plt.cm.GnBu_r)
plt.colorbar()
plt.plot(frequency,  mean_s21, 'k', linewidth=1)
title = 'Monte Carlo Simulation (' + str(num_sims) + ' Runs)'
plt.title(title)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain (dB)')
plt.savefig('Desktop/MC_results.png', bbox_inches='tight')
plt.show()