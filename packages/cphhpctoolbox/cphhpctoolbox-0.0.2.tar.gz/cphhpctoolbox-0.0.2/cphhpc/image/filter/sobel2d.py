#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# sobel2d - Sobel 2-dimensional convolution filter
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

"""Sobel 2-dimensional numpy convolution filter"""

from numpy import array, zeros, sqrt, float32

from cphhpc.signal.convolution.kernels import allowed_padding, \
    separate2d, ses_convolve2d_separate

# Globals

_cache = {}


def init(
    input_shape,
    padding='pass',
    data_type=float32,
    sobel_id='oneshot',
    ):
    """
    Initializes the data structures needed for the sobel2d filtering
    
    Parameters
    ----------
    input_shape : (int, int)
        Shape of input (rows, cols)
    padding : str, optional
        How to handle boarder elements, default is 'pass' as we initialize
        padded input to zero and never touch those elements again.
        Valid paddings: 'pass', 'zero', 'replicate'
    data_type : data-type, optional
        The precision of the data structures needed for the sobel2d filtering
    sobel_id : str, optional
        Used to identify cache settings for different sobel2d filteres
    """

    # Check parameter types

    if type(input_shape) != tuple or len(input_shape) != 2 \
        or type(input_shape[0]) != int or type(input_shape[1]) != int:
        msg = 'input_shape: %s is _NOT_ a two-tuple of integers' \
            % str(input_shape)
        raise ValueError(msg)

    if not padding in allowed_padding:
        msg = 'Padding: %s _NOT_ supported, valid paddings: %s' \
            % (padding, allowed_padding.keys())
        raise ValueError(msg)

    # Init cache

    if _cache.has_key(sobel_id):
        _cache[sobel_id].clear()
    else:
        _cache[sobel_id] = {}

    cache = _cache[sobel_id]

    sobel_matrices = _generate_sobel_matrices(data_type)

    cache['sobel_vectors'] = (separate2d(sobel_matrices[0]),
                              separate2d(sobel_matrices[1]))

    cache['sobel_window_radius'] = (1, 1)

    cache['input_shape'] = input_shape

    cache['padded_shape'] = (input_shape[0] + 2
                             * cache['sobel_window_radius'][0],
                             input_shape[1] + 2
                             * cache['sobel_window_radius'][1])

    cache['padding'] = allowed_padding[padding]

    cache['tmp_padded_input'] = zeros(cache['padded_shape'],
            dtype=data_type)

    cache['tmp_col_result'] = zeros((cache['input_shape'][0],
                                    cache['padded_shape'][1]),
                                    dtype=data_type)

    cache['sobel_y'] = zeros(cache['input_shape'], dtype=data_type)
    cache['sobel_x'] = zeros(cache['input_shape'], dtype=data_type)

    cache['data_type'] = data_type


def free(sobel_id='oneshot'):
    """
    Free up the internal data structures needed for the sobel2d filtering

    Parameters
    ----------
    sobel_id : str, optional
        Used to identify cache settings for different sobel2d filteres
    """

    if _cache.has_key(sobel_id):
        _cache[sobel_id].clear()
        del _cache[sobel_id]


def _generate_sobel_matrices(data_type=float32):
    """
    Returns a Sobel filter matrix:
    http://en.wikipedia.org/wiki/Sobel_operator
    
    Parameters
    ----------
    data_type : data-type, optional
       The precision of the data structures needed for the sobel2d filtering

    Returns
    -------
    output : Two tuple of ndarrays
        sobel2d (horizontal,vertical) convolution matrices
        with the given data_type.

    """

    sobel_window_y = array([[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0,
                           2.0, 1.0]]).astype(data_type)

    sobel_window_x = array([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0,
                           0.0, 1.0]]).astype(data_type)

    return (sobel_window_y, sobel_window_x)


def filter_kernel(input, out=None, sobel_id='oneshot'):
    """
    Returns a 2d Sobel filtered array based on `convolution
    <http://www.songho.ca/dsp/convolution/convolution.html>`_.
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    out : ndarray, optional
        Output argument. This must have the exact kind that would be returned
        if it was not used. In particular, it must have the right type, must be
        C-contiguous, and its dtype must be the dtype that would be returned
        for *filter_kernel(input)*. This is a performance feature. Therefore,
        if these conditions are not met, an exception is raised, instead of
        attempting to be flexible.
    sobel_id : str, optional
        Used to identify cache settings for different sobel2d filteres
           
    Returns
    -------
    output : ndarray
        2d Sobel filtered version of *input*, 
        if *out* is given, then it's returned, if not *output* is created with
        shape and type equivalent to *input*. 
        
    Raises
    ------
    ValueError
        If sobel2d wasn't initialized or if the shape of *input*
        doesn't match the one given to the init function or
        if the shape of *input* and *out* don't match.
    """

    if _cache.has_key(sobel_id):
        cache = _cache[sobel_id]
    else:
        msg = 'sobel2d is not initialized with sobel_id: %s' % sobel_id
        raise ValueError(msg)

    input_shape = cache['input_shape']
    tmp_padded_input = cache['tmp_padded_input']
    sobel_vectors = cache['sobel_vectors']
    sobel_window_radius = cache['sobel_window_radius']
    padding = cache['padding']
    tmp_col_result = cache['tmp_col_result']
    sobel_y = cache['sobel_y']
    sobel_x = cache['sobel_x']
    data_type = cache['data_type']

    # If pre-allocated output matrix provided, check shape and types

    if input.shape != input_shape:
        msg = 'input.shape: %s differs from init shape %s' \
            % (str(input.shape), str(input_shape))
        raise ValueError(msg)

    if out is not None:
        if out.shape != input_shape:
            msg = 'out.shape: %s differs from init shape %s' \
                % (str(out.shape), str(input_shape))
            raise ValueError(msg)
    else:

        # If no pre-allocated output matrix provided, allocate data

        out = zeros(input.shape, dtype=data_type)

    sobel_y = ses_convolve2d_separate(
        input,
        sobel_vectors[0],
        padding,
        sobel_window_radius,
        tmp_padded_input,
        tmp_col_result,
        sobel_y,
        data_type,
        )

    sobel_x = ses_convolve2d_separate(
        input,
        sobel_vectors[1],
        padding,
        sobel_window_radius,
        tmp_padded_input,
        tmp_col_result,
        sobel_x,
        data_type,
        )

    out[:] = sqrt(sobel_y ** 2 + sobel_x ** 2)

    return out


def filter(
    input,
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
    padding : str, optional
        How to handle boarder elements, default is 'pass' as we initialize
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
       The precision of the data structures needed for the sobel2d filtering

    Returns
    -------
    output : ndarray
        2d Sobel filtered version of *input*, 
        if *out* is given, then it's returned, if not *output* is created with
        shape and type equivalent to *input*. 
    """

    # Initialize

    init(input.shape, padding, data_type)

    # Perform filtering

    out = filter_kernel(input, out)

    # Free up resources

    free()

    return out


