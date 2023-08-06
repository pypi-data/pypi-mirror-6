# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
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

u"""
"""


import unittest
import pkg_resources
import pyphant.core.Param as Param
from pyphant.core.CompositeWorker import CompositeWorker
import pyphant.core.EventDispatcher as EventDispatcher
from pyphant.core import Worker


class TestCompositeDummyWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution("pyphant").version
    name = "TestCompositeDummyWorker"


class CompositeWorkerParamNameChangeTest(unittest.TestCase):
    def setUp(self):
        self.composite = CompositeWorker()
        self.worker1 = TestCompositeDummyWorker(self.composite)
        self.worker1.getParam('name').value = 'worker1'
        self.worker2 = TestCompositeDummyWorker(self.composite)
        self.worker2.getParam('name').value = 'worker2'

    def testVetoBadNameChange(self):
        def setNameParam():
            self.worker1.getParam('name').value = 'worker2'
        self.assertRaises(Param.VetoParamChange, setNameParam)

    def testVetoGoodNameChange(self):
        self.worker1.getParam('name').value = 'worker1_neu'

    def testVetoBadNameCreation(self):
        TestCompositeDummyWorker(self.composite)
        TestCompositeDummyWorker(self.composite)
        TestCompositeDummyWorker(self.composite)
        TestCompositeDummyWorker(self.composite)
        TestCompositeDummyWorker(self.composite)
        TestCompositeDummyWorker(self.composite)

if __name__ == '__main__':
    unittest.main()
