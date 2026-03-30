#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt

lamb = 1.6
a2l = 0.9
a2u = 1.1
pk = [0.22, 0.28, 0.3, 0.08, 0.07, 0.05]
mu = 0.8
alpha = 0.8
n = 200000
nb = 50

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12))

u = np.random.random(n)
x_exp = -np.log(1 - u) / lamb

x_uniform = np.random.uniform(a2l, a2u, n)

x_interarrival = x_exp * x_uniform
freq, bin_edges = np.histogram(x_interarrival, bins=nb, range=(0, np.max(x_interarrival)))
bin_lower = bin_edges[:-1]
bin_upper = bin_edges[1:]

effective_lamb = lamb / ((a2l + a2u) / 2)
y_expected = n * (np.exp(-effective_lamb * bin_lower) - np.exp(-effective_lamb * bin_upper))
bin_center = (bin_lower + bin_upper) / 2
bin_width = bin_edges[1] - bin_edges[0]
ax1.bar(bin_center, freq, width=bin_width, alpha=0.6, label='Simulated')
ax1.plot(bin_center, y_expected, 'r--', label='Expected', linewidth=3)
ax1.set_title('Interarrival Time Distribution')
ax1.set_xlabel('Time')
ax1.set_ylabel('Frequency')
ax1.legend()

x_subjob = np.random.choice(np.arange(1, 7), size=n, p=pk)
freq, bin_edges = np.histogram(x_subjob, bins=np.arange(1, 8)-0.5)
bin_center = np.arange(1, 7)
y_expected = n * np.array(pk)
ax2.bar(bin_center, freq, width=0.8, alpha=0.6, label='Simulated')
ax2.plot(bin_center, y_expected, 'r--', label='Expected', linewidth=3)
ax2.set_title('Sub-job Count Distribution')
ax2.set_xlabel('Number of Sub-jobs')
ax2.set_ylabel('Frequency')
ax2.legend()

x_service = (np.random.weibull(alpha, n) / mu) ** (1/alpha)
freq, bin_edges = np.histogram(x_service, bins=nb, range=(0, np.max(x_service)))
bin_lower = bin_edges[:-1]
bin_upper = bin_edges[1:]
y_expected = n * (np.exp(-(mu*bin_lower)**alpha) - np.exp(-(mu*bin_upper)**alpha))
bin_center = (bin_lower + bin_upper) / 2
bin_width = bin_edges[1] - bin_edges[0]
ax3.bar(bin_center, freq, width=bin_width, alpha=0.6, label='Simulated')
ax3.plot(bin_center, y_expected, 'r--', label='Expected', linewidth=3)
ax3.set_title('Service Time Distribution')
ax3.set_xlabel('Time')
ax3.set_ylabel('Frequency')
ax3.legend()

plt.tight_layout()
plt.savefig('rng_verification.pdf')
plt.close()