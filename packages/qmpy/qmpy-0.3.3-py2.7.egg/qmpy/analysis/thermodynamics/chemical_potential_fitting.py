from qmpy import *
from qmpy.utils.strings import *
from pprint import pprint
from qmpy.data import save_chem_pots, chem_pots

import yaml

def fit(calculations=None, experiments=None, fit_for=[]):
    data = []
    hub_data = []

    elements = set()  # list of all elements in any compound in fit
    hubbards = set() # list of all hubbards in any calc in fit
    fit_set = set(fit_for)
    expts = {}
    calcs = {}

    expt_data = experiments.values_list('composition_id', 'delta_e')
    calc_data = calculations.values_list('composition_id', 'energy_pa')
    base_mus = dict( (elt, Composition.get(elt).energy) for elt in
            element_groups['all'])

    for (name, delta_e), expt in zip(expt_data, experiments):
        if expt.delta_e is None:
            continue
        if not set(parse_comp(name).keys()) & fit_set:
            continue

        if not expt.composition.name in expts:
            expts[expt.composition.name] = expt
        elif delta_e < expts[name].delta_e:
            expts[name] = expt

    for (name, energy_pa), calc in zip(calc_data, calculations):
        if energy_pa is None:
            continue
        if not set(parse_comp(name).keys()) & fit_set:
            continue

        if not name in calcs:
            calcs[name] = calc
        elif energy_pa < calcs[name].energy_pa:
            calcs[name] = calc

    valid_pairs = set(calcs.keys()) & set(expts.keys())
    for name in valid_pairs:
        for elt in parse_comp(name):
            elements.add(elt)
        if not calcs[name].hub_comp:
            data.append(name)
        else:
            hub_data.append(name)
            for hub in calcs[name].hubbards:
                if hub: 
                    hubbards.add(hub)

    elements = list(elements)
    hubbards = list(hubbards)
    hubbard_elements = [ hub.element.symbol for hub in hubbards ]

    A = []
    b = []

    for name in data:
        uc = unit_comp(parse_comp(name))
        # remove non-fitting elements
        b.append(calcs[name].energy_pa - expts[name].delta_e - sum( base_mus[elt]*amt 
                for elt, amt in uc.items() if elt not in fit_for ))
        A.append([ uc.get(elt,0) for elt in fit_for ])
    
    A = np.array(A)
    b = np.array(b)
    if len(A) == 0 and len(b) == 0:
        element_mus = {}
    else:
        result = np.linalg.lstsq(A, b)
        element_mus = dict(zip(fit_for, result[0]))

    ### Second fit
    A = []
    b = []
    for name in hub_data:
        uc = unit_comp(parse_comp(name))
        b.append(calcs[name].energy_pa - expts[name].delta_e -
                sum( base_mus[elt]*amt
                    for elt, amt in uc.items() 
                    if elt not in fit_for) - 
                sum( element_mus.get(elt, 0)*amt
                    for elt, amt in uc.items()))
        A.append([ uc.get(elt, 0) for elt in hubbard_elements ])

    A = np.array(A)
    b = np.array(b)
    if len(A) == 0 and len(b) == 0:
        hubbard_mus = {}
    else:
        result = np.linalg.lstsq(A, b)
        hubbard_mus = dict(zip(hubbards, result[0]))

    element_mus = dict( (str(e), float(val)) for e, val in element_mus.items())
    for elt, mu in base_mus.items():
        if elt not in element_mus:
            element_mus[str(elt)] = float(mu)
        elif abs(element_mus[elt]) > 100:
            print elt, element_mus[elt], mu
            element_mus[str(elt)] = float(mu)

    hubbard_mus = dict( (str(h.key), float(val)) for h, val in hubbard_mus.items())

    for elt, val in element_mus.items():
        print elt, val

    for hub, val in hubbard_mus.items():
        print hub, val

    return element_mus, hubbard_mus
