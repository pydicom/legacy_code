# pil_handler.py
"""Handler for decompressing pixel data using the PIL or pillow imaging libraries"""
# Copyright (c) 2016 Darcy Mason and pydicom contributors
# This file is part of pydicom, released under a modified MIT license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/darcymason/pydicom

have_jpeg_ls = True
try:
    import jpeg_ls
except ImportError:
    have_jpeg_ls = False

have_pillow = True
try:
    from PIL import Image as PILImg
except ImportError:
    have_pillow = False
    # If that failed, try the alternate import syntax for PIL.
    try:
        import Image as PILImg
    except ImportError:
        # Neither worked, so it's likely not installed.
        have_pillow = False

        
from pydicom.uid import JPEGLossless
from pydicom.uid import JPEGBaseLineLossy8bit, JPEGBaseLineLossy12bit
from pydicom.uid import JPEG2000Lossless, JPEG2000Lossy


PILSupportedCompressedPixelTransferSyntaxes = [JPEGBaseLineLossy8bit,
                                               JPEGLossless,
                                               JPEGBaseLineLossy12bit,
                                               JPEG2000Lossless,
                                               JPEG2000Lossy, ]


def register():
    """Return information about which compressed images are supported, or 
    could be supported with additional libraries
    
    Returns
    =======
    handled: dict
        A list of compressed transfer syntax UIDs that this module can decompress,
        or could with additional libraries installed
        The dictionary is of the form:
            UID: (
        
    could_handle: dict
    """

    def _get_PIL_supported_compressed_pixeldata(self):
        if not have_pillow:
            msg = "The pillow package is required to use pixel_array for this transfer syntax {0}, and pillow could not be imported.".format(self.file_meta.TransferSyntaxUID)
            raise ImportError(msg)
        # decompress here
        if self.file_meta.TransferSyntaxUID in pydicom.uid.JPEGLossyCompressedPixelTransferSyntaxes:
            if self.BitsAllocated > 8:
                raise NotImplementedError("JPEG Lossy only supported if Bits Allocated = 8")
            generic_jpeg_file_header = '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x01\x00\x01\x00\x00'
            frame_start_from = 2
        elif self.file_meta.TransferSyntaxUID in pydicom.uid.JPEG2000CompressedPixelTransferSyntaxes:
            generic_jpeg_file_header = ''
            # generic_jpeg_file_header = '\x00\x00\x00\x0C\x6A\x50\x20\x20\x0D\x0A\x87\x0A'
            frame_start_from = 0
        else:
            generic_jpeg_file_header = ''
            frame_start_from = 0
        try:
            UncompressedPixelData = ''
            if 'NumberOfFrames' in self and self.NumberOfFrames > 1:
                # multiple compressed frames
                CompressedPixelDataSeq = pydicom.encaps.decode_data_sequence(self.PixelData)
                for frame in CompressedPixelDataSeq:
                    data = generic_jpeg_file_header + frame[frame_start_from:]
                    fio = io.BytesIO(data)
                    try:
                        decompressed_image = PILImg.open(fio)
                    except IOError as e:
                        raise NotImplementedError(e.message)
                    UncompressedPixelData += decompressed_image.tobytes()
            else:
                # single compressed frame
                UncompressedPixelData = pydicom.encaps.defragment_data(self.PixelData)
                UncompressedPixelData = generic_jpeg_file_header + UncompressedPixelData[frame_start_from:]
                try:
                    fio = io.BytesIO(UncompressedPixelData)
                    decompressed_image = PILImg.open(fio)
                except IOError as e:
                    raise NotImplementedError(e.message)
                UncompressedPixelData = decompressed_image.tobytes()
        except:
            raise
        return UncompressedPixelData
