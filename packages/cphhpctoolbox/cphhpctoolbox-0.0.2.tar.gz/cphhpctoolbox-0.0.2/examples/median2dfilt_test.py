#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# median2dfilt_test - simple 2d median filter test
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

"""Simple median filter test"""

import time
from numpy import zeros, random, uint16
import cphhpc.image.filter.median2d as median2d

data_type = uint16
image_shape = (2048, 2048)
filter_shape = (3, 3)

# Oneshot

input = (random.random(image_shape) * 10000).astype(data_type)
t1 = time.time()
output = median2d.filter(input, filter_shape)
t2 = time.time()
print 'median2d: %s secs' % (t2 - t1)

# Repeated use

t1 = time.time()

output = zeros(image_shape, dtype=data_type)
median2d.init(image_shape, filter_shape, data_type=input.dtype)

for i in xrange(10):
    median2d.filter_kernel(input, out=output)

median2d.free()

t2 = time.time()
print 'Repeated median2d: %s secs' % (t2 - t1)

