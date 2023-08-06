#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# gauss2d - Gauss 2-dimensional convolution filter
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

"""Gauss 2-dimensional numpy convolution filter"""

from numpy import zeros, float32, exp
from cphhpc.signal.convolution.kernels import allowed_padding, \
    separate2d, ses_convolve2d_separate

# Globals

_cache = {}


def init(
    input_shape,
    filter_shape,
    sigma,
    padding='pass',
    data_type=float32,
    gauss_id='oneshot',
    ):
    """
    Initializes the data structures needed for the gauss2d filtering
    
    Parameters
    ----------
    input_shape : (int, int)
        Shape of input (rows, cols)
    filter_shape : (int, int)
        Filter window shape (rows, cols) (must be odd)
    sigma : int
        The sigma value used to generate the `Gaussian window 
        <http://en.wikipedia.org/wiki/Gaussian_filter>`_
    padding : str, optional
        How to handle border elements, default is 'pass' as we initialize
        padded input to zero and never touch those elements again.
        Valid paddings: 'pass', 'zero', 'replicate'
    data_type : data-type, optional
        The precision of the data structures needed for the gauss2d filtering
    gauss_id : str, optional
        Used to identify cache settings for different gauss2d filteres
                
    Raises
    ------
    ValueError
        If *filter_shape* values are even or 
        if parameters have the wrong type
    """

    # Check parameter types

    if type(input_shape) != tuple or len(input_shape) != 2 \
        or type(input_shape[0]) != int or type(input_shape[1]) != int:
        msg = 'input_shape: %s is _NOT_ a two-tuple of integers' \
            % str(input_shape)
        raise ValueError(msg)

    if type(filter_shape) != tuple or len(filter_shape) != 2 \
        or type(filter_shape[0]) != int or type(filter_shape[1]) != int:
        msg = 'filter_shape: %s is _NOT_ a two-tuple of integers' \
            % str(filter_shape)
        raise ValueError(msg)

    if type(sigma) != int:
        msg = 'sigma: %s must be an integer' % str(sigma)
        raise ValueError(msg)

    if not padding in allowed_padding:
        msg = 'Padding: %s _NOT_ supported, valid paddings: %s' \
            % (padding, allowed_padding.keys())
        raise ValueError(msg)

    # Init cache

    if _cache.has_key(gauss_id):
        _cache[gauss_id].clear()
    else:
        _cache[gauss_id] = {}

    cache = _cache[gauss_id]

    gauss_matrix = _generate_gauss_matrix(filter_shape, sigma,
            data_type)

    cache['gauss_vectors'] = separate2d(gauss_matrix, data_type)

    cache['gauss_window_radius'] = (len(cache['gauss_vectors'][0]) / 2,
                                    len(cache['gauss_vectors'][1]) / 2)

    cache['input_shape'] = input_shape

    cache['padded_shape'] = (input_shape[0] + 2
                             * cache['gauss_window_radius'][0],
                             input_shape[1] + 2
                             * cache['gauss_window_radius'][1])

    cache['padding'] = allowed_padding[padding]

    cache['tmp_padded_input'] = zeros(cache['padded_shape'],
            dtype=data_type)

    cache['tmp_col_result'] = zeros((cache['input_shape'][0],
                                    cache['padded_shape'][1]),
                                    dtype=data_type)

    cache['data_type'] = data_type


def free(gauss_id='oneshot'):
    """
    Free up the internal data structures needed for the gauss2d filtering
    
    Parameters
    ----------
    gauss_id : str, optional
        Used to identify cache settings for different gauss2d filteres
    """

    if _cache.has_key(gauss_id):
        _cache[gauss_id].clear()
        del _cache[gauss_id]


def _generate_gauss_matrix(filter_shape, sigma, data_type=float32):
    """
    Returns a Gauss filter matrix equivalent to the MATLAB
    fspecial('gaussian', dim, sigma) function
    
    Parameters
    ----------
    filter_shape : (int, int)
        Filter window shape (rows, cols) (must be odd)
    sigma : int
        The sigma value used to generate the `Gaussian window
        <http://en.wikipedia.org/wiki/Gaussian_filter>`_
    data_type : data-type, optional
        The precision of the generated gauss window

    Returns
    -------
    output : ndarray
        Gauss convolution matrix with the given dimensions, sigma and
        data_type.
    
    Raises
    ------
    ValueError
        If *filter_shape* values are even
    """

    if filter_shape[0] % 2 == 0 or filter_shape[1] % 2 == 0:
        msg = 'filter_shape: %s is _NOT_ odd' % str(filter_shape)
        raise ValueError(msg)

    result = zeros(filter_shape, dtype=data_type)

    y_radius = filter_shape[0] / 2
    x_radius = filter_shape[1] / 2

    for y in xrange(filter_shape[0]):
        y_distance = y - y_radius
        for x in xrange(filter_shape[1]):
            x_distance = x - x_radius
            result[y, x] = exp(-(y_distance ** 2 + x_distance ** 2)
                               / (2.0 * sigma ** 2))

    result = result / result.sum()

    return result


def filter_kernel(input, out=None, gauss_id='oneshot'):
    """
    Returns a 2d Gauss filtered array based on `convolution
    <http://www.songho.ca/dsp/convolution/convolution.html>`_.
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    out : ndarray, optional
        Output argument. This must have the exact kind that would be returned
        if it was not used. In particular, it must have the right type, must be
        C-contiguous, and its dtype must be the dtype that would be returned
        for *filter_kernel(input, ...)*. This is a performance feature.
        Therefore, if these conditions are not met, an exception is raised,
        instead of attempting to be flexible.
    gauss_id : str, optional
        Used to identify cache settings for different gauss2d filteres
           
    Returns
    -------
    output : ndarray
        2d Gauss filtered version of *input*,
        if *out* is given, then it is returned.
        if not *output* is created with shape and type equivalent to *input*. 
        
    Raises
    ------
    ValueError
        If gauss2d wasn't initialized or if the shape of *input*
        doesn't match the one given to the init function or
        if the shape and dtype of *input* and *out* don't match.
    """

    if _cache.has_key(gauss_id):
        cache = _cache[gauss_id]
    else:
        msg = 'gauss2d is not initialized with gauss_id: %s' % gauss_id
        raise ValueError(msg)

    input_shape = cache['input_shape']
    tmp_padded_input = cache['tmp_padded_input']
    gauss_window_radius = cache['gauss_window_radius']
    padding = cache['padding']
    tmp_col_result = cache['tmp_col_result']
    gauss_vectors = cache['gauss_vectors']
    data_type = cache['data_type']

    # If pre-allocated output matrix provided, check shape and types

    if input.shape != input_shape:
        msg = 'input.shape: %s differs from init shape %s' \
            % (str(input.shape), str(input_shape))
        raise ValueError(msg)

    if out is not None:
        if out.shape != input_shape:
            msg = 'out.shape: %s differs from init shape: %s' \
                % (str(out.shape), str(input_shape))
            raise ValueError(msg)
        if out.dtype != data_type:
            msg = 'out.dtype: %s differs from data_type: %s' \
                % (out.dtype, data_type)
            raise ValueError(msg)
    else:

        # If no pre-allocated output matrix provided, allocate data

        out = zeros(input.shape, dtype=data_type)

    return ses_convolve2d_separate(
        input,
        gauss_vectors,
        padding,
        gauss_window_radius,
        tmp_padded_input,
        tmp_col_result,
        out,
        data_type,
        )


def filter(
    input,
    filter_shape,
    sigma,
    padding='pass',
    out=None,
    data_type=float32,
    ):
    """
    This performs a one-shot filtering: *init(...)*, *filter_kernel(...)* and
    *free(...)*
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    filter_shape : (int, int)
        Filter window shape (rows, cols) (must be odd)
    sigma : int
        The sigma value used to generate the `Gaussian window
        <http://en.wikipedia.org/wiki/Gaussian_filter>`_
    padding : str, optional
        How to handle border elements, default is 'pass' as we initialize
        padded input to zero and never touch those elements again.
        Valid paddings: 'pass', 'zero', 'replicate'
    out : ndarray, optional
        Output argument. This must have the exact kind that would be returned
        if it was not used. In particular, it must have the right type, must be
        C-contiguous, and its dtype must be the dtype that would be returned
        for *filter(input, ...)*. This is a performance feature. Therefore, if
        these conditions are not met, an exception is raised, instead of
        attempting to be flexible.
    data_type : data-type, optional
        The precision of the internal data structures needed for the gauss2d
        filtering

    Returns
    -------
    output : ndarray
        2d Gauss filtered version of *input*, 
        if *out* is given, then it is returned,
        if not *output* is created with shape and type equivalent to *input*. 
        
    Raises
    ------
    ValueError
        If *filter_shape* values are even or
        if parameters have the wrong type or
        if the shape and dtype of *input* and *out* don't match each other,
    """

    # Initialize

    init(input.shape, filter_shape, sigma, padding, data_type)

    # Perform filtering

    out = filter_kernel(input, out)

    # Free up resources

    free()

    return out


