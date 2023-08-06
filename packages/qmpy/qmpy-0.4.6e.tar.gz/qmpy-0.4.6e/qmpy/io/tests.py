from qmpy import *
import unittest
from django.test import TestCase

class POSCARTestCase(TestCase):
    def setUp(self):
        elements = open(INSTALL_PATH+'/data/elements/data.yml').read()
        elts = []
        for elt, data in yaml.load(elements).items():
            e = Element(**data)
            elts.append(e)
        Element.objects.bulk_create(elts)

        a = 3.54
        cell = [[a,0,0],[0,a,0],[0,0,a]]
        atoms = [('Cu', [0,0,0]),
                         ('Cu', [0.5, 0.5, 0.5])]
        self.struct = Structure.create(cell=cell, atoms=atoms)


    def test_vasp4(self):
        s = io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_vasp4')
        self.assertEqual(self.struct, s)

    def test_vasp5(self):
        s = io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_vasp5')
        self.assertEqual(self.struct, s)

    def test_write_vasp5(self):
        ans = open(INSTALL_PATH+'/io/files/POSCAR_vasp5').read()
        self.assertEqual(io.poscar.write(self.struct), ans)

    def test_write_vasp5(self):
        ans = open(INSTALL_PATH+'/io/files/POSCAR_vasp4').read()
        self.assertEqual(io.poscar.write(self.struct, vasp4=True), ans)


class CifTestCase(TestCase):
    def setUp(self):
        elements = open(INSTALL_PATH+'/data/elements/data.yml').read()
        elts = []
        for elt, data in yaml.load(elements).items():
            e = Element(**data)
            elts.append(e)
        Element.objects.bulk_create(elts)
        a = 3.54
        cell = [[a,0,0],[0,a,0],[0,0,a]]
        atoms = [('Cu', [0,0,0]),
                         ('Cu', [0.5, 0.5, 0.5])]
        self.struct = Structure.create(cell=cell, atoms=atoms)

    def test_read(self):
        s = io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_vasp4')
        self.assertEqual(self.struct, s)

    def test_write(self):
        ans = open(INSTALL_PATH+'/io/files/test.cif').read()
        self.assertEqual(io.cif.write(self.struct), ans)
