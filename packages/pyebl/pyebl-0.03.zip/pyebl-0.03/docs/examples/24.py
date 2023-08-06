#!/usr/bin/env python
import os
WD = os.path.abspath(os.curdir) + '\\'

##########
import pyebl as edw

import numpy as np

amplitude = 100.0
wavelength = 100.0
phase = 0.0
stripe_length = 1000.0
stripe_width = 5.0

A = amplitude
k = 2*np.pi/wavelength
phi = phase
L = stripe_length
w = stripe_width

N = L/wavelength
L = N*wavelength

# samples per period
N_p = 2**8
# total samples
N_s = N*N_p

x_samples = np.linspace(-L/2.0, L/2.0, N_s)
y_top = A*np.sin(k*x_samples + phi) + w/2
y_bottom = A*np.sin(k*x_samples + phi) - w/2

points_top = list(zip(x_samples, y_top))
points_bottom = list(zip(x_samples, y_bottom))[::-1]

stripe = edw.poly(points = points_top + points_bottom)

edw.save(stripe, WD + "output/24", format="ely, svg")
