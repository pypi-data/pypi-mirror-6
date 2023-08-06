"""
Copyright 2012 Christian Fobel

This file is part of geo_util.

geo_util is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

geo_util is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with geo_util.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import numpy as np

first_dim = 0
second_dim = 1


class CartesianSpace(object):
    def __init__(self, width, height, offset=None):
        self.dims = (width, height)
        self._scale = 1.
        if offset is None:
            self._offset = (0, 0)
        else:
            self._offset = offset
        if width >= height:
            self.largest_dim = first_dim
        else:
            self.largest_dim = second_dim

    @property
    def height(self):
        return self.dims[second_dim]

    @property
    def width(self):
        return self.dims[first_dim]

    @property
    def scale(self):
        return self._scale

    def translate_normalized(self, x, y):
        return np.array([x, y]) * self.dims + self._offset

    def normalized_coords(self, x, y):
        return np.array([(x - self._offset[first_dim]) / self.width,
                (y - self._offset[second_dim]) / self.height])

    def update_scale(self, scale_dims):
        dim = self.largest_dim
        self._scale = scale_dims[dim] / self.dims[dim]
