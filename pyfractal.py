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
from PIL import Image
from time import perf_counter
import matplotlib.pyplot as plt
import matplotlib.image as pmimg


class EscapeTimeFractal(abc.ABC):
    """Escape-time fractal base class"""
    def __init__(self, name: str):
        self.name = name

        # image params
        self.xy = ((-2, 2), (2, -2))  # ((x1, y1), (x2, y2))
        self.pixels_per_unit = 231

        self.escape_bound = 2

        # self.xmin = -2
        # self.xmax = 2
        # self.ymin = -2
        # self.ymax = 2
        # self.c = 0
        # self.z = 0
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
        self.Z = None
        self.C = None

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, value):
        self._c = value
        self.C *= value

    @abc.abstractmethod
    def quadratic_map(self, *args, **kwargs) -> None:
        """
        Function that defines the fractal.
        Modifies class parameters in place
        """
        pass

    def calculate_escape_time(self, iterations: int) -> None:
        """
        Calculates number of iterations for which each point in self.N remains bounded
        :param iterations: int for number of calculation iterations
        :return: None
        """
        # I: np.array is matrix of Z values that haven't yet escaped
        # apply quadratic_map only to these values
        for n in range(iterations):
            I = abs(self.Z) < self.escape_bound
            self.quadratic_map(I)

    def render(self, show: bool = True, save_path: str = None):
        plt.axis('off')
        plt.imshow(self.N, origin='lower', interpolation=self.interpolation, cmap=self.color_map)
        if save_path is not None:
            plt.savefig(save_path, dpi=self.pixels_per_unit, format='png', bbox_inches='tight')
        if show:
            plt.show()

    def set_center(self, center: tuple[float, float]):
        pass


class MandelbrotSet(EscapeTimeFractal):
    def __init__(self):
        super().__init__('Mandelbrot Set')

        # mandelbrot calc params
        self.C = self.complex_plane
        self.Z = np.zeros_like(self.C)

    def quadratic_map(self, I: np.array) -> None:
        """I (np.array) mask defining which values to apply calculation to"""
        self.N[I] += 1
        self.Z[I] = self.Z[I] ** 2 + self.C[I]


class JuliaSet(EscapeTimeFractal):
    def __init__(self):
        super().__init__('Julia Set')

        # # julia set params
        self.Z = self.complex_plane
        self.C = np.ones_like(self.complex_plane, dtype=np.cdouble) #* self.c

    def quadratic_map(self, I: np.array) -> None:
        self.N[I] += 1
        self.Z[I] = self.Z[I] ** 2 + self.C[I]


class BurningShipSet(EscapeTimeFractal):
    def __init__(self):
        super().__init__('Burning Ship Set')

        # burning ship params
        self.C = self.complex_plane
        self.Z = np.zeros_like(self.complex_plane) #, dtype=np.cdouble)

    def quadratic_map(self, I: np.array) -> None:
        self.N[I] += 1
        self.Z[I] = (np.abs(self.Z[I].real) + np.abs(self.Z[I].imag) * 1j)**2 + self.C[I]


if __name__=="__main__":
    # f = MandelbrotSet()
    f = JuliaSet()
    # f = BurningShipSet()
    f.c = complex(-0.82, -0.2)
    f.calculate_escape_time(100)
    f.render()
