#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021 Alexander Brefeld <alexander.brefeld@protonmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# References:
# https://users.math.yale.edu/public_html/People/frame/Fractals/MandelSet/welcome.html
# https://www.johnmyleswhite.com/notebook/2009/12/18/using-complex-numbers-in-r/
# https://randomascii.wordpress.com/2011/08/13/faster-fractals-through-algebra/
# https://www.cygnus-software.com/docs/html/64bitcalcs.htm
# https://matplotlib.org/stable/gallery/showcase/mandelbrot.html#sphx-glr-gallery-showcase-mandelbrot-py
# https://stackoverflow.com/questions/24185083/change-resolution-of-imshow-in-ipython
# https://pythoninformer.com/generative-art/fractals/burning-ship/

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as pmimg
from time import perf_counter

def in_julia_set(c, xmin, xmax, ymin, ymax, xn, yn, iterations=100, bound=2):
    """Return Julia set matrix"""
    X = np.linspace(xmin, xmax, xn).astype(np.float32)
    Y = np.linspace(ymin, ymax, yn).astype(np.float32)
    Z = X + Y[:, None] * 1j
    N = np.zeros_like(Z, dtype=int)
    C = np.ones_like(Z, dtype=np.cdouble) * c
    for n in range(iterations):
        I = abs(Z) < bound
        N[I] = n
        Z[I] = Z[I]**2 + C[I]
    # N[N == iterations-1] = 0
    return N

def in_mandelbrot_set(z, xmin, xmax, ymin, ymax, xn, yn, iterations=100, bound=2):
    """Return Mandelbrot set matrix"""
    X = np.linspace(xmin, xmax, xn).astype(np.float32)
    Y = np.linspace(ymin, ymax, yn).astype(np.float32)
    C = X + Y[:, None] * 1j
    N = np.zeros_like(C, dtype=int)
    Z = np.zeros_like(C)
    for n in range(iterations):
        I = abs(Z) < bound
        N[I] = n
        Z[I] = Z[I]**2 + C[I]
    # N[N == iterations-1] = 0
    return N

def gen_fractal(iterations=100, bound=2, fract_name='julia'):
    resolution = 0.01
    img_width = 1.65
    save_fig = True
    fract_name = 'mandelbrot'

    c = complex(-0.835, -0.211)

    t0 = perf_counter()
    N = in_julia_set(c=c, xmin=-img_width, xmax=img_width, ymin=-img_width, ymax=img_width, xn=2000, yn=2000)
    t1 = perf_counter()
    print(t1-t0)
    
    # dpi = 1024
    # width = 10
    # height = 10
    # fig = plt.figure(figsize=(width, height), dpi=dpi)
    # ax = fig.add_axes([0,0,1,1], frame_on=False, aspect=1)
    # plt.axis('off')
    # ax.imshow(N, extent=[-img_width, img_width, -img_width, img_width], interpolation='bilinear', cmap='bone_r')
    # abc.savefig(f'/Users/abrefeld/Desktop/fractal_pics/{fract_name}.png', dpi=1024, format='png')
    
    plt.axis('off')
    plt.imshow(N, extent=[-img_width, img_width, -img_width, img_width], interpolation='bilinear', cmap='bone_r')
    if save_fig: 
        plt.savefig(f'/Users/abrefeld/Desktop/fractal_pics/{fract_name}.png', dpi=1024, format='png', bbox_inches='tight')

    # img = plt.imshow(vis_matrix, cmap='bone_r')
    # plt.axis('off')
    # if save_fig:
    #     plt.savefig(f'/Users/abrefeld/Desktop/fractal_pics/{fract_name}.png', dpi=1024, format='png', bbox_inches='tight')
    # plt.show()



gen_fractal()
