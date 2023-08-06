import logging
import time
from django.db import models
from datetime import datetime
import os

import qmpy.utils as utils
from qmpy.analysis.vasp import *
from qmpy.analysis.thermodynamics.space import PhaseSpace

logger = logging.getLogger(__name__)

def initialize(entry, **kwargs):
    entry.input.set_magnetism('ferro')
    calc = Calculation.setup(entry.input, entry=entry,
            configuration='initialize', path=entry.path+'/initialize', 
            **kwargs)
    if not calc.converged:
        calc.write()
        return calc
    if calc.converged:
        if calc.magmom > 0.1:
            entry.keywords.append('magnetic')
        entry.calculations['initialize'] = calc
        entry.structures['initialize'] = calc.output
    return calc

def coarse_relax(entry, **kwargs):
    if entry.calculations.get('coarse_relax', Calculation()).converged:
        return entry.calculations['coarse_relax']

    calc = initialize(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    inp = entry.structures['input']
    if not 'magnetic' in entry.keywords:
        inp.set_magnetism('none')
    calc = Calculation.setup(inp, entry=entry,
        configuration='coarse_relax', path=entry.path+'/coarse_relax',
        **kwargs)

    if calc.converged:
        entry.structures['coarse_relax'] = calc.output
        entry.calculations['coarse_relax'] = calc
    return calc

def fine_relax(entry, **kwargs):
    if entry.calculations.get('fine_relax', Calculation()).converged:
        return entry.calculations['fine_relax']

    calc = coarse_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc
    inp = entry.structures['coarse_relax']
    if 'magnetic' in entry.keywords:
        inp.set_magnetism('ferro')

    calc = Calculation.setup(inp, entry=entry,
        configuration='fine_relax', path=entry.path+'/fine_relax', **kwargs)
    if calc.converged:
        entry.structures['fine_relax'] = calc.output
        entry.calculations['fine_relax'] = calc
    return calc

def standard(entry, **kwargs):
    if entry.calculations.get('standard', Calculation()).converged:
        return entry.calculations['standard']

    calc = fine_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    inp = entry.structures['fine_relax']
    if 'magnetic' in entry.keywords:
        inp.set_magnetism('ferro')

    calc = Calculation.setup(inp, entry=entry,
        configuration='standard', path=entry.path+'/standard', **kwargs)
    if calc.converged:
        f = calc.compute_formation()
        f.entry = entry
        f.save()
        entry.calculations['standard'] = calc
        entry.structures['standard'] = calc.output
    return calc

def relaxation(entry, **kwargs):
    if entry.calculations.get('relaxation', Calculation()).converged:
        return entry.calculations['relaxation']

    input = entry.input
    input.make_primitive()

    calc = Calculation.setup(input,  entry=entry,
                                     configuration='relaxation',
                                     path=entry.path+'/relaxation',
                                     **kwargs)
    entry.calculations['relaxation'] = calc
    if not calc.converged:
        calc.write()
        return calc
    else:
        entry.structures['relaxation'] = calc.output
    return calc

def static(entry, **kwargs):
    if entry.calculations.get('static', Calculation()).converged:
        return entry.calculations['static']

    calc = relaxation(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    input = calc.output
    calc = Calculation.setup(input, entry=entry,
                                    configuration='static', 
                                    path=entry.path+'/static', 
                                    chgcar=entry.path+'/relaxation',
                                    **kwargs)
    entry.calculations['static'] = calc

    if calc.converged:
        f = calc.compute_formation()
        f.save()
        s = PhaseSpace('-'.join(entry.comp.keys()))
        s.compute_stabilities()
        entry.calculations['static'] = calc
        entry.structures['final'] = calc.output
    return calc
