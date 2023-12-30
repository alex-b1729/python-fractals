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
# https://mathematica.stackexchange.com/questions/89458/how-to-make-a-nebulabrot
# http://www.steckles.com/buddha/
# http://www.paulbourke.net/fractals/burnship/

import os
import abc
import sys
import random
import argparse
import numpy as np
import pandas as pd
import datetime as dt
from time import perf_counter
import matplotlib.pyplot as plt
import matplotlib.image as pmimg


class Fractal(abc.ABC):
    """Fractal base class.
    Technically this is just for escape-time fractals
    """
    def __init__(self, name: str):
        self.name = name

        # image params
        self.xy = ((-2, 2), (2, -2))  # ((x1, y1), (x2, y2))
        self.pixels_per_unit = 231

        self.bound = 2

        self.xmin = -2
        self.xmax = 2
        self.ymin = -2
        self.ymax = 2
        self.c = 0
        self.z = 0
        self.color_map = 'RdBu_r'
        self.interpolation = 'bilinear'

        # matrix objects
        self.X = np.linspace(self.xy[0][0], self.xy[1][0],
                             abs(self.xy[1][0] - self.xy[0][0]) * self.pixels_per_unit).astype(np.float32)
        self.Y = np.linspace(self.xy[0][1], self.xy[1][1],
                             abs(self.xy[0][1] - self.xy[1][1]) * self.pixels_per_unit).astype(np.float32)
        self.complex_plane = self.X + self.Y[:, None] * 1j
        # N is the matrix of n that represent the number of iterations before a point escapes
        self.N = np.zeros_like(self.complex_plane, dtype=int)

    @abc.abstractmethod
    def quadratic_map(self, *args, **kwargs) -> None:
        """
        Function that defines the fractal.
        Modifies class attributes in-place and returns nothing.
        """
        return

    def calculate_N(self, iterations: int) -> None:
        """
        Calculates number of iterations for which each point in self.N remains bounded
        :param iterations: int for number of calculation iterations
        :return: None
        """
        for n in range(iterations):
            pass

    @abc.abstractmethod
    def set(self):
        pass

def in_julia_set(fract_params, xn, yn, iterations=100, bound=2):
    """Return Julia set matrix"""
    X = np.linspace(fract_params.xmin, fract_params.xmax, xn).astype(np.float32)
    Y = np.linspace(fract_params.ymin, fract_params.ymax, yn).astype(np.float32)
    Z = X + Y[:, None] * 1j
    N = np.zeros_like(Z, dtype=int)
    C = np.ones_like(Z, dtype=np.cdouble) * fract_params.c
    for n in range(iterations):
        I = abs(Z) < bound
        N[I] = n
        Z[I] = Z[I]**2 + C[I]
    return N

def in_burning_ship_set(fract_params, xn, yn, iterations=100, bound=2):
    """Return Mandelbrot set matrix"""
    X = np.linspace(fract_params.xmin, fract_params.xmax, xn).astype(np.float32)
    Y = np.linspace(fract_params.ymin, fract_params.ymax, yn).astype(np.float32)
    C = X + Y[:, None] * 1j
    N = np.zeros_like(C, dtype=int)
    Z = np.zeros_like(C)
    for n in range(iterations):
        I = abs(Z) < bound
        N[I] = n
        Z[I] = (np.abs(Z[I].real) + np.abs(Z[I].imag) * 1j)**2 + C[I]
        # Z[I] = (Z[I].real + np.abs(Z[I].imag) * 1j)**2 + C[I]
    return N

def in_mandelbrot_set(fract_params, xn, yn, iterations=100, bound=2):
    """Return Burning Ship set matrix"""
    X = np.linspace(fract_params.xmin, fract_params.xmax, xn).astype(np.float32)
    Y = np.linspace(fract_params.ymin, fract_params.ymax, yn).astype(np.float32)
    C = X + Y[:, None] * 1j
    N = np.zeros_like(C, dtype=int)
    Z = np.zeros_like(C)
    for n in range(iterations):
        I = abs(Z) < bound
        N[I] = n
        Z[I] = Z[I]**2 + C[I]
    return N

class Fract_Params():
    """Holds fractal parameters"""
    def __init__(self):
        self.fract_name = 'mandelbrot'
        self.xmin = -2
        self.xmax = 2
        self.ymin = -2
        self.ymax = 2
        self.c = 0
        self.z = 0
        self.color_map = 'Blues'
        self.interpolation = 'bilinear'
        self.save_fig = False
        self.cwd = os.getcwd()

def gen_fractal(fract_params, iterations=100, bound=2):
    """Generate fractal set"""

    # info to terminal
    print('Fractal:', fract_params.fract_name.capitalize(), 'set')
    print('Matplotlib color map:', fract_params.color_map)

    if fract_params.fract_name=='julia':
        # fract_params.xmin = -1.65
        # fract_params.xmax = 1.65
        # fract_params.ymin = -1.65
        # fract_params.ymax = 1.65
        # imag_var = complex(-0.835, -0.211)
        fract_params.c = complex(-0.82, -0.2)
        fractal_func = in_julia_set
    elif fract_params.fract_name=='mandelbrot':
        # xmin = -2.05
        # xmax = .6
        # ymin = -1.27
        # ymax = 1.27
        # fract_params.xmin = -.19
        # fract_params.xmax = -.13
        # fract_params.ymin = 1.01
        # fract_params.ymax = 1.06
        fract_params.c = 0
        fractal_func = in_mandelbrot_set
    elif fract_params.fract_name=='burning-ship':
        # xmin = -1.8
        # xmax = -1.7
        # ymin = -.1
        # ymax = .02
        # xmin = -2
        # xmax = 2
        # ymin = -2
        # ymax = 2
        # fract_params.xmin = -1.84
        # fract_params.xmax = -1.54
        # fract_params.ymin = .05
        # fract_params.ymax = -.1
        fract_params.c = 0
        fractal_func = in_burning_ship_set

    t0 = perf_counter()
    N = fractal_func(fract_params, xn=1024, yn=1024)
    t1 = perf_counter()
    tot_time = round(t1-t0, 3)
    print('Total time:', tot_time, 'seconds')

    plt.axis('off')
    plt.imshow(N, extent=[fract_params.xmin, fract_params.xmax,
                          fract_params.ymin, fract_params.ymax],
               interpolation=fract_params.interpolation, cmap=fract_params.color_map)

    if fract_params.save_fig:
        unique_save = dt.datetime.today().strftime('%m%d%Y-%H%M%S')
        save_path = os.path.join(fract_params.cwd, f'{fract_params.fract_name}_{unique_save}.png')
        plt.savefig(save_path, dpi=340, format='png', bbox_inches='tight')
        print('Saved to:', save_path)
        plt.show()
    else:
        plt.show()

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fractal', help='Fractal type', nargs='?', const='random')
parser.add_argument('-s', '--save', help='Save image', nargs='?', const='working_dir')
parser.add_argument('-c', '--colors', help='Matplotlib color map', nargs='?', const='random')
parser.add_argument('-i', '--interpolation', help='Image interpolation')
parser.add_argument('-x', '--center-point', help='Center of image in complex form: <real> <complex>', type=float, nargs=2, default=[0, 0])
parser.add_argument('-w', '--width', help='Width of image', type=float, default=4)
args = parser.parse_args()

fract_params = Fract_Params()

if args.fractal is not None:
    if args.fractal != 'random':
        fract_params.fract_name = args.fractal
    else:
        fract_params.fract_name = random.choices(['mandelbrot', 'julia', 'burning-ship'])[0]
else:
    fract_params.fract_name = 'mandelbrot'

if args.save is not None:
    fract_params.save_fig = True
    if args.save != 'working_dir':
        fract_params.cwd = args.save
    else:
        fract_params.cwd = os.path.join(os.getcwd(), 'fractal_images')
else:
    fract_params.save_fig = False

if args.colors is not None:
    if args.colors != 'random':
        fract_params.color_map = args.colors
    else:
        fract_params.color_map = random.choices(plt.colormaps())[0]
else:
    fract_params.color_map = 'RdBu_r'

if args.interpolation is not None:
    fract_params.interpolation = args.interpolation
else:
    fract_params.interpolation = 'bilinear'

# set min/max x/y values using center point and with
center_p = complex(args.center_point[0], args.center_point[1])
fract_params.xmin = center_p.real - args.width/2
fract_params.xmax = center_p.real + args.width/2
fract_params.ymin = center_p.imag - args.width/2
fract_params.ymax = center_p.imag + args.width/2

# =============================================================================
# # for testing
# fract_params = Fract_Params()
# fract_params.fract_name = 'burning-ship'
# fract_params.save = False
# fract_params.colors = 'RdBu_r'
# fract_params.interpolation = 'bilinear'
# fract_params.xmax = -1.56
# fract_params.xmin = -1.92
# fract_params.ymin = -.2
# fract_params.ymax = .16
# =============================================================================

if __name__=="__main__":
    # gen_fractal(fract_params)
    f = Fractal()
