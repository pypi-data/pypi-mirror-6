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

u"""Provides unittest class TestSlopeCalculator."""


import sys
import unittest
import numpy
import ImageProcessing as I
import ImageProcessing.SlopeCalculator as IM
import pyphant.quantities as pq
from TestDistanceMapper import stringFeature
from pyphant.core import DataContainer

class TestSlopeCalculator(unittest.TestCase):
    """Tests the correct computation of distance maps for equally spaced features composed from one or more strings."""
    def setUp(self):
        self.dim = 11
        self.worker = IM.SlopeCalculator(None)

    def testSlopeOfString(self):
        """All elements of a string-like feature have distance 1 to the background."""

        referenceField = DataContainer.FieldContainer(
            stringFeature(self.dim),
            unit = '1',
            longname='String Feature',
            shortname='S')

        referenceField.seal()
        result = self.worker.slope(referenceField)

        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1,0)
#        numpy.testing.assert_array_equal(afoot,result.data)
#        assert(result.unit == referenceField.dimensions[0].unit)

if __name__ == '__main__':
    unittest.main()
