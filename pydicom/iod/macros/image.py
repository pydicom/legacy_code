# image.py
"""Image Pixel Macro definition"""

from pydicom import iod

image_pixel_macro_attributes = {
    # tag: (Type, ...)
    0x00280002: ('1',),  # Samples per Pixel
    0x00280004: ('1',),  # Photometric Interpretation
    0x00280010: ('1',),  # Rows
    0x00280011: ('1',),  # Cols
    0x7fe00010: ('1',),  # PixelData
    # ... XXX need to fill in more...
    }

