#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# convolve2d - Generic 2-dimensional convolution
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

"""Generic 2-dimensional numpy convolution"""

from numpy import zeros, float32
from cphhpc.signal.convolution.kernels import allowed_padding, \
    separate2d, ses_convolve2d_separate, ses_convolve2d

# Globals

_cache = {}


def init(
    input_shape,
    window,
    padding='pass',
    data_type=float32,
    convolve_id='oneshot',
    ):
    """
    Initializes the data structures needed for the 2d convolution
    
    Parameters
    ----------
    input_shape : (int, int)
        Shape of input (rows, cols)
    window : ndarray
        A 2-dimensional convolution window with shape (rows, cols) where both
        must be odd
    padding : str, optional
        How to handle boarder elements, default is 'pass' as we initialize
        padded input to zero and never touch those elements again.
        Valid paddings: 'pass', 'zero', 'replicate'
    data_type : data-type, optional
        The precision of the data structures needed for the 2d convolution
    convolve_id : str, optional
        Used to identify cache settings for different convolutions
                
    Raises
    ------
    ValueError
        If *window.shape* values are even or 
        if parameters have the wrong type
    """

    # Check parameter types

    if type(input_shape) != tuple or len(input_shape) != 2 \
        or type(input_shape[0]) != int or type(input_shape[1]) != int:
        msg = 'input_shape: %s is _NOT_ a two-tuple of integers' \
            % str(input_shape)
        raise ValueError(msg)

    if len(window.shape) != 2 or window.shape[0] % 2 == 0 \
        or window.shape[1] % 2 == 0:
        msg = \
            'window shape %s must be two dimentional with odd dimensions' \
            % str(window.shape)
        raise ValueError(msg)

    if not padding in allowed_padding:
        msg = 'Padding: %s _NOT_ supported, valid paddings: %s' \
            % (padding, allowed_padding.keys())
        raise ValueError(msg)

    # Init cache

    if _cache.has_key(convolve_id):
        _cache[convolve_id].clear()
    else:
        _cache[convolve_id] = {}

    cache = _cache[convolve_id]

    cache['input_shape'] = input_shape

    cache['window_matrix'] = window
    cache['window_radius'] = (window.shape[0] / 2, window.shape[1] / 2)

    cache['padded_shape'] = (input_shape[0] + 2 * cache['window_radius'
                             ][0], input_shape[1] + 2
                             * cache['window_radius'][1])

    cache['padding'] = allowed_padding[padding]

    cache['tmp_padded_input'] = zeros(cache['padded_shape'],
            dtype=data_type)

    # Try to seperate window into vectors

    cache['colvolve_window'] = window
    try:
        cache['convolve_vectors'] = separate2d(window, data_type)
    except ValueError:

        cache['convolve_vectors'] = None

    cache['tmp_col_result'] = None
    if cache['convolve_vectors'] is not None:
        cache['tmp_col_result'] = zeros((cache['input_shape'][0],
                cache['padded_shape'][1]), dtype=data_type)

    cache['data_type'] = data_type


def free(convolve_id='oneshot'):
    """
    Free up the internal data structures needed for the 2d convolution
    
    Parameters
    ----------
    convolve_id : str, optional
        Used to identify cache settings needed for the 2d convolution
    """

    if _cache.has_key(convolve_id):
        _cache[convolve_id].clear()
        del _cache[convolve_id]


def convolve2d_kernel(input, out=None, convolve_id='oneshot'):
    """
    Returns a 2d convoluted array based on `convolution
    <http://www.songho.ca/dsp/convolution/convolution.html>`_.
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    out : ndarray, optional
        Output argument. This must have the exact kind that would be returned
        if it was not used. In particular, it must have the right type, must be
        C-contiguous, and its dtype must be the dtype that would be returned
        for *convolve2d_kernel(input, ...)*. This is a performance feature.
        Therefore, if these conditions are not met, an exception is raised,
        instead of attempting to be flexible.
    convolve_id : str, optional
        Used to identify cache settings for different convolutions
           
    Returns
    -------
    output : ndarray
        2d convoluted version of *input*,
        if *out* is given, then it is returned.
        if not *output* is created with shape and type equivalent to *input*. 
        
    Raises
    ------
    ValueError
        If convolve2d wasn't initialized or if the shape of *input*
        doesn't match the one given to the init function or if the shape and
        dtype of *input* and *out* don't match.
    """

    if _cache.has_key(convolve_id):
        cache = _cache[convolve_id]
    else:
        msg = 'convolve2d is not initialized with convolve_id: %s' \
            % convolve_id
        raise ValueError(msg)

    input_shape = cache['input_shape']
    tmp_padded_input = cache['tmp_padded_input']
    window_matrix = cache['window_matrix']
    window_radius = cache['window_radius']
    padding = cache['padding']
    tmp_col_result = cache['tmp_col_result']
    convolve_vectors = cache['convolve_vectors']
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

    if convolve_vectors is not None:
        result = ses_convolve2d_separate(
            input,
            convolve_vectors,
            padding,
            window_radius,
            tmp_padded_input,
            tmp_col_result,
            out,
            data_type,
            )
    else:
        result = ses_convolve2d(
            input,
            window_matrix,
            padding,
            window_radius,
            tmp_padded_input,
            out,
            data_type,
            )

    return result


def convolve2d(
    input,
    window,
    padding='pass',
    out=None,
    data_type=float32,
    ):
    """
    This performs a one-shot 2d convolution: *init(...)*, *convolve2d(...)* and
    *free(...)*
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    window : ndarray
        A 2-dimensional convolution window
    padding : str, optional
        How to handle border elements, default is 'pass' as we initialize
        padded input to zero and never touch those elements again.
        Valid paddings: 'pass', 'zero', 'replicate'
    out : ndarray, optional
        Output argument. This must have the exact kind that would be returned
        if it was not used. In particular, it must have the right type, must be
        C-contiguous, and its dtype must be the dtype that would be returned
        for *convolve2d(input, ...)*. This is a performance feature. Therefore,
        if these conditions are not met, an exception is raised, instead of
        attempting to be flexible.
    data_type : data-type, optional
        The precision of the internal data structures needed for the 2d
        convolution

    Returns
    -------
    output : ndarray
        2d convoluted version of *input*, 
        if *out* is given, then it is returned,
        if not *output* is created with shape and type equivalent to *input*. 
        
    Raises
    ------
    ValueError
        If *window.shape* values are even or
        if parameters have the wrong type or
        if the shape and dtype of *input* and *out* don't match each other,
    """

    # Initialize

    init(input.shape, window, padding, data_type)

    # Perform convolution

    out = convolve2d_kernel(input, out)

    # Free up resources

    free()

    return out


