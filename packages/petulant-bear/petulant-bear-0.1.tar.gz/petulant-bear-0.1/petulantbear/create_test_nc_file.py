from netCDF4 import Dataset

import numpy

rootgrp = Dataset('test.nc','w')


### Create some groups
group1 = rootgrp.createGroup('g1')
group2 = rootgrp.createGroup('g2')
group3 = rootgrp.createGroup('really_long group_name')

# a nested group
group2_1 = group2.createGroup('g2_1')


### Create some dimensions
# unlimited
dim1 = rootgrp.createDimension('bad_name', None)
dim2 = rootgrp.createDimension('good_name', None)

# limited
dim3 = rootgrp.createDimension('funny_dim_name?!@#$%^&*()_-+""{}', 3)
dim4 = rootgrp.createDimension('dim4', 4)

# in other groups
g1_dim1 = group1.createDimension('same_dim', 1)
g1_dim2 = group1.createDimension('diff_dim', None)

# Should be allowed to use the same name in a different part of the tree?
g2_1_dim1 = group2_1.createDimension('same_dim', 3)
g2_1_dim2 = group2_1.createDimension('diff_dim', None)


### Create some attributes

att_dict = {
    'foo'           : 'bar',
    'foo_byte'      : numpy.iinfo(numpy.int8).max,
    'foo_short'     : numpy.iinfo(numpy.int16).max,
    'foo_int'       : numpy.iinfo(numpy.int32).max,
    'foo_float'     : numpy.float32(numpy.pi),
    'foo_long'      : numpy.iinfo(numpy.int64).max,
    'foo_double'    : numpy.float64(numpy.pi),
    'foo funny name': 'fun string?!@#$%^<>&*()_-+""{}'
}

rootgrp.setncatts(att_dict)
#create some attributes in a group
group3.setncatts(att_dict)


### Create some variables (with atts)

def add_vars_to_grp(grp,types, **kwargs):
    v = grp.createVariable(kwargs.get('var1','var1'),numpy.int8)
    v[:] = numpy.int8(8)
    v.foo = 'bar'
    
    v = grp.createVariable(kwargs.get('var2','var2'),numpy.int8, (dim3._name,), fill_value=5)
    v[:] = numpy.int8(8)
    v.foo = 'bar'
    
    v = grp.createVariable(kwargs.get('var3','var3'),numpy.int8, (dim1._name,dim4._name,))
    v[:] = numpy.arange(8,dtype=numpy.int8).reshape(2,4)
    v.foo = 'bar'
    
    v = grp.createVariable(kwargs.get('var4','var4'),'S1', (dim1._name,dim4._name,))
    #v[:] = numpy.ndarray(8,dtype='S1').reshape(2,4)
    v[:] = 'a'
    v.foo = 'bar'
    
    for num,type in enumerate(types):    
        default_name = 'var{}'.format(num+5)
        print default_name
        v = grp.createVariable(kwargs.get(default_name,default_name),type, (dim4._name,))
        try:
            v[:] = numpy.iinfo(type).max
            continue
        except ValueError:
            pass
        try:
            for i,c in enumerate('char'):
                v[i] = c 
            continue
        except ValueError:
            pass
       
        v[:] = numpy.pi
 
        
    
types = [numpy.int8,numpy.int16,numpy.int32,numpy.int64,numpy.float32,numpy.float64,'S1']

add_vars_to_grp(rootgrp,types)

add_vars_to_grp(group1,types,var1='foobar',var2='moobar',var3='long funny name!@#$%<>^&*()_=+""{}')
add_vars_to_grp(group2_1,types)

# Make a var using nested dimensions...
v = group2_1.createVariable('crazy_dims',numpy.int8, (dim1._name,dim2._name,dim3._name,g2_1_dim1._name), fill_value=5)


rootgrp.close()
