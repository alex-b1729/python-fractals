#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021 Alexander Brefeld <code@abrefeld.anonaddy.com>

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
import json
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
        self._xy = ((-2, 2), (2, -2))  # ((x1, y1), (x2, y2)) eg bounding box
        self._center = (0, 0)
        self._width = 4
        self._height = 4
        self._magnification = 1

        self.pixels_per_unit = 231

        self.escape_bound = 2
        self.iterations = 100

        self.c = 1
        # self.z = 0

        # render defaults
        self.color_map = 'RdBu_r'
        self.interpolation = 'bilinear'

    def init_complex_plane(self) -> None:
        """
        Builds X and Y as np.linspace and create plane of calculation
        :return: None
        """
        self.X = np.linspace(self._xy[0][0], self._xy[1][0],
                             self.pixels_per_unit).astype(np.longdouble)
        self.Y = np.linspace(self._xy[0][1], self._xy[1][1],
                             self.pixels_per_unit).astype(np.longdouble)
        self.complex_plane = self.X + self.Y[:, None] * 1j

    @abc.abstractmethod
    def init_calculation_values(self) -> None:
        """
        Define self.C, self.Z, self.N
        :return: None
        """

    @abc.abstractmethod
    def quadratic_map(self, *args, **kwargs) -> None:
        """
        Function that defines the fractal.
        Should modify _calc class parameters in place??
        """
        pass

    def calculate_escape_time(self) -> None:
        """
        Calculates number of iterations for which each point in self.N remains bounded
        :param iterations: int for number of calculation iterations
        :return: None
        """
        sys.stdout.write(f'Calculating escape time for {self.name} with {self.iterations} iterations\n')
        self.init_complex_plane()
        self.init_calculation_values()
        for n in range(self.iterations):
            # I: np.array is matrix of Z values that haven't yet escaped
            # apply quadratic_map only to these values
            I = abs(self.Z) < self.escape_bound
            self.quadratic_map(I)
            sys.stdout.write(
                f'\rProgress: {"#" * int(40 * n / self.iterations)}{" " * (40 - int(40 * n / self.iterations))}| '
                f'{int(100 * n / self.iterations)}%')

    def render(self, show: bool = True, save_path: str = None):
        plt.axis('off')
        plt.imshow(self.N, origin='lower', interpolation=self.interpolation, cmap=self.color_map)
        if save_path is not None:
            plt.savefig(save_path, dpi=self.pixels_per_unit, format='png', bbox_inches='tight')
        if show:
            plt.show()

    def set_bounding_box(self,
                         center: tuple[float, float] = (0., 0.),
                         width: float = 4.,
                         height: float = None,
                         magnification: int = None,
                         xy: tuple[tuple[float, float], tuple[float, float]] = None
                         ) -> None:
        """
        Define image bounding box
        :param center: (Re(c), Im(c))
        :param width:
        :param height: if None set to width
        :param magnification: relative to default bounding box of ((-2, 2), (2, -2))
        :param xy: bounding box
        :return: None
        """
        if xy is not None:
            assert xy[0][0] < xy[1][0] and xy[0][1] > xy[1][1]
            self._xy = xy
            self._center = ((xy[0][0] + xy[1][0]) / 2,
                            (xy[0][1] + xy[1][1]) / 2)
            self._width = xy[1][0] - xy[0][0]
            self._height = xy[0][1] - xy[1][1]
            self._magnification = 4 / self._width
        else:
            if height is None: height = width
            if magnification is None:
                magnification = 1
                self._magnification = 4 / width
            width, height = width / magnification, height / magnification
            x1 = center[0] - width / 2
            y1 = center[1] + height / 2
            self._xy = ((x1, y1), (x1 + width, y1 - height))
            self._center = center
            self._width = width
            self._height = height

    @property
    def params(self) -> dict:
        return {
            'name': self.name,
            'xy': self._xy,
            'center': self._center,
            'width': self._width,
            'height': self._height,
            'magnification': self._magnification,
            'pixels_per_unit': self.pixels_per_unit,
            'escape_bound': self.escape_bound,
            'iterations': self.iterations,
            'c': self.c,
            # self.z = 0
            'color_map': self.color_map,
            'interpolation': self.interpolation
        }

    def export_params(self, path: str):
        with open(path, 'w') as f:
            f.write(json.dumps(self.params, indent=4))

    def import_params(self, path: str):
        with open(path, 'r') as f:
            params = json.loads(f.read())

        self._xy = params['xy']
        self._center = params['center']
        self._width = params['width']
        self._height = params['height']
        self._magnification = params['magnification']
        self.pixels_per_unit = params['pixels_per_unit']
        self.escape_bound = params['escape_bound']
        self.iterations = params['iterations']
        self.c = params['c']
        self.color_map = params['color_map']
        self.interpolation = params['interpolation']


class MandelbrotSet(EscapeTimeFractal):
    def __init__(self):
        super().__init__('Mandelbrot Set')

    def init_calculation_values(self) -> None:
        self.C = self.complex_plane
        self.Z = np.zeros_like(self.C)
        self.N = np.zeros_like(self.C, dtype=int)

    def quadratic_map(self, I: np.array) -> None:
        """I (np.array) mask defining which values to apply calculation to"""
        self.N[I] += 1
        self.Z[I] = self.Z[I] ** 2 + self.C[I]


class JuliaSet(EscapeTimeFractal):
    def __init__(self):
        super().__init__('Julia Set')

    def init_calculation_values(self) -> None:
        self.C = np.ones_like(self.complex_plane, dtype=np.clongdouble) * self.c
        self.Z = self.complex_plane
        self.N = np.zeros_like(self.C, dtype=int)

    def quadratic_map(self, I: np.array) -> None:
        self.N[I] += 1
        self.Z[I] = self.Z[I] ** 2 + self.C[I]


class BurningShipSet(EscapeTimeFractal):
    def __init__(self):
        super().__init__('Burning Ship Set')

    def init_calculation_values(self) -> None:
        self.C = self.complex_plane
        self.Z = np.zeros_like(self.complex_plane, dtype=np.clongdouble)
        self.N = np.zeros_like(self.C, dtype=int)

    def quadratic_map(self, I: np.array) -> None:
        self.N[I] += 1
        self.Z[I] = (np.abs(self.Z[I].real) + np.abs(self.Z[I].imag) * 1j)**2 + self.C[I]


if __name__ == '__main__':
    # Mandelbrot Misiurewicz point
    f = MandelbrotSet()
    # f.set_bounding_box(center=(-0.743030, 0.126433), width=0.016110) #, magnification=500)

    # f = JuliaSet()
    # f.c = complex(-0.835, -0.2321)

    # f = BurningShipSet()
    # f.set_bounding_box(center=(-1.7, 0), width=0.3, height=0.3)

    # f.pixels_per_unit = 500
    # f.iterations = 1000
    # f.export_params('/Users/abrefeld/Desktop/fractest.json')
    f.import_params('/Users/abrefeld/Desktop/fractest.json')
    print(f.params)
    f.calculate_escape_time()
    f.render()
