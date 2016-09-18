# standard_handler.py
"""Handler for uncompressing pixel data"""
# Copyright (c) 2016 Darcy Mason and pydicom contributors
# This file is part of pydicom, released under a modified MIT license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/darcymason/pydicom

import numpy
   
import sys
sys_is_little_endian = (sys.byteorder == 'little')


def process(ds):
    """Return a numpy array of pixel data for the given dataset.

    Returns:
    -------
    pixel_array: None, or numpy array
                 If unable to process the pixel data, returns None.
    message: str
             If unable to process, a message explaining libraries to install,
             or reason it cannot be processed.
    """


    if ds._is_uncompressed_transfer_syntax():
        return None, "Standard image handler: unable to process compressed images"

    # Make NumPy format code, e.g. "uint16", "int32" etc
    # from two pieces of info:
    #    ds.PixelRepresentation -- 0 for unsigned, 1 for signed;
    #    ds.BitsAllocated -- 8, 16, or 32
    format_str = '%sint%d' % (('u', '')[ds.PixelRepresentation],
                              ds.BitsAllocated)
    try:
        numpy_dtype = numpy.dtype(format_str)
    except TypeError:
        msg = ("Standard image handler: Data type not understood by NumPy: "
               "format='%s', PixelRepresentation=%d, BitsAllocated=%d")
        return None, msg % (format_str, ds.PixelRepresentation,
                        ds.BitsAllocated)

    if ds.is_little_endian != sys_is_little_endian:
        numpy_dtype = numpy_dtype.newbyteorder('S')

    pixel_bytearray = ds.PixelData

    pixel_array = numpy.fromstring(pixel_bytearray, dtype=numpy_dtype)

    # Note the following reshape operations return a new *view* onto pixel_array, but don't copy the data
    if 'NumberOfFrames' in ds and ds.NumberOfFrames > 1:
        if ds.SamplesPerPixel > 1:
            # TODO: Handle Planar Configuration attribute
            assert ds.PlanarConfiguration == 0
            pixel_array = pixel_array.reshape(ds.NumberOfFrames, ds.Rows, ds.Columns, ds.SamplesPerPixel)
        else:
            pixel_array = pixel_array.reshape(ds.NumberOfFrames, ds.Rows, ds.Columns)
    else:
        if ds.SamplesPerPixel > 1:
            if ds.BitsAllocated == 8:
                if ds.PlanarConfiguration == 0:
                    pixel_array = pixel_array.reshape(ds.Rows, ds.Columns, ds.SamplesPerPixel)
                else:
                    pixel_array = pixel_array.reshape(ds.SamplesPerPixel, ds.Rows, ds.Columns)
                    pixel_array = pixel_array.transpose(1, 2, 0)
            else:
                raise NotImplementedError("This code only handles SamplesPerPixel > 1 if Bits Allocated = 8")
        else:
            pixel_array = pixel_array.reshape(ds.Rows, ds.Columns)
    return pixel_array, "Standard image handler: processed successfully"
