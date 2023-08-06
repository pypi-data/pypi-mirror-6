#/usr/bin/env python
# -*- coding: utf-8 -*-

import cif
import poscar
import ase

class StructureFormatError(Exception):
    """Problem reading an input file"""

class FormatNotSupportedError(Exception):
    """The provided input format is not supported"""

def read(source_file, *args, **kwargs):
    if 'cif' in source_file:
        return cif.read(source_file, *args, **kwargs)
    elif ( 'POSCAR' in source_file or
            'CONTCAR' in source_file ):
        return poscar.read(source_file, *args, **kwargs)
    else:
        return ase.read(source_file, *args, **kwargs)
    raise FormatNotSupportedError('The file %s is in an unrecognized format\
            and cannot be read' % source_file)

def write(structure, format='poscar', convention=None, filename=None,
        **kwargs):
    if convention == 'primitive':
        structure.make_primitive()
    elif convention == 'conventional':
        structure.make_conventional()

    def write_or_return(string, filename=None):
        if filename is None:
            return string
        else:
            f = open(filename, 'w')
            f.write(string)
            f.close()

    if format == 'poscar':
        return write_or_return(poscar.write(structure, **kwargs), filename)
    elif format == 'cif':
        return write_or_return(cif.write(structure, **kwargs), filename)
    else:
        return write_or_return(ase_mapper.write(structure, **kwargs), filename)
