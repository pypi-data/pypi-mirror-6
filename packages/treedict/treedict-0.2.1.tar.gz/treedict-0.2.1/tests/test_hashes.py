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
from treedict import TreeDict, getTree, HashError
import treedict
from copy import deepcopy, copy

from hashlib import md5
import random

from common import *

class TestHashes(unittest.TestCase):

    ################################################################################
    # Hashes

    def testhashes_01(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf = "1234"
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.asdf = "1234"

        self.assert_(len(p1.hash()) != 0)
        self.assert_(p1.hash() == p2.hash())

    def testhashes_02(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf = "1234"
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.asdf = "1235"

        self.assert_(len(p1.hash()) != 0)
        self.assert_(p1.hash() != p2.hash())
        
    def testhashes_03(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf = "1234"
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.asdf = "1234"

        self.assert_(len(p1.hash("asdf")) != 0)
        self.assert_(p1.hash("asdf") == p2.hash("asdf"))


    def testhashes_04(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf = 221.12345139
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.asdf = 221.12345139

        self.assert_(len(p1.hash("asdf")) != 0)
        self.assert_(p1.hash("asdf") == p2.hash("asdf"))

    def testhashes_05(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf = 1234498484884499393939999324322432
         
        p2 = makeTDInstance('hashes_test_tree')
        p2.asdf = 1234498484884499393939999324322432

        self.assert_(len(p1.hash("asdf")) != 0)
        self.assert_(p1.hash("asdf") == p2.hash("asdf"))

    def testhashes_06(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf  = 1234498484884499393939999324322432
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.a.b.c = 1234498484884499393939999324322432

        self.assert_(len(p1.hash("asdf")) != 0)
        self.assert_(p1.hash("asdf") != p2.hash("a"))
        self.assert_(p1.hash("asdf") != p2.hash("a.b"))

    def testhashes_07(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf = 1234498484884499393939999324322432
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.a.b.asdf = 1234498484884499393939999324322432

        self.assert_(len(p1.hash("asdf")) != 0)
        self.assert_(p1.hash("asdf") == p2.hash("a.b.asdf"))

    def testhashes_08(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.asdf = 1234498484884499393939999324322432
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.a.b.notasdf = 1234498484884499393939999324322432

        self.assert_(len(p1.hash("asdf")) != 0)
        self.assert_(p1.hash("asdf") != p2.hash("a.b"))
        self.assert_(p1.hash() != p2.a.b.hash())
        self.assert_(p2.a.b.hash() == p2.hash("a.b"))

    def testhashes_09(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.a.b.c.asdf = 123
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.a.b.asdf = 123

        self.assert_(len(p1.hash("a.b.c.asdf")) != 0)
        self.assert_(p1.hash("a.b.c") == p2.hash("a.b"))
        self.assert_(p1.hash("a.b.c.asdf") == p2.hash("a.b.asdf"))
        self.assert_(p1.a.b.c.hash() == p1.hash("a.b.c"))
        self.assert_(p2.a.b.hash() == p2.hash("a.b"))

    def testhashes_10(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.a.b.c.asdf = deepcopy(test_object)
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.a.b.c.asdf = deepcopy(test_object)

        self.assert_(p1.hash() == p2.hash())

    def testhashes_11(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.a.b.c.asdf = deepcopy(test_tuple)
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.a.b.c.asdf = deepcopy(test_tuple)

        self.assert_(p1.hash() == p2.hash())

    def testhashes_12(self):
        p1 = makeTDInstance('hashes_test_tree')
        p1.a.b.c.asdf = deepcopy(test_list)
        
        p2 = makeTDInstance('hashes_test_tree')
        p2.a.b.c.asdf = deepcopy(test_list)
        
        self.assert_(p1.hash() == p2.hash())

    def testhashes_13_frozen_consistency(self):

        p1 = sample_tree()
        h = p1.hash()

        p1.freeze()

        self.assert_(p1.hash() == h)

    def testhashes_14_frozen_consistency(self):
        p1 = sample_tree()
        p1.z.a.b.c = 123

        h = p1.hash()
        p1.z.a.freeze()

        self.assert_(p1.hash() == h)

    def testhashes_15_attaching(self):
        p1 = makeTDInstance('root')
        p1.b1 = makeTDInstance('b1')

        h = p1.hash()

        p1.attach(copy = False, recursive = True)
        
        self.assert_(p1.hash() != h)

    def testhashes_15_attaching(self):
        p1 = makeTDInstance('root')
        p1.b1 = makeTDInstance('b1')
        p1.b1.b2 = makeTDInstance('b2')

        h = p1.hash()

        p1.b1.attach(copy = False, recursive = True)
        
        self.assert_(p1.hash() != h)
        
    def testhashes_16_pythonkeys(self):
        p1 = makeTDInstance()
        p1.a.b = 123

        def f(): return {p1 : 0}

        self.assertRaises(TypeError, f)

        p1.freeze()

        # Should work now
        d = {p1 : 0}


    def testhashes_17_pythonkeys(self):
        p1 = makeTDInstance()
        p1.a.b = [123, 43]
        p1.freeze()

        def f(): return {p1 : 0}

        self.assertRaises(TypeError, f)

    def testhashes_18_EqualityTesting_01(self):
        p = sample_tree()
        p1 = p.copy(deep=True)
        p2 = p.copy(deep=True)

        self.assert_(p1 == p2)
        self.assert_(p1.hash() == p2.hash())

        p1.mydict = {1 : 2}
        p2.mydict = {1 : 3}

        self.assert_(p1 != p2)
        self.assert_(p1.hash() != p2.hash())

    def testhashes_19_Keys_01_reversing(self):
        p = makeTDInstance(a = 1, b = 2, c = 3)
        self.assert_(p.hash(keys=['a', 'b']) == p.hash(keys=['b', 'a']))

    def testhashes_19_Keys_02_full(self):
        p = makeTDInstance(a = 1, b = 2, c = 3)
        self.assert_(p.hash(keys=['a', 'b', 'c']) == p.hash())

    def testhashes_19_Keys_03_single(self):
        p = makeTDInstance(a = 1, b = 2, c = 3)
        self.assert_(p.hash(keys=['a']) == p.hash('a'))

    def testhashes_19_Keys_04_nonintersection(self):
        p = makeTDInstance(a = 1, b = 2, c = 3)
        self.assert_(p.hash(keys=['a', 'b']) != p.hash(keys=['a','c']))

    def testhashes_20a_infinite_recursion_raises_error(self):
        p = makeTDInstance()

        p.makeBranch("a")

        p.a.b.c = p.a

        self.assertRaises(RuntimeError, lambda: p.hash())
        
    def testhashes_20b_infinite_recursion_raises_error__frozen(self):
        p = makeTDInstance()

        p.makeBranch("a")

        p.a.b.c = p.a

        p.freeze()

        self.assertRaises(RuntimeError, lambda: p.hash())


    def testHashError_01(self):

        p = makeTDInstance()

        p.a.b = lambda: None

        self.assertRaises(HashError, lambda: p.hash())

        try:
            p.hash()
        except HashError as he:
            self.assert_(he.key == 'a.b', he.key)
        
    def testHashError_02(self):

        p = makeTDInstance()

        p.a.b = [lambda: None]

        self.assertRaises(HashError, lambda: p.hash())

        try:
            p.hash()
        except HashError as he:
            self.assert_(he.key == 'a.b', he.key)

    def testHashError_03(self):

        p = makeTDInstance()

        p.a.b = {'a' : lambda: None}

        self.assertRaises(HashError, lambda: p.hash())

        try:
            p.hash()
        except HashError as he:
            self.assert_(he.key == 'a.b', he.key)

    def testHashError_05_custom(self):

        p = makeTDInstance()

        class HType:
            def __init__(self):
                self.h = 1

            def __treedict_hash__(self):
                self.h += 1
                return self.h

        p.a.b.c = HType()

        self.assert_(p.hash() != p.hash())




if __name__ == '__main__':
    unittest.main()

