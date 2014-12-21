# classes.py
"""Classes for Information Object Definitions"""
# Copyright (c) 2014 Darcy Mason
# This file is part of pydicom, released under a modified MIT license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/darcymason/pydicom
#

import inspect

from pydicom import datadict
from pydicom.tag import Tag
from pydicom.dataelem import DataElement



class IOD(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        # Get list of methods with this instance, to match tags to
        self.props = dict((name, propobj) 
                 for (name, propobj)
                 in inspect.getmembers(ImagePixelModule, inspect.isdatadescriptor)
                 if not name.startswith("_")
                )
    def get_item(self, ds, tag, data_elem):
        """Called from Dataset when it has been asked to get an item
        that this module "owns"
        """
        keyword = datadict.keyword_for_tag(tag)
        prop = self.props.get(keyword, None)
        if prop:
            value = prop.fget(self, ds, tag, data_elem)
            return DataElement(tag, data_elem.VR, value)
        else:
            # This class not handling it, return it unchanged
            return data_elem
    
    def set_item(self, ds, tag, data_elem):
        keyword = datadict.keyword_for_tag(tag)
        prop = self.props.get(keyword, None)
        if prop:
            value = prop.fget(self, ds, tag, data_elem)
            data_elem = DataElement(tag, data_elem.VR, value)
        ds.__dict__[tag] = data_elem


    def tags(self):
        return self.keys()
        
    def __str__(self):
        tags = sorted(self.keys())
        format_str = "{0}:  Type {1}  {2}" 
        tuples = [(Tag(tag), self[tag][0], datadict.keyword_for_tag(tag))
                  for tag in tags]
                  
        return "\n".join(format_str.format(*tup) for tup in tuples)
        

class Module(IOD):
    pass

    
class Macro(IOD):
    pass

class ImagePixelModule(IOD):
    """Handle all pixel data elements. Defined in dicom standard PS3 C.7.11-a
    """
    
    @property
    def PixelData(self, ds, tag, data_elem):
        if hasattr(ds, "_pixel_array"):
            return ds._pixel_array
        else:
            return dict.__getitem__(ds, tag).value    
        
    @property
    def Rows(self, ds, tag, data_elem):
        if hasattr(ds, "_pixel_array"):
            return ds.pixel_array.shape[0]  # XXX need to work out all multi-frame variations etc.
        else:
            return dict.__getitem__(ds, tag).value



if __name__ == "__main__":
    from pydicom.iod.macros.image import image_pixel_macro_attributes
    from pydicom import dicomio
    
    m = ImagePixelModule(image_pixel_macro_attributes)
    ds = dicomio.read_file("../../tests/test_files/CT_small.dcm")
    print("Rows before..:", ds.Rows)
    ds.register_module(m)
    ds.pixel_array
    ds.PixelData.shape = (64, 128*2)
    print("Numpy array new shape..:", ds.pixel_array.shape)
    print("Rows after..:", ds.Rows)
    