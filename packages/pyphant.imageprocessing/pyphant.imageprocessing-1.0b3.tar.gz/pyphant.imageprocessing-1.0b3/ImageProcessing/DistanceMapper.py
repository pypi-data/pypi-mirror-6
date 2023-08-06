# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""
The Map Distance worker is a class of Pyphant's Image Processing
Toolbox. It is used to determine the size of respective features in
binary images through calculating the distance of every pixel to the
nearest background pixel.
"""

from pyphant.core import (Worker, Connectors, DataContainer)
import scipy
import copy
from ImageProcessing import FEATURE_COLOR
import pkg_resources


def UnEqualUnits():
    raise ValueError("The dimensions do not have equal units.")


class Metrics:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.equalDiscretisations = True
        self.checkDimensions()
        self.dydx = self.dy / self.dx
        rt2 = scipy.sqrt(1.0 + self.dydx ** 2)
        self.metric = scipy.array(
            [[rt2, self.dydx, rt2], [1, 2, 1], [rt2, self.dydx, rt2]]
            )

    def distance(self, square):
        assert square.shape == (3, 3), 'Method distance expects a 3x3 matrix '\
               'as input, but got a %ix%i matrix!' % square.shape
        metric = self.metric.copy()
        result = scipy.amin(metric + square)
        return result

    def checkDimensions(self):
        try:
            if not (self.dimensions[0].unit == self.dimensions[1].unit):
                UnEqualUnits()
        except TypeError:
            UnEqualUnits()
        delta = map(lambda d: scipy.diff(d.data), self.dimensions)
        for dim in delta:
            if abs(dim.min() - dim.max()) > 1E-4:
                raise ValueError("Each dimension has to be equally spaced.")
        self.dx = delta[0].min()
        self.dy = delta[1].min()


class DistanceMapper(Worker.Worker):
    API = 2
    VERSION = 2
    REVISION = pkg_resources.get_distribution(
        "pyphant.imageprocessing"
        ).version
    name = "Map Distance"
    _sockets = [("image", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def calculateDistanceMap(self, image, subscriber=0):
        """
        This worker calculates the Euklidean distance map of the
        (binary) image provided. Features are expected to be black (i.e. 0),
        background is expected white.
        The given image is modified in place!
        The algorithm used is modified after the solution discussed in
        "The Image Processing Handbook, Fourth Edition"
        by John C. Russ (p. 427ff).
        """
        metric = Metrics(image.dimensions)
        nx, ny = image.data.shape
        nx += 2
        ny += 2
        im = scipy.zeros((nx, ny), dtype=image.data.dtype)
        im[:, :] = FEATURE_COLOR
        im[1:-1, 1:-1] = image.data
        g = nx * nx + ny * ny
        a = scipy.where(im == FEATURE_COLOR, g, 0).astype('d')
        rowPercentage = 50.0 / ny
        featurePixels = []
        for y in xrange(1, ny - 1):
            subscriber %= y * rowPercentage
            for x in xrange(1, nx - 1):
                if a[x, y] > 0:
                    a[x, y] = metric.distance(a[x - 1:x + 2, y - 1:y + 2])
                    featurePixels.append((x, y))
        subscriber %= 50
        if len(featurePixels) > 0:
            perc = 50.0 / len(featurePixels)
            acc = 50.0
            for (x, y) in reversed(featurePixels):
                acc += perc
                subscriber %= acc
                a[x, y] = metric.distance(a[x - 1:x + 2, y - 1:y + 2])
        a = scipy.where(a == g, 0, a)
        result = DataContainer.FieldContainer(
            a[1:-1, 1:-1] * metric.dx,
            image.dimensions[0].unit,
            rescale=True,
            dimensions=copy.deepcopy(image.dimensions),
            longname=u'Distance to background',
            shortname=u'D'
            )
        result.seal()
        return result
