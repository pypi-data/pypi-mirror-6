#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# convolve2d_test - simple 2d convolution test
# Copyright (C) 2011-2014  The CPHHPC Project lead by Brian Vinter
#
# This file is part of CPHHPC Toolbox.
#
# CPHHPC Toolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CPHHPC Toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.
#
# -- END_HEADER ---
#

"""Simple convolve2d filter test"""

import time
from numpy import zeros, random, float32, array
import cphhpc.signal.convolution.convolve2d as convolve2d

data_type = float32
image_shape = (2048, 2048)

convolve_window = data_type(array([[3.0, 10.0, 3.0], [0.0, 0.0, 0.0],
                            [-3.0, -10.0, -3.0]]) / 32)

# Oneshot

input = (random.random(image_shape) * 100).astype(data_type)
t1 = time.time()
output = convolve2d.convolve2d(input, convolve_window)
t2 = time.time()
print 'convolve2d: %s secs' % (t2 - t1)

# Repeated use

t1 = time.time()

output = zeros(image_shape, dtype=data_type)
convolve2d.init(image_shape, convolve_window, padding='pass',
                data_type=data_type)

repeats = 10
for i in xrange(repeats):
    convolve2d.convolve2d_kernel(input, out=output)

convolve2d.free()

t2 = time.time()
print "Repeated %s convolve2d's in %s secs" % (repeats, t2 - t1)

