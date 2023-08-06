# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
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

u"""Provides unittest classes for UltimatePointsCalculator worker
"""


import unittest
import numpy


class UltimatePointsCalculatorTestCase(unittest.TestCase):
    def testUltimatePoints(self):
        from ImageProcessing.UltimatePointsCalculator \
             import UltimatePointsCalculator
        from pyphant.core.DataContainer import FieldContainer
        from pyphant.quantities import Quantity
        data = numpy.zeros((10, 10), dtype='uint8')
        data[1][2] = 1
        data[5][3] = 2
        image = FieldContainer(data)
        for dim in image.dimensions:
            dim.unit = Quantity('1 mum')
        image.seal()
        upc = UltimatePointsCalculator()
        result = upc.findUltimatePoints(image)
        self.assertEqual(result['i'].unit, Quantity('1 mum'))
        self.assertEqual(result['j'].unit, Quantity('1 mum'))
        indices = zip(result['j'].data, result['i'].data)
        self.assertTrue((1, 2) in indices)
        self.assertTrue((5, 3) in indices)
        self.assertEqual(len(indices), 2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
