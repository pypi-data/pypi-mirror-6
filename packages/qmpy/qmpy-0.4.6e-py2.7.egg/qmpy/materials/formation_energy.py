#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
import json
import logging

from qmpy.db.custom import DictField
from qmpy.materials.composition import Composition
from qmpy.utils import *

logger = logging.getLogger(__name__)

class ExptFormationEnergy(models.Model):
    """Experimentally measured formation energy.

    Any external formation energy should be entered as an ExptFormationEnergy
    object, rather than a FormationEnergy. If the external source is also
    computational, set the "dft" attribute to be True.

    Attributes:
        | composition
        | delta_e
        | delta_g
        | dft
        | fit
        | id
        | source


    """
    composition = models.ForeignKey('Composition', null=True, blank=True)
    delta_e = models.FloatField(null=True)
    delta_g = models.FloatField(null=True)
    source = models.CharField(max_length=127, blank=True, null=True)
    dft = models.BooleanField(default=False)

    class Meta:
        app_label = 'qmpy'
        db_table = 'expt_formation_energies'

    def __str__(self):
        return '%s : %s' % (self.composition, self.delta_e)

    @classmethod
    def read_file(cls, filename, dft=False):
        source = filename.split('.')[0]
        expts = []
        for line in open(filename, 'r'):
            comp, energy = line.strip().split()
            expt, new = ExptFormationEnergy.objects.get_or_create(delta_e=energy,
                    composition=Composition.get(comp),
                    source=source, 
                    dft=dft)
            if new:
                expt.save()
            expts.append(expt)
        return expts

class Fit(models.Model):
    """
    The core model for a reference energy fitting scheme. 
    
    The Fit model links to the experimental data (ExptFormationEnergy objects) 
    that informed the fit, as well as the DFT calculations (Calculation objects) 
    that were matched to each experimental formation energy. Once the fit is 
    completed, it also stores a list of chemical potentials both as a 
    relationship to ReferenceEnergy and HubbardCorrection objects. 
    These correction energies can also be accessed by dictionaries at 
    Fit.mus and Fit.hubbard_mus.

    Attributes:
        | dft
        | experiments
        | formationenergy
        | hubbard_correction_set
        | name
        | reference_energy_set
        | structure
    
    Example:
    >>> f = Fit.get('standard')
    >>> f.experiments.count()
    >>> f.dft.count()
    >>> f.mus
    >>> f.hubbard_mus
    """
    name = models.CharField(max_length=255, primary_key=True)
    experiments = models.ManyToManyField('ExptFormationEnergy') 
    dft = models.ManyToManyField('Calculation')

    class Meta:
        app_label = 'qmpy'
        db_table = 'fits'

    @classmethod
    def get(cls, name):
        try:
            return Fit.objects.get(name=name)
        except Fit.DoesNotExist:
            return Fit(name=name)


    @property
    def mus(self):
        mus = self.reference_energy_set.values_list('element_id', 'value')
        return dict(mus)

class HubbardCorrection(models.Model):
    """
    Energy correction for DFT+U energies.

    Attributes:
        | element
        | fit
        | id
        | value

    """
    element = models.ForeignKey('Element')
    value = models.FloatField()
    fit = models.ForeignKey('Fit', blank=True, null=True,
                                   related_name='hubbard_correction_set')

    class Meta:
        app_label = 'qmpy'
        db_table = 'hubbard_corrections'

class ReferenceEnergy(models.Model):
    """
    Elemental reference energy for evaluating heats of formation.

    Attributes:
        | element
        | fit
        | id
        | value


    """
    element = models.ForeignKey('Element')
    value = models.FloatField()
    fit = models.ForeignKey('Fit', blank=True, null=True,
                                   related_name='reference_energy_set')

    class Meta:
        app_label = 'qmpy'
        db_table = 'reference_energies'

class FormationEnergy(models.Model):
    """
    Base class for a formation energy.

    Attributes:
        | calculation
        | composition
        | delta_e
        | description
        | entry
        | equilibrium
        | fit
        | id
        | stability

    """
    composition = models.ForeignKey('Composition', null=True, blank=True)
    entry = models.ForeignKey('Entry', null=True, blank=True)
    calculation = models.ForeignKey('Calculation', null=True, blank=True)
    description = models.CharField(max_length=20, null=True, blank=True)
    fit = models.ForeignKey('Fit', null=True)

    stability = models.FloatField(blank=True, null=True)
    delta_e = models.FloatField(null=True)

    equilibrium = models.ManyToManyField('self', blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'formation_energies'

    @classmethod
    def get(cls, calculation, fit='standard'):
        fit = Fit.get(fit)
        try:
            return FormationEnergy.objects.get(calculation=calculation, fit=fit)
        except:
            return FormationEnergy(calculation=calculation, fit=fit)

    def __str__(self):
        return '%s : %s' % (self.composition, self.delta_e)

    def save(self, *args, **kwargs):
        self.composition = self.calculation.composition
        self.entry = self.calculation.entry
        super(FormationEnergy, self).save(*args, **kwargs)

Formation = FormationEnergy
