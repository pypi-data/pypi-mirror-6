#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# kernel - http://www.songho.ca/dsp/convolution/convolution.html
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

"""Convolution: http://www.songho.ca/dsp/convolution/convolution.html"""

from numpy import zeros, spacing, sqrt, dot, float32, einsum
from numpy.linalg import svd
from numpy.lib.stride_tricks import as_strided

allowed_padding = {'pass': 0, 'zero': 1, 'replicate': 2}


def pad_input(
    input,
    padding,
    window_radius,
    out=None,
    ):
    """
    Returns padded input data.
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    padding : int
        How to handle border elements {'pass': 0, 'zero': 1, 'replicate': 2}
    window_radius: (int, int)
        Tuple containing the (y, x) radius of the convolution window
    out : ndarray, optional
        A 2-dimensional with the same shape and type 
        as *input*.
        
    Raises
    ------
    ValueError
        If *padding* is unsupported
        
    Returns
    -------
    output : ndarray
       Padded version of *input*
    """

    if out is None:
        out = zeros((input.shape[0] + 2 * window_radius[0],
                    input.shape[1] + 2 * window_radius[1]),
                    dtype=input.dtype)

    # Copy data from input to out

    out[window_radius[0]:-window_radius[0], window_radius[1]:
        -window_radius[1]] = input

    if padding == allowed_padding['pass']:
        pass
    elif padding == allowed_padding['zero']:

        # Top line minus corners

        out[:window_radius[0], window_radius[1]:-window_radius[1]] = 0

        # Bottom line minus corners

        out[-window_radius[0]:, window_radius[1]:-window_radius[1]] = 0

        # Left incl. corners

        out[:, :window_radius[1]] = 0

        # Right incl. corners

        out[:, -window_radius[1]:] = 0
    elif padding == allowed_padding['replicate']:

        # Top line minus corners

        out[:window_radius[0], window_radius[1]:-window_radius[1]] = \
            input[0]

        # Bottom line minus corners

        out[-window_radius[0]:, window_radius[1]:-window_radius[1]] = \
            input[-1]

        # Left incl. corners

        out[:, :window_radius[1]] = out[:, window_radius[1]:
                window_radius[1] + 1]

        # Right incl. corners

        out[:, -window_radius[1]:] = out[:, -window_radius[1] - 1:
                -window_radius[1]]
    else:
        msg = 'Padding: %s _NOT_ supported, valid paddings: %s' \
            % (padding, allowed_padding.keys())
        raise ValueError(msg)
    
    return out


def separate2d(input, data_type=float32):
    """
    `Separate a 2d-matrix convolution filter into two decomposed vectors
    <http://blogs.mathworks.com/steve/2006/11/28/separable-convolution-part-2/>`_
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array representing a convolution window
    out : Two tuple of 1-d ndarrays
        Tuple containing the two convolution vectors obtained by decomposing
        *input* 

    Raises
    ------
    ValueError
        If *input* can't be decomposed into two vectors
    """

    # Singular Value Decomposition
    # NOTE: The convolution window is flipped:
    # http://www.songho.ca/dsp/convolution/convolution.html

    (U, S, V) = svd(input[::-1, ::-1])

    # Check rank of input matrix

    tolerance = max(input.shape) * spacing(max(S))
    rank = sum(S > tolerance)

    if rank != 1:
        msg = \
            'Decomposition error, \
             The number of linearly independent rows or columns are != 1'
        raise ValueError(msg)

    horizontal_vector = V[0] * sqrt(S[0])
    vertical_vector = U[:, 0] * sqrt(S[0])

    return (data_type(vertical_vector), data_type(horizontal_vector))


def convolve2d_separate(
    input,
    window_vectors,
    padding,
    tmp_window_radius=None,
    tmp_padded_input=None,
    tmp_col_result=None,
    out=None,
    data_type=float32,
    ):
    """
    Returns a `2d convoluted array 
    <http://www.songho.ca/dsp/convolution/convolution.html>`_
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    window_vectors: Two tuple of 1-d ndarrays
        Tuple containing the two convolution vectors obtained 
        by `seperating the convolution window matrix <cphhpc.signal.html#cphhpc.signal.convolution.separate2d>`_
    padding : int
        How to handle border elements {'pass': 0, 'zero': 1, 'replicate': 2}
    tmp_window_radius: (int, int), optional
        Tuple containing the (y, x) radius of the convolution window
    tmp_padded_input: ndarray, optional
        A 2-dimensional array with shape (*input.shape* + 2 * *window_radius*)
    tmp_col_result: ndarray, optional
        A 2-dimensional array with shape:
        (input.shape[0], input.shape[1] + 2 * tmp_window_radius[1])
    out : ndarray, optional
        A 2-dimensional convoluted float array with the same shape 
        as *input*.
    data_type : data-type, optional
        The precision of the data structures needed for the convolution
           
    Returns
    -------
    output : ndarray
        2d convoluted version of *input*,
    """

    if tmp_window_radius is None:
        tmp_window_radius = (len(window_vectors[0]) / 2,
                             len(window_vectors[1]) / 2)

    if tmp_col_result is None:
        tmp_col_result = zeros((input.shape[0], input.shape[1] + 2
                               * tmp_window_radius[1]), dtype=data_type)

    if out is None:
        out = zeros(input.shape, dtype=data_type)

    tmp_padded_input = pad_input(input, padding, tmp_window_radius,
                                 out=tmp_padded_input)

    # First calculate dot product of image and Gauss vector
    # along columns (y direction) with radius 'tmp_window_radius[0]'
    # from input pixels

    for y in xrange(tmp_window_radius[0], input.shape[0]
                    + tmp_window_radius[0]):
        start_y = y - tmp_window_radius[0]
        end_y = y + tmp_window_radius[0] + 1

        dot(tmp_padded_input[start_y:end_y].T, window_vectors[0],
            out=tmp_col_result[start_y])

    # Second calculate dot product of the dot products calculated above
    # and Gauss vector along rows (x direction)
    # with radius 'tmp_window_radius[1]' from input pixel

    for x in xrange(tmp_window_radius[1], input.shape[1]
                    + tmp_window_radius[1]):
        start_x = x - tmp_window_radius[1]
        end_x = x + tmp_window_radius[1] + 1

        out[:, start_x] = dot(tmp_col_result[:, start_x:end_x],
                              window_vectors[1])

    return out


def ses_convolve2d_separate(
    input,
    window_vectors,
    padding,
    tmp_window_radius=None,
    tmp_padded_input=None,
    tmp_col_result=None,
    out=None,
    data_type=float32,
    ):
    """
    Returns a `2d convoluted array
    <http://www.songho.ca/dsp/convolution/convolution.html>`_, 
    `using strides and einstein summation
    <http://stackoverflow.com/questions/21743871/how-to-perform-iterative-2d-operation-on-4d-numpy-array>`_
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    window_vectors: Two tuple of 1-d ndarrays
        Tuple containing the two convolution vectors obtained 
        by `seperating the convolution window matrix <cphhpc.signal.html#cphhpc.signal.convolution.separate2d>`_
    padding : int
        How to handle border elements {'pass': 0, 'zero': 1, 'replicate': 2}
    tmp_window_radius: (int, int), optional
        Tuple containing the (y, x) radius of the convolution window
    tmp_padded_input: ndarray, optional
        A 2-dimensional array with shape (*input.shape* + 2 * *window_radius*)
    tmp_col_result: ndarray, optional
        A 2-dimensional array with shape:
        (input.shape[0], input.shape[1] + 2 * tmp_window_radius[1])
    out : ndarray, optional
        A 2-dimensional convoluted float array with the same shape 
        as *input*.
    data_type : data-type, optional
        The precision of the data structures needed for the convolution
           
    Returns
    -------
    output : ndarray
        2d convoluted version of *input*,
    """

    if tmp_window_radius is None:
        tmp_window_radius = (len(window_vectors[0]) / 2,
                             len(window_vectors[1]) / 2)

    if tmp_col_result is None:
        tmp_col_result = zeros((input.shape[0], input.shape[1] + 2
                               * tmp_window_radius[1]), dtype=data_type)

    if out is None:
        out = zeros(input.shape, dtype=data_type)

    tmp_padded_input = pad_input(input, padding, tmp_window_radius,
                                 out=tmp_padded_input)

    window_len_y = len(window_vectors[0])
    window_len_x = len(window_vectors[1])
    window_radius_y = window_len_y / 2
    window_radius_x = window_len_x / 2

    shape = (tmp_padded_input.shape[0] - 2 * window_radius_y,
             tmp_padded_input.shape[1], window_len_y, 1)
    strides = tmp_padded_input.strides * 2

    strided_data = as_strided(tmp_padded_input, shape=shape,
                              strides=strides)

    einsum('ijkl,k->ij', strided_data, window_vectors[0],
           out=tmp_col_result)

    shape = (tmp_padded_input.shape[0] - 2 * window_radius_y,
             tmp_padded_input.shape[1] - 2 * window_radius_x, 1,
             window_len_x)
    strides = tmp_padded_input.strides * 2

    strided_data = as_strided(tmp_col_result, shape=shape,
                              strides=strides)

    einsum('ijkl,l->ij', strided_data, window_vectors[1], out=out)

    return out


def convolve2d(
    input,
    window_matrix,
    padding,
    tmp_window_radius=None,
    tmp_padded_input=None,
    out=None,
    data_type=float32,
    ):
    """
    `Convolve two 2-dimensional arrays
    <http://www.songho.ca/dsp/convolution/convolution.html>`_
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    window_matrix: ndarray
        A 2-dimensional array containing convolution window
    padding : int
        How to handle border elements {'pass': 0, 'zero': 1, 'replicate': 2}
    tmp_window_radius: (int, int)
        Tuple containing the (y, x) radius of the convolution window
    tmp_padded_input: ndarray
        A 2-dimensional array with shape (*input.shape* + 2 * *tmp_window_radius*)
    out : ndarray, optional
        A 2-dimensional convoluted float array with the same shape
        as *input*.
    data_type : data-type, optional
        The precision of the data structures needed for the convolution
           
    Returns
    -------
    output : ndarray
        2d convoluted version of *input*,
    """

    if tmp_window_radius is None:
        tmp_window_radius = (window_matrix.shape[0] / 2,
                             window_matrix.shape[1] / 2)

    if out is None:
        out = zeros(input.shape, dtype=data_type)
    else:
        out[:] = data_type(0.0)

    tmp_padded_input = pad_input(input, padding, tmp_window_radius,
                                 out=tmp_padded_input)

    start_y = tmp_window_radius[0] * 2
    end_y = tmp_padded_input.shape[0]

    for y in xrange(window_matrix.shape[0]):
        start_x = tmp_window_radius[1] * 2
        end_x = tmp_padded_input.shape[1]

        for x in xrange(window_matrix.shape[1]):
            tmp = tmp_padded_input * window_matrix[y][x]
            out += tmp[start_y:end_y, start_x:end_x]

            start_x -= 1
            end_x -= 1

        start_y -= 1
        end_y -= 1

    return out


def ses_convolve2d(
    input,
    window_matrix,
    padding,
    tmp_window_radius=None,
    tmp_padded_input=None,
    out=None,
    data_type=float32,
    ):
    """
    `Convolve two 2-dimensional arrays
    <http://www.songho.ca/dsp/convolution/convolution.html>`_,
    `using strides and einstein summation
    <http://stackoverflow.com/questions/21743871/how-to-perform-iterative-2d-operation-on-4d-numpy-array>`_
        
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    window_matrix: ndarray
        A 2-dimensional array containing convolution window
    padding : int
        How to handle border elements {'pass': 0, 'zero': 1, 'replicate': 2}
    tmp_window_radius: (int, int)
        Tuple containing the (y, x) radius of the convolution window
    tmp_padded_input: ndarray
        A 2-dimensional array with shape (*input.shape* + 2 * *tmp_window_radius*)
    out : ndarray, optional
        A 2-dimensional convoluted float array with the same shape
        as *input*.
    data_type : data-type, optional
        The precision of the data structures needed for the convolution
           
    Returns
    -------
    output : ndarray
        2d convoluted version of *input*,
    """

    if tmp_window_radius is None:
        tmp_window_radius = (window_matrix.shape[0] / 2,
                             window_matrix.shape[1] / 2)

    if out is None:
        out = zeros(input.shape, dtype=data_type)

    tmp_padded_input = pad_input(input, padding, tmp_window_radius,
                                 out=tmp_padded_input)

    window_matrix = window_matrix[::-1, ::-1]
    window_len_y = len(window_matrix[0])
    window_len_x = len(window_matrix[1])
    window_radius_y = window_len_y / 2
    window_radius_x = window_len_x / 2

    shape = (tmp_padded_input.shape[0] - 2 * window_radius_y,
             tmp_padded_input.shape[1] - 2 * window_radius_x,
             window_len_y, window_len_x)
    strides = tmp_padded_input.strides * 2

    strided_data = as_strided(tmp_padded_input, shape=shape,
                              strides=strides)

    return einsum('ijkl,kl->ij', strided_data, window_matrix, out=out)


