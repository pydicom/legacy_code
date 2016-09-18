# jpgls_handler.py
"""Handler for decompressing pixel data using the JPEGLS library"""
# Copyright (c) 2016 Darcy Mason and pydicom contributors
# This file is part of pydicom, released under a modified MIT license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/darcymason/pydicom

# Import nice names for UID values 
from pydicom.uid import JPEGLSLossless, JPEGLSLossy
import pydicom.encaps

# Check for dependencies needed to handle the images
have_jpeg_ls = True
try:
    import jpeg_ls
except ImportError:
    have_jpeg_ls = False


# Set up the information about what images this library can deal with    
# can_handle: list
#       List of UIDs that the library expects to be able to handle, with
#       the *current* state of the system.  If required libraries are not 
#       installed, the uid should NOT be in the can_handle list.
#       Can still raise NotImplementedError if attempt but fail
# could_handle: dict
#       Dictionary of uid: message, where uid is a transfer syntax
#       that could be handled if a dependency were fulfilled.
#       The message line instructs the user what to install or configure
#       to enable the handler to work with the image.
#       The message is only printed if no other handlers are successful.

# Constants to label decompress capability
CANNOT, COULD, CAN = (-1, 0, 1)

# Available syntaxes for this module
my_transfer_syntaxes = [JPEGLSLossless, 
                     JPEGLSLossy, ]

# Message if dependencies needed
could_message = "The CharLS library and the python binding CharPyLs are required to decompress this compression type"


def capability_for(transfer_syntax):
    """Specify whether this module can likely decompress an image of the given type
    
    Returns
    -------
    capability:  int
        -1 if the routine cannot decompress the specified transfer syntax, regardless of dependencies
        0 if it could, but needs additional dependencies installed.  The dependencies are specified in message.
        1 if it most likely *can* decompress the image type without any additional libraries
    message: str
        For the capability=0 case, a descriptive message for the user to know how to activate the capability
        Otherwise message should be blank
    """
    capability = CANNOT
    message = ""
    if transfer_syntax in my_transfer_syntaxes:
        if have_jpeg_ls:
            capability = CAN
        else:
            capability = COULD
            message = could_message
    return capability, message
        

def process(ds):
    """Return the decompressed pixel data for the given dataset"""
    # Throw a warning just in case called even though we said could not handle this syntax
    if not have_jpeg_ls:
        msg = "The jpeg_ls package is required to use pixel_array for transfer syntax {0}, and jpeg_ls could not be imported.".format(ds.file_meta.TransferSyntaxUID)
        raise NotImplementedError(msg)
    # decompress here
    UncompressedPixelData = ''
    if 'NumberOfFrames' in ds and ds.NumberOfFrames > 1:
        # multiple compressed frames
        CompressedPixelDataSeq = pydicom.encaps.decode_data_sequence(ds.RawPixelData)
        for frame in CompressedPixelDataSeq:
            decompressed_image = jpeg_ls.decode(numpy.fromstring(frame, dtype=numpy.uint8))
            UncompressedPixelData += decompressed_image.tobytes()
    else:
        # single compressed frame
        CompressedPixelData = pydicom.encaps.defragment_data(ds.PixelData)
        decompressed_image = jpeg_ls.decode(numpy.fromstring(CompressedPixelData, dtype=numpy.uint8))
        UncompressedPixelData = decompressed_image.tobytes()
    return UncompressedPixelData
