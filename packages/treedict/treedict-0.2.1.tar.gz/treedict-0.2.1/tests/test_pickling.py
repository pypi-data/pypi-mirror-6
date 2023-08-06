#!/usr/bin/env python

# Copyright (c) 2009-2011, Hoyt Koepke (hoytak@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     - Neither the name 'treedict' nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Hoyt Koepke ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Hoyt Koepke BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import random, unittest, collections
try:
    import cPickle as pickle
except ImportError:
    import pickle
from treedict import TreeDict, getTree
import treedict
from copy import deepcopy, copy

from hashlib import md5
import random

from common import *

class TestPickling(unittest.TestCase):
       
    def testPickling_P0(self):
        p = sample_tree()
        s = pickle.dumps(p, protocol=0)
        p2 = pickle.loads(s)

        self.assert_(p == p2)

    def testPickling_P1(self):
        p = sample_tree()
        s = pickle.dumps(p, protocol=1)
        p2 = pickle.loads(s)
        
        self.assert_(p == p2)

    def testPickling_P2(self):
        p = sample_tree()
        s = pickle.dumps(p, protocol=2)
        p2 = pickle.loads(s)
        
        self.assert_(p == p2)

    def testPickling_P0f(self):
        p = frozen_tree()
        s = pickle.dumps(p, protocol=0)
        p2 = pickle.loads(s)

        self.assert_(p == p2)

    def testPickling_P1f(self):
        p = frozen_tree()
        s = pickle.dumps(p, protocol=1)
        p2 = pickle.loads(s)
        
        self.assert_(p == p2)

    def testPickling_P2f(self):
        p = frozen_tree()
        s = pickle.dumps(p, protocol=2)
        p2 = pickle.loads(s)
        
        self.assert_(p2.isFrozen())
        self.assert_(p == p2)

    def testPickling_Dangling_01(self):

        p = makeTDInstance()
        p.a

        p2 = pickle.loads(pickle.dumps(p, protocol=2))

        self.assert_(p2 == p)

    def testPickling_Dangling_02(self):

        p = makeTDInstance()
        p.a = p.b

        p2 = pickle.loads(pickle.dumps(p, protocol=2))

        self.assert_(p2 == p)

    def testPickling_Dangling_03(self):

        p = makeTDInstance()
        p.a = p.b = p.c
        
        p.b = 2

        p2 = pickle.loads(pickle.dumps(p, protocol=2))

        self.assert_(p2 == p)

    def testPicklingWithIteratorReferencing(self):

        p = makeTDInstance()

        p.a = 1
        p.b = 2
        p.c = 3

        it = p.iteritems()

        p2 = pickle.loads(pickle.dumps(p, protocol=2))

        self.assert_(p == p2)

        self.assertRaises(RuntimeError, lambda: p.set('d', 4))
        p2.d = 4


if __name__ == '__main__':
    unittest.main()

