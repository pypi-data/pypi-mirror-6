#!/usr/bin/env python
'''
COPYRIGHT 2013 RPS ASA

This file is part of  Petulant Bear.

    Petulant Bear is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Petulant Bear is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Petulant Bear.  If not, see <http://www.gnu.org/licenses/>.

@author David Stuebe <dstuebe@asasscience.com>
@file netcdf_etree.py
@date 07/16/13
@description Provides a parser method which uses a set of custom element classes to create
a lxml tree which allows the user to query and modify a NetCDF4 dataset using the lxml 
interface.
'''

import cStringIO
from lxml import etree
from netcdf2ncml import *

namespaces = {NCML:NAMESPACE}

class NetcdfEtreeException(Exception):
    """
    An exception class for NetCDF etree wrappers
    """

class NcDimAttrib(etree._Attrib):
    
    def __init__(self, *args, **kwargs):
        self._nc_element = args[0]
        self._nc_obj = args[0]._nc_obj
        super(NcDimAttrib, self).__init__(*args,**kwargs)
    
    def __setitem__(self, key, value):

        nc_object = self._nc_obj
        if nc_object is None:
            raise NetcdfEtreeException('Internal Error: No nc_obj available!')  

        if key == NAME:
            # renameDimension(Old value, New Value)
            nc_object.renameDimension(self[NAME], value)
        elif key == LENGTH:
            raise NetcdfEtreeException('''The legth of the dimension "{}" can not be modified in a NetCDF4 Python Dataset'''.format(self[NAME]))
        elif key == ISUNLIMITED:
            raise NetcdfEtreeException('''The nature of the dimension "{}" can not be changed once it is created as limited or unlimited in a NetCDF4 Python Dataset'''.format(self[NAME]))
        else:
            raise NetcdfEtreeException('''The key "{}" is not part of the schema for NcML Dimensions'''.format(key))

        super(NcDimAttrib, self).__setitem__(key, value)

    def __delitem__(self, key):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be deleted from the a NetCDF4 Python Dataset''')

    def update(self, dct):
        for key, value in dct.iteritems():
            self[key] = value

    def pop(self, key, *default):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be popped from a NetCDF4 Python Dataset''')

    def clear(self):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be cleared from a NetCDF4 Python Dataset''')

class NcGrpAttrib(etree._Attrib):
    
    def __init__(self, *args, **kwargs):
        self._nc_element = args[0]
        self._nc_obj = args[0]._nc_obj
        super(NcGrpAttrib, self).__init__(*args,**kwargs)
    
    def __setitem__(self, key, value):

        nc_object = self._nc_obj
        if nc_object is None:
            raise NetcdfEtreeException('Internal Error: No nc_obj available!')  

        if key == NAME:
            raise NetcdfEtreeException('''The name of the group "{}" can not be modified in a NetCDF4 Python Dataset'''.format(self[NAME]))
        else:
            raise NetcdfEtreeException('''The key "{}" is not part of the schema for NcML Groups'''.format(key))

        super(NcGrpAttrib, self).__setitem__(key, value)

    def __delitem__(self, key):
        raise NetcdfEtreeException('''Group attributes can not be deleted from the a NetCDF4 Python Dataset''')

    def update(self, dct):
        for key, value in dct.iteritems():
            self[key] = value

    def pop(self, key, *default):
        raise NetcdfEtreeException('''Group attributes can not be popped from a NetCDF4 Python Dataset''')

    def clear(self):
        raise NetcdfEtreeException('''Group attributes can not be cleared from a NetCDF4 Python Dataset''')



class NcVarAttrib(etree._Attrib):
    
    def __init__(self, *args, **kwargs):
        self._nc_element = args[0]
        self._nc_obj = args[0]._nc_obj
        super(NcVarAttrib, self).__init__(*args,**kwargs)
    
    def __setitem__(self, key, value):

        nc_object = self._nc_obj
        if nc_object is None:
            raise NetcdfEtreeException('Internal Error: No nc_obj available!')  

        if key == NAME:
            # renameVariable(Old value, New Value) is a method of the group containing the variable
            nc_object.group().renameVariable(self[NAME], value)
        elif key == SHAPE:
            raise NetcdfEtreeException('''The shape of the variable "{}" can not be modified in a NetCDF4 Python Dataset'''.format(self[NAME]))
        elif key == ISUNLIMITED:
            raise NetcdfEtreeException('''The type of the variable "{}" can not be changed once it is created as in a NetCDF4 Python Dataset'''.format(self[NAME]))
        else:
            raise NetcdfEtreeException('''The key "{}" is not part of the schema for NcML Variables'''.format(key))

        super(NcVarAttrib, self).__setitem__(key, value)

    def __delitem__(self, key):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be deleted from the a NetCDF4 Python Dataset''')

    def update(self, dct):
        for key, value in dct.iteritems():
            self[key] = value

    def pop(self, key, *default):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be popped from a NetCDF4 Python Dataset''')

    def clear(self):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be cleared from a NetCDF4 Python Dataset''')




class NcAttrAttrib(etree._Attrib):
    
    def __init__(self, *args, **kwargs):
        self._nc_element = args[0]
        self._nc_obj = args[0]._nc_obj
        super(NcAttrAttrib, self).__init__(*args,**kwargs)
    
    def __setitem__(self, key, value):

        nc_object = self._nc_obj
        if nc_object is None:
            raise NetcdfEtreeException('Internal Error: No nc_obj available!')  

        current_attr_name = self[NAME]

        if key == NAME:
            # change the name of an existing attribute
            new_attr_name = value
            current_attr_value = nc_object.getncattr(current_attr_name)
            nc_object.setncattr(new_attr_name, current_attr_value)
            nc_object.delncattr(current_attr_name)
        elif key == VALUE:
            # Set the value of an existing attribute without changing its type
            current_type = type(nc_object.getncattr(current_attr_name))
            try:
                new_value = current_type(value)
            except ValueError, TypeError:
                raise NetcdfEtreeException('''Can not cast the new value "{}" (type: {}) of the attribute "{}" to the current type "{}"'''.format(value, type(value), current_attr_name, current_type))
            nc_object.setncattr(current_attr_name, new_value)
        elif key == TYPE:
            current_value = nc_object.getncattr(current_attr_name)
            try:
                new_type = inverse_type_map[value]
            except KeyError:
                raise NetcdfEtreeException('''Unknown new type "{}" specified for attribute "{}"'''.format(value, current_attr_name))
            
            try:
                new_value = new_type(current_value)
            except ValueError, TypeError:
                raise NetcdfEtreeException('''Can not cast the current value "{}" (type: {}) of the attribute "{}" to the new type "{}"'''.format(current_value, type(current_value), current_attr_name, new_type))
                
            nc_object.setncattr(current_attr_name, new_value)
            
            # Make sure to change the representation of the value to be consistent with the new type
            super(NcAttrAttrib, self).__setitem__(VALUE, unicode(new_value))
            
        else:
            raise NetcdfEtreeException('''The key "{}" is not part of the schema for NcML Attributes'''.format(key))

        super(NcAttrAttrib, self).__setitem__(key, value)
        

    def __delitem__(self, key):
        raise NetcdfEtreeException('''NcML Attribute attributes can not be deleted from a NetCDF4 Python Dataset''')

    def update(self, dct):
        for key, value in dct.iteritems():
            self[key] = value

    def pop(self, key, *default):
        raise NetcdfEtreeException('''NcML Attribute attributes can not be popped from a NetCDF4 Python Dataset''')

    def clear(self):
        raise NetcdfEtreeException('''NcML Attribute attributes can not be cleared from a NetCDF4 Python Dataset''')




class NetcdfElement(etree.ElementBase):
    """
    Must define a Python class extending from etree cython so that we can set attributes 
    """
        
    def remove(self, element):
        
        if not element.tag.endswith(ATTRIBUTE):
            raise NetcdfEtreeException('''You can not remove a "{}", only Attributes can be removed from a NetCDF4 Python Dataset (not Groups, Variables or Dimensions)'''.format(element.tag))
        
        # Remove the attribute from the NC Dataset
        name_att = element.get(NAME)
        self._nc_obj.delncattr(name_att)
           
        # now remove it from the element
        super(NetcdfElement, self).remove(element)
                
class VariableElement(NetcdfElement):
    def _init(self):
        name_att = self.get(NAME) # use get interface during init because self._nc_obj is not set yet
        if name_att is None:
            raise NetcdfEtreeException('''Can not create a VariableElement with no name attribute!''')
        
        pobj = self.getparent()._nc_obj
        
        try:
            var = pobj.variables[name_att]
        except KeyError:
            # if it is not there, try to create it!
            shape_att = self.get(SHAPE)
            if shape_att is None:
                raise NetcdfEtreeException('''Can not create a new NetCDF Variable "{}" with no shape attribute!'''.format(name_att))
            
            dimensions = tuple(shape_att.split())
            
            type_att = self.get(TYPE)
            if type_att is None:
                raise NetcdfEtreeException('''Can not create a new NetCDF Variable "{}" with no type attribute!'''.format(name_att))
                
            var = pobj.createVariable(varname=name_att, datatype=inverse_type_map[type_att], dimensions=dimensions)
            
        self._nc_obj = var
        
    @property 
    def attrib(self):
        return NcVarAttrib(self)
        
    def set(self,key,value):
        self.attrib[key] = value
        
        
        
class GroupElement(NetcdfElement):
    def _init(self):
        name_att = self.get(NAME) # use get interface during init because self._nc_obj is not set yet
        pobj = self.getparent()._nc_obj
        grp = pobj.groups[name_att]
        self._nc_obj = grp

    @property 
    def attrib(self):
        return NcGrpAttrib(self)
        
    def set(self,key,value):
        self.attrib[key] = value


class DimensionElement(etree.ElementBase):
    def _init(self):
        parent = self.getparent()
        self._nc_obj = parent._nc_obj

    @property 
    def attrib(self):
        return NcDimAttrib(self)
        
    def set(self,key,value):
        self.attrib[key] = value
                
        
class AttributeElement(etree.ElementBase):
    def _init(self):
        parent = self.getparent()
        self._nc_obj = parent._nc_obj
        
        name_att = self.get(NAME) # use get interface during init because self._nc_obj is not set yet
        if name_att is None:
            raise NetcdfEtreeException('''Can not create a AttributeElement with no name attribute!''')
        
        
        try:
            self._nc_obj.getncattr(name_att)
        except AttributeError:
            type_att = self.get(TYPE,'char')
        
            value_att = self.get(VALUE)
            if value_att is None:
                raise NetcdfEtreeException('''Can not create a new NetCDF Attribute "{}" with no value!'''.format(name_att))
        
            new_type = inverse_type_map[type_att]
            self._nc_obj.setncattr(name_att, new_type(value_att))

    @property 
    def attrib(self):
        return NcAttrAttrib(self)
        
    def set(self,key,value):
        self.attrib[key] = value
        

class ValuesElement(etree.ElementBase):
    def _init(self):
        parent = self.getparent()
        self._nc_obj = parent._nc_obj
    
        default_threshold = numpy.get_printoptions().get('threshold',1000)
        numpy.set_printoptions(threshold=1000000)
        text = numpy.array2string(self._nc_obj[:].flatten(),separator=' ',max_line_width=numpy.Inf)
        numpy.set_printoptions(threshold=default_threshold)
        
        self.text = text[1:-1] # cut off the leading/trailing brackets

    @property 
    def text(self):
        return super(ValuesElement, self).text
        
    @text.setter
    def set_text(self, value):
        self._nc_obj[:] = numpy.array(text.split(),dtype=self._nc_obj.dtype)
        super(ValuesElement, self).text = value
    




class NetCDFLookup(etree.CustomElementClassLookup):

    _lookup = {
        NETCDF      : NetcdfElement,
        VARIABLE    : VariableElement,
        DIMENSION   : DimensionElement,
        ATTRIBUTE   : AttributeElement,
        GROUP       : GroupElement,
        VALUES      : ValuesElement
        }


    def lookup(self, node_type, document, namespace, name):        
        return NetCDFLookup._lookup.get(name)
        
        
def parse_nc_dataset_as_etree(dataset):

    parser = etree.XMLParser()
    parser.set_element_class_lookup(NetCDFLookup())

    xml_etree = None
    output = cStringIO.StringIO()
    try:
        dataset2ncml_buffer(dataset,output)
        output.reset()
        xml_etree = etree.parse(output, parser)
    finally:
        output.close()

    root = xml_etree.getroot()
    
    root._nc_obj = dataset
    
    return root
    
    
    
