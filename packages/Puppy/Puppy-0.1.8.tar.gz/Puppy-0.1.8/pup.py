from datetime import datetime

import numpy


class Dimension(object):
    def __init__(self, length):
        self.length = length


class Variable(object):
    def __init__(self, data, dimensions=None, record=False, **kwargs):
        # fix strings, since netcdf3 has only the concept of char arrays
        if isinstance(data, basestring):
            data = list(data)

        # replace masked data --if any-- with missing_value.
        missing_value = (
                kwargs.get('missing_value') or
                kwargs.get('_FillValue') or 
                getattr(data, 'fill_value', None))
        if missing_value is not None:
            kwargs.setdefault('missing_value', missing_value)
            kwargs.setdefault('_FillValue', missing_value)
            self.data = numpy.ma.asarray(data).filled(missing_value)
        else:
            self.data = numpy.asarray(data)

        self.dimensions = dimensions
        self.record = record
        self.attributes = kwargs


class Group(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class NetCDF(object):
    @classmethod
    def save(klass, filename, **kwargs):
        # find netcdf loader
        if hasattr(klass, 'loader') and callable(getattr(klass, 'loader')):
            loader = getattr(klass, 'loader')
        else:
            from pupynere import netcdf_file as loader
        out = loader(filename, 'w', **kwargs)
        process(klass, out)
        out.close()


def format(attr):
    if isinstance(attr, (tuple, list)):
        return map(format, attr)
    else:
        return str(attr)


def process(obj, target):
    # add attributes
    for name in dir(obj):
        attr = getattr(obj, name)
        if name.startswith("__") or not isinstance(attr, (tuple, list, basestring)):
            continue
        setattr(target, name, format(attr))

    # set variable names from the class
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, (Variable, Dimension)):
            attr.name = name

    # add explicitly defined dimensions
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, Dimension):
            target.createDimension(name, attr.length)

    # add groups
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, Group):
            group = target.createGroup(name)
            process(attr, group)

    # add variables, and add their dimensions if necessary
    variables = []
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, Variable):
            variables.append(attr)

    # sort so that record dimensions get created first
    variables.sort(key=lambda var: not var.record)
    for variable in variables:
        # add dimension?
        if variable.dimensions is None:
            variable.dimensions = [ variable ]
        for dim in variable.dimensions:
            if dim.name not in target.dimensions:
                if dim.record:
                    target.createDimension(dim.name, None)
                else:
                    target.createDimension(dim.name, len(dim.data))

        # create var
        if variable.data.dtype == numpy.int64:
            variable.data = variable.data.astype(numpy.int32)
        var = target.createVariable(
                variable.name, 
                variable.data.dtype, 
                tuple(dim.name for dim in variable.dimensions))
        var[:] = variable.data[:]
        for k, v in variable.attributes.items():
            setattr(var, k, v)
