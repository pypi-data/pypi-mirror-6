# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009,  Rectorate of the University of Freiburg
# Copyright (c) 2009-2011, Andreas W. Liehr (liehr@users.sourceforge.net)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import unittest, numpy
from pyphant.core.DataContainer import (
    FieldContainer, SampleContainer, assertEqual
    )
from pyphant.quantities import Quantity
from pyphant.quantities.ParseQuantities import str2unit
from copy import deepcopy
from pyphant.core import LoadFMF
import pkg_resources

#Estimate floating point accuracy
ACCURACY = 1.0 -0.1 -0.1 -0.1 -0.1 -0.1 -0.1 -0.1 -0.1 -0.1 -0.

class FieldContainerCondenseDim(unittest.TestCase):
    def setUp(self):
        self.x = numpy.linspace(0,0.9,10)
        m = numpy.meshgrid(self.x, self.x*5)
        self.valid = numpy.tile(self.x, (10,1))
        self.invalid = [
            a.squeeze() for a in numpy.vsplit(m[0] + m[1], len(m[0]))
            ]

    def testInvalid(self):
        self.assertRaises(
            AssertionError, LoadFMF.checkAndCondense, self.invalid
            )

    def testValid(self):
        result = LoadFMF.checkAndCondense(self.valid)
        numpy.testing.assert_array_equal(self.x, result)

class TestColumn2FieldContainer(unittest.TestCase):
    def testStrings(self):
        column = ['Hello', 'World']
        result = LoadFMF.column2FieldContainer('simple string', column)
        expectedResult = FieldContainer(
            numpy.array(column), longname='simple string'
            )
        assertEqual(result, expectedResult)

    def testListofStrings(self):
        column = ['World', ['Hello', 'World'], 'World']
        result = LoadFMF.column2FieldContainer('simple string', column)
        expectedResult = FieldContainer(
            numpy.array(['World', 'Hello, World', 'World']),
            longname='simple string'
            )
        assertEqual(result, expectedResult)

    def testListofStrings2(self):
        column = [['Hello', 'World'], 'World']
        result = LoadFMF.column2FieldContainer('simple string', column)
        expectedResult = FieldContainer(
            numpy.array(['Hello, World', 'World']), longname='simple string'
            )
        assertEqual(result, expectedResult)

    def testVariable(self):
        column = [
            ('T', Quantity('22.4 degC'), Quantity('0.5 degC')),
            ('T', Quantity('11.2 degC'), Quantity('0.5 degC'))
            ]
        result = LoadFMF.column2FieldContainer('temperature', column)
        expectedResult = FieldContainer(
            numpy.array([22.4, 11.2]) ,error=numpy.array([0.5, 0.5]),
            mask=numpy.array([False, False]),
            unit='1 degC', longname='temperature', shortname='T'
            )
        assertEqual(result, expectedResult)

    def testVariableWithNaN(self):
        column = [
            ('T', Quantity('22.4 degC'), Quantity('0.5 degC')),
            ('T', Quantity('11.2 degC'), None)
            ]
        result = LoadFMF.column2FieldContainer('temperature', column)
        expectedResult = FieldContainer(
            numpy.array([22.4, 11.2]), error=numpy.array([0.5, 0.0]),
            mask = numpy.array([False, False]),
            unit='1 degC', longname='temperature', shortname='T'
            )
        assertEqual(result, expectedResult)

    def testVariableFirstNaN(self):
        column = [
            ('T', 'NaN', Quantity('0.5 degC')),
            ('T', Quantity('11.2 degC'), None)
            ]
        result = LoadFMF.column2FieldContainer('temperature', column)
        expectedResult = FieldContainer(
            numpy.array([numpy.NaN, 11.2]), error=numpy.array([0.5, 0.0]),
            mask = numpy.array([True, False]),
            unit='1 degC', longname='temperature', shortname='T')
        assertEqual(result, expectedResult)

class TestDiscriminatingJouleAndImaginary(unittest.TestCase):
    """
    In order to discriminate between an imaginary number and unit Joule,
    imaginary numbers have to be indicated only by a minor capital 'j',
    while a major capital 'J' indicates the unit Joule.
    """
    def setUp(self):
        self.inputDict = {'complexJ':'1.0j', 'Joule':'1.0J'}

    def testComplexValue(self):
        """Imaginary numbers are indicated by 'j'."""
        result = LoadFMF.item2value(self.inputDict['complexJ'])
        self.assertEqual(result, (complex(self.inputDict['complexJ']), None))

    def testJouleValue1_1(self):
        """Physical quantities with unit Joule are indicated by 'J'."""
        result = LoadFMF.item2value(self.inputDict['Joule'])
        self.assertEqual(result, (Quantity(self.inputDict['Joule']), None))

    def testJouleValue1_0(self):
        """Physical quantities with unit Joule are indicated by 'J'."""
        result = LoadFMF.item2value(
            self.inputDict['Joule'], FMFversion='1.0'
            )
        self.assertEqual(result, (Quantity(self.inputDict['Joule']), None))

class TestFMFversion1_0(unittest.TestCase):
    def almostEqual(self, a, b):
        diff = a - b
        mean = 0.5 * (a + b)
        self.assertTrue(abs(diff / mean) < ACCURACY)

    def setUp(self):
        self.FMFinput = """# -*- fmf-version: 1.0; coding: utf-8 -*-
[*reference]
title: The physical constants of the Full-Metadata Format 1.0 as documented in http://arxiv.org/abs/0904.1299
creator: Andreas W. Liehr
created: 2010-03-16
place: ICE 676, Offenburg-Karlsruhe, Germany
[Mathematical and Physical Constants]
Area of unit circle:  pi = 3.1415926535897931
Speed of light: c = 299792458 m/s
Permeability of vacuum: \mu_0 = 4.e-7 pi*N/A**2
Permittivity of vacuum: \eps_0 = 1.0 1/mu0/c**2
Gravitational constant: Grav = 6.67259e-11 m**3/kg/s**2
Planck constant: hplanck = 6.6260755e-34 J*s
Planck constant / 2pi: hbar = 0.5 hplanck/pi
Elementary charge: e = 1.60217733e-19 C
Electron mass:       m_e = 9.1093897e-31 kg
Proton mass: m_p = 1.6726231e-27 kg
Avogadro number: Nav = 6.0221367e23 1/mol
Boltzmann constant: k = 1.380658e-23 J/K
[Additional constants changed from FMF version 1.0 to 1.1]
Parsec: pc = 3.08567758128E16 m
US gallon: galUS = 4 qt
Atomic mass units: amu = 1.6605402e-27 kg
[*table definitions]
table: T
mixed: M
[*data definitions: T]
String: S
Integer: I
Float with dot: Fd
Float with exponent: Fe
Complex: C
Missing Value: V_m
Infinite Value: V_i
[*data: T]
H_2	1	1.	1e1	1+0j	nan	inf
O_2	2	.2	2E1	2+.1j	NaN	INF
O 2	2	.2	2E1	2.+2j	NAN	Inf
[*data definitions: M]
String: S
Complex: C
Float: F
[*data: M]
N_2	1	2
2	1+1j	2.
"""
    def testReadSingleFile(self):
        """
        Test the correct interpretation of physical constants
        as definied in FMF version 1.0.
        """
        consts = LoadFMF.readSingleFile(
            self.FMFinput,
            "testReadSingleFile")[0].attributes[
            'Mathematical and Physical Constants'
            ]
        self.assertEqual(
            consts[u'Speed of light'][1], str2unit("1 c", FMFversion="1.0")
            )
        self.assertEqual(consts[u'Speed of light'][1], str2unit("1 c"))
        self.assertEqual(
            consts[u'Permeability of vacuum'][1],
            str2unit("1 mu0", FMFversion="1.0")
            )
        self.assertEqual(
            consts[u'Permittivity of vacuum'][1],
            str2unit("1 eps0", FMFversion="1.0")
            )
        self.assertEqual(
            consts[u'Gravitational constant'][1],
            str2unit("1 Grav", FMFversion="1.0")
            )
        self.assertTrue(
            consts[u'Planck constant'][1],
            str2unit("1 hplanck", FMFversion="1.0")
            )
        self.almostEqual(
            consts[u'Planck constant / 2pi'][1],
            str2unit("1 hbar", FMFversion="1.0")
            )
        self.almostEqual(
            consts[u'Elementary charge'][1],
            str2unit("1 e", FMFversion="1.0")
            )
        self.assertNotEqual(
            consts[u'Elementary charge'][1], str2unit("1 e"),
            "Elementary charge has been adapted to new CODATA recommendations."
            )
        self.assertEqual(
            consts[u'Electron mass'][1], str2unit("1 me", FMFversion="1.0")
            )
        self.assertNotEqual(
            consts[u'Electron mass'][1], str2unit("1 me"),
            "Electron mass has been adapted to new CODATA recommendations."
            )
        self.assertEqual(
            consts[u'Proton mass'][1], str2unit("1 mp", FMFversion="1.0")
            )
        self.assertNotEqual(
            consts[u'Proton mass'][1], str2unit("1 mp"),
            "Proton mass has been adapted to new CODATA recommendations."
            )
        self.assertEqual(
            consts[u'Avogadro number'][1], str2unit("1 Nav", FMFversion="1.0")
            )
        self.assertEqual(
            consts[u'Boltzmann constant'][1], str2unit("1 k", FMFversion="1.0")
            )
        consts = LoadFMF.readSingleFile(
            self.FMFinput,
            "testReadSingleFile")[0].attributes[
            'Additional constants changed from FMF version 1.0 to 1.1'
            ]
        self.almostEqual(
            consts[u'Parsec'][1], str2unit("1 pc", FMFversion="1.0")
            )
        self.almostEqual(
            consts[u'US gallon'][1], str2unit("1 galUS", FMFversion="1.0")
            )
        self.assertEqual(
            consts[u'Atomic mass units'][1],
            str2unit("1 amu", FMFversion="1.0")
            )


class TestFMFversion1_1(unittest.TestCase):
    def setUp(self):
        self.FMFinput = """# -*- fmf-version: 1.1; coding: utf-8 -*-
[*reference]
title: The physical constants of the Full-Metadata Format 1.1 by Riede in doi://10.1016/j.cpc.2009.11.014
creator: Andreas W. Liehr
created: 2010-03-17
place: ICE 604, Offenburg-Karlsruhe, Germany
[Mathematical and Physical Constants]
Area of unit circle:  pi = 3.1415926535897931
Speed of light: c = 299792458 m/s
Permeability of vacuum: \mu_0 = 4.e-7 pi*N/A**2
Permittivity of vacuum: \eps_0 = 1.0 1/mu0/c**2
Faraday constant: Fa = 96485.3399 C/mol
Gravitational constant: G = 6.67428e-11 m**3/kg/s**2
Planck constant: h = 6.62606896e-34 J*s
Planck constant / 2pi: hbar = 0.5 h/pi
Elementary charge: e = 1.602176487e-19 C
Electron mass:       m_e = 9.10938215e-31 kg
Proton mass: m_p = 1.672621637e-27 kg
Avogadro number: NA = 6.02214179e23 1/mol
Boltzmann constant: k = 1.3806504e-23 J/K
Rydberg constant: Ryd = 10973731.568527 1/m
[Additional constants changed from FMF version 1.0 to 1.1]
Parsec: pc = 3.0856776E16 m
US gallon: galUS = 231 inch**3
Wave-numbers/inverse cm: invcm = 1 h*c/cm
Atomic mass units: u = 1.660538782e-27 kg
[*table definitions]
table: T
mixed: M
[*data definitions: T]
String: S
Integer: I
Float with dot: Fd
Float with exponent: Fe
Complex: C
Missing Value: V_m
Infinite Value: V_i
[*data: T]
H_2	1	1.	1e1	1+0j	nan	inf
O_2	2	.2	2E1	2+.1j	NaN	INF
O 2	2	.2	2E1	2.+2j	NAN	Inf
[*data definitions: M]
String: S
Complex: C
Float: F
[*data: M]
N_2	1	2
2	1+1j	2.
"""
    def testReadSingleFile(self):
        """
        Test the correct interpretation of physical constants
        as definied in FMF version 1.1.
        """
        consts = LoadFMF.readSingleFile(
            self.FMFinput, "testReadSingleFile")[0].attributes[
            'Mathematical and Physical Constants'
            ]
        self.assertEqual(
            consts[u'Speed of light'][1], str2unit("1 c", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Permeability of vacuum'][1],
            str2unit("1 mu0", FMFversion="1.1"),
            'The values differ by %s.' % (
                consts[u'Permeability of vacuum'][1] -\
                str2unit("1 mu0", FMFversion="1.1"),
                )
            )
        self.assertEqual(
            consts[u'Permittivity of vacuum'][1],
            str2unit("1 eps0", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Gravitational constant'][1],
            str2unit("1 G", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Planck constant'][1],
            str2unit("1 h", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Planck constant / 2pi'][1],
            str2unit("1 hbar", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Elementary charge'][1], str2unit("1 e",FMFversion="1.1"),
            'The elements %s and %s do not match.' % (
                consts[u'Elementary charge'][1],
                str2unit("1 e", FMFversion="1.1")
                )
            )
        self.assertEqual(
            consts[u'Electron mass'][1], str2unit("1 me", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Proton mass'][1], str2unit("1 mp", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Avogadro number'][1], str2unit("1 NA", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Boltzmann constant'][1], str2unit("1 k",FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Rydberg constant'][1], str2unit("1 Ryd", FMFversion="1.1")
            )
        consts = LoadFMF.readSingleFile(
            self.FMFinput, "testReadSingleFile")[0].attributes[
            'Additional constants changed from FMF version 1.0 to 1.1'
            ]
        self.assertEqual(
            consts[u'Parsec'][1], str2unit("1 pc", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'US gallon'][1], str2unit("1 galUS", FMFversion="1.1")
            )
        self.assertEqual(
            consts[u'Atomic mass units'][1], str2unit("1 u", FMFversion="1.1")
            )


class Emd5ConsistencyTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = pkg_resources.resource_filename(
            'pyphant', 'tests/resources/fmf/dep.fmf'
            )

    def testImportFMF(self):
        from pyphant.core.LoadFMF import loadFMFFromFile
        table = loadFMFFromFile(self.filename)
        print "Testing imported SampleContainer for consistency..."
        for column in ['y0', 'y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8']:
            self.assertEqual(table[column].dimensions[0].id,
                             table['x'].id)

    def testRegisterFMF(self):
        from pyphant.core.KnowledgeManager import KnowledgeManager
        kmanager = KnowledgeManager.getInstance()
        table_id = kmanager.registerFMF(self.filename, temporary=True)
        table = kmanager.getDataContainer(table_id)
        print "Testing registered SampleContainer for consistency..."
        for column in ['y0', 'y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8']:
            self.assertEqual(table[column].dimensions[0].id,
                             table['x'].id)

    def testRegisterFMFSummary(self):
        from pyphant.core.KnowledgeManager import KnowledgeManager
        kmanager = KnowledgeManager.getInstance()
        table_id = kmanager.registerFMF(self.filename, temporary=True)
        table = kmanager.getDataContainer(table_id)
        print "Testing registered SampleContainer summary for consistency..."
        for column in ['y0', 'y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8']:
            summary = kmanager.getSummary(table[column].id)
            emd5 = summary['dimensions'][0]
            self.assertEqual(emd5, table['x'].id)


class LoaderTestCase(unittest.TestCase):
    def load(self, filename):
        res = 'tests/resources/fmf/' + filename
        data = LoadFMF.loadFMFFromFile(
            pkg_resources.resource_filename('pyphant', res)
            )
        data.seal()
        return data


class PathologicalTestCase(LoaderTestCase):
    def checkExpected(self, columns, result):
        expected = SampleContainer(columns, longname='Table', shortname='T',
                                   attributes=deepcopy(result.attributes))
        expected.seal()
        self.assertEqual(result, expected)

    def testLoadOneRowDep(self):
        result = self.load('onerow_dep.fmf')
        t = FieldContainer(numpy.array([1.0]), unit=Quantity('1 s'),
                           shortname='t', longname='time')
        s = FieldContainer(numpy.array([5.0]), unit=Quantity('1 m'),
                           shortname='s', longname='distance')
        s.dimensions[0] = deepcopy(t)
        self.checkExpected([t, s], result)

    def testLoadOneRow(self):
        result = self.load('onerow.fmf')
        t = FieldContainer(numpy.array([1.0]), unit=Quantity('1 s'),
                           shortname='t', longname='time')
        s = FieldContainer(numpy.array([2.0]), unit=Quantity('1 m'),
                           shortname='s', longname='distance')
        self.checkExpected([t, s], result)

    def testLoadOneColumn(self):
        result = self.load('onecolumn.fmf')
        t = FieldContainer(numpy.array([1, 2, 3, 4]), unit=Quantity('1 s'),
                           shortname='t', longname='time')
        self.checkExpected([t], result)

    def testLoadOneValue(self):
        result = self.load('onevalue.fmf')
        t = FieldContainer(numpy.array([1.0]), unit=Quantity('1 s'),
                           shortname='t', longname='time')
        self.checkExpected([t], result)

    def testLoadMultiTable(self):
        self.load('multitable.fmf')


class CommentCharTestCase(LoaderTestCase):
    def testHash(self):
        result = self.load('hash_test.fmf')
        title = "Testfile for # checking"
        self.assertEqual(result.attributes['*reference']['title'], title)

    def testSemi(self):
        result = self.load('semi_test.fmf')
        title = "Testfile for ; checking"
        self.assertEqual(result.attributes['*reference']['title'], title)


if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger('pyphant')
    hdlr = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('[%(name)s|%(levelname)s] %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
