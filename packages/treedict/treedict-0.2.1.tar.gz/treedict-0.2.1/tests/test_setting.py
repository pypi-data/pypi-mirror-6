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
from treedict import TreeDict, getTree
import treedict
from copy import deepcopy, copy

from hashlib import md5
import random

from common import *

class TestSetting(unittest.TestCase):

    def test_Frozen(self):
        p = sample_tree()
        p.freeze()
        self.assertRaises(TypeError, lambda: p.set("asdf", 0))

    def testSetGet01(self):
        p = sample_tree()

        p.set("aabsd", 123)

        self.assert_(p.aabsd == 123)

    def testSetGet02(self):
        p = sample_tree()
        p.a = 123

        self.assert_(p.get("a") == 123)

    def testSetGet03(self):
        p = makeTDInstance()
        p.a.b.c.d.e.f = 1
        self.assert_(p.get("a.b.c.d.e.f") == 1)

    def testSetGet04(self):
        p = sample_tree()
        p.set("b.c", 123)

        self.assert_(p.get("b.c") == 123)

    def testSetGet04b(self):
        p = sample_tree()
        p.makeBranch("b")
        p.set("b.c", 123)

        self.assert_(p.get("b.c") == 123)

    def testSetGet05(self):
        p = getTree('a_s3kkdf93kd9k3ikdkmd') # unique
        p.a.b.c.d.e.f = 1
        self.assert_(p.get("a.b.c.d.e.f") == 1)

    def testSetGet06(self):

        # regression test
        p = getTree('upt_08_bcg1_')
        p.a18462.a1732643.x = 1
        q = p.a18462.copy()
        q.a1732643.a1232 = "borkbork"  # should be bad

        self.assert_(p.a18462.a1732643.x == 1)
        self.assert_(q.a1732643.a1232 == "borkbork")
        self.assert_(q.a1732643.x == 1)

    def testSetGet07(self):

        # Regression
        p = getTree('upt_08_bcg2_whodunit_')
        self.assert_(not p.isFrozen())
        p.a18462.a1732643.x = 1
        q = p.a18462.a1732643.copy()
        q.a1232 = "borkbork"

        self.assert_(p.a18462.a1732643.x == 1)
        self.assert_(q.a1232 == "borkbork")
        self.assert_(q.x == 1)


    ############################################################
    # Testing more advanced functionality of the set() method

    def testSet_01(self):
        p = sample_tree()
        v1 = (1,2,3)

        p.set("a.b", v1)
        self.assert_(p.a.b is v1)

    def testSet_02(self):
        p = sample_tree()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.set("a.b", v1, "a.c", v2)
        self.assert_(p.a.b is v1)
        self.assert_(p.a.c is v2)

    def testSet_03_SetOrder(self):
        p = sample_tree()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.set("a.b", v1, "a.b", v2)
        self.assert_(p.a.b is v2)

    def testSet_04_mixKWargs(self):
        p = sample_tree()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.set("a.b", v1, **{"b" : v2})

        self.assert_(p.a.b is v1)
        self.assert_(p.b is v2)

    def testSet_05_kwargs(self):
        p = sample_tree()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.set(**{"a" : v1, "b" : v2})

        self.assert_(p.a is v1)
        self.assert_(p.b is v2)

    def testSet_05b_kwargs(self):
        p = sample_tree()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.set(a = v1, b = v2)

        self.assert_(p.a is v1)
        self.assert_(p.b is v2)

    def testSet_06_kwargs_large_dict(self):
        d = {}

        for i in range(10000):
            d["a%d" % i] = i

        p = sample_tree()

        p.set(**d)

        for i in range(10000):
            self.assert_(p["a%d" % i] == i)

    def testSet_07_kwargs_precedence(self):
        p = sample_tree()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.set("a", v1, a = v2)

        # Keyword arguments
        self.assert_(p.a is v2)

    def testSet_08_validation_first(self):
        p = sample_tree()
        v1 = (1,2,3)

        try:
            p.set("a", v1, "0123", v2)
        except Exception:
            pass

        self.assert_("a" not in p)

    def testSet_09_validation_first(self):
        p = sample_tree()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.a = v1

        try:
            p.set("a", v2, "0123", None)
        except Exception:
            pass

        self.assert_(p.a is v1)

    def testSet_10_validation_first(self):
        p = makeTDInstance()
        v1 = (1,2,3)
        v2 = (3,2,1)

        p.a = v1

        p1 = deepcopy(p)

        try:
            p.set("a", v2, "0123", None)
        except Exception:
            pass

        self.assert_(p.a is v1)
        self.assert_(p1 == p)

    def testSet_11_validation_first(self):
        d = {}

        tn = unique_name()

        for i in range(10000):
            d["a%d" % i] = i

        p = treedict.getTree(tn)

        p1 = deepcopy(p)

        self.assert_(p1 == p)

    def testSet_12_bad_args(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.set('a', 1, None, 1))

    def testSet_13_bad_args(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.set('a', 1, 123, 1))

    def testSet_14_bad_args(self):
        p = sample_tree()
        self.assertRaises(NameError, lambda: p.set('a', 1, '', 1))

    def testSet_15_bad_args(self):
        p = sample_tree()
        self.assertRaises(NameError, lambda: p.set('a', 1, '123', 1))

    def testSet_16_bad_args(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.set('a', 1, 'abc'))

    def testSet_17_bad_args(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.set('a'))

    def testSet_19_overwriting_value_with_branch_01_okay(self):
        p = makeTDInstance()

        p.a = 12

        p.set("a.b.c", 1, protect_values=False)

        self.assert_(p.a.b.c == 1)

    def testSet_19_overwriting_value_with_branch_02_nochange_on_bad(self):
        p = makeTDInstance()

        p.a = 12

        pc = p.copy()

        self.assertRaises(NameError, lambda: p.set("a.b.c.123.d", 1, protect_structure = False))

        self.assert_(p.a == 12)
        self.assert_(p == pc)

    def testSet_19_overwriting_value_with_branch_03_error(self):
        p = makeTDInstance()

        p.a = 12

        self.assertRaises(TypeError, lambda: p.set("a.b.c", 1, protect_structure = True))

    def testSet_20_setting_linked_branch_01(self):
        p = makeTDInstance()

        p.a = p.defs.a1

        p.defs.a1.v = 1

        self.assert_(p.a.v == 1)

    def testSet_20_setting_linked_branch_02(self):
        p = makeTDInstance()

        p.a = p.defs.a1

        p.set("defs.a1.v", 1)

        self.assert_(p.a.v == 1)

    def testSet_21_Setting_ThroughmakeTDInstance_01(self):
        p = makeTDInstance()

        p.a.b = makeTDInstance()

        p.set("a.b.c.d.x", 1)

        self.assert_(p.a.b.c.d.x == 1)
        self.assert_(p.a.b.isRoot())

    def testSet_21_Setting_ThroughmakeTDInstance_02(self):
        p = makeTDInstance()
        p.a.b = makeTDInstance()
        p["a.b.c.d.x"] = 1

        self.assert_(p.a.b.c.d.x == 1)
        self.assert_(p.a.b.isRoot())

    def testSetInit_01(self):
        p = makeTDInstance(a = 1, b = 2)
        self.assert_(p.a == 1)
        self.assert_(p.b == 2)


    def testSet_30_ValueFrozen_01(self):
        p = makeTDInstance(a = 1, b = 2)
        p.freeze(values_only = True)

        p.c = 3


    def testSet_30_ValueFrozen_02(self):
        p = makeTDInstance(a = 1)
        p.freeze(values_only = True)

        self.assertRaises(TypeError, lambda: p.set('a', 2))

    def testSet_30_ValueFrozen_03(self):
        p = makeTDInstance()
        p.a.b = 1
        p.freeze(values_only = True)

        p.a.c = 3

    def testSet_30_ValueFrozen_04(self):
        p = makeTDInstance()
        p.a.b = 1
        p.freeze(values_only = True)

        self.assertRaises(TypeError, lambda: p.set('a', 2))

    def testSet_30_ValueFrozen_05(self):
        p = makeTDInstance()
        p.a.b = 1
        p.a.freeze(values_only = True)

        p.a = 2

    def testSet_30_ValueFrozen_06_proper_Exception(self):
        p = makeTDInstance()
        self.assertRaises(ValueError, lambda: p.freeze(structure_only = True, values_only = True))

    def testSet_30_ValueFrozen_07(self):
        p = makeTDInstance()
        p.a.b.c = 1
        p.freeze(values_only = True)

        self.assertRaises(TypeError, lambda: p.set('a.b', None) )

    ############################################################
    # Testing the checkset function

    def testDrySet_01(self):
        p = sample_tree()
        p1 = p.copy(deep = True)
        p2 = p.copy(deep = True)

        p1.checkset(a = 123)

        self.assert_(p1 == p2)

    def testDrySet_02(self):
        p1 = sample_tree().copy(deep=True)

        p1.v = 100
        p1.a.b.c = 100

        p2 = deepcopy(p1)

        p1.checkset(v = 123)

        self.assert_(p1.v != 123)
        self.assert_(p1.v == 100)
        self.assert_(p1 == p2)

    def testDrySet_03(self):
        p = sample_tree()

        p1 = p.copy(deep=True)
        p2 = p.copy(deep=True)

        p1.checkset("a.b.c.d", 123)

        self.assert_(p1 == p2)

    def testDrySet_04_value_overwrite(self):
        p = makeTDInstance()
        p.b = 1

        p_before = p.copy()

        self.assertRaises(TypeError, lambda: p.checkset("b.a", None, protect_structure = True))

        self.assert_(p_before == p)

    def testDrySet_05_makeBranch_Frozen(self):
        p = makeTDInstance()
        p.makeBranch('b')
        p.b.freeze()

        p_before = p.copy()

        self.assertRaises(TypeError, lambda: p.checkset("b.a", None))

        self.assert_(p_before == p)

    def testDrySet_06_makeBranch_Frozen_StructureOnly(self):
        p = makeTDInstance()
        p.makeBranch('b')
        p.b.freeze(structure_only = True)

        p_before = p.copy()

        self.assertRaises(TypeError, lambda: p.checkset("b.a", None))

        self.assert_(p_before == p)

    def testDrySet_07_makeBranch_Frozen_StructureOnly_Okay(self):
        p = makeTDInstance()
        p.b.a = 1
        p.b.freeze(structure_only = True)

        p_before = p.copy()
        p.checkset('b.a', 2)

        self.assertRaises(TypeError, lambda: p.checkset("b.b", None))

        self.assert_(p.b.a == 1)

        self.assert_(p_before == p)

    def testDrySet_08_makeBranch_Frozen_StructureOnly_Okay(self):
        p = makeTDInstance()
        p.b.a = 1
        p.b.freeze(structure_only = True)

        p_before = p.copy()
        p.checkset('b.a', 2)

        self.assert_(p.b.a == 1)

        self.assert_(p_before == p)

    def testDrySet_10_makeBranch_Frozen_ValuesOnly_01(self):
        p = makeTDInstance()
        p.b.a = 1
        p.freeze(values_only = True)

        p_before = p.copy()

        self.assertRaises(TypeError, lambda: p.checkset("b.a", 2))

        self.assert_(p_before == p)

    def testDrySet_10_makeBranch_Frozen_ValuesOnly_01b(self):
        p = makeTDInstance()
        p.b.a = 1
        p.b.freeze(values_only = True) # only freeze branch, checkset from base

        p_before = p.copy()

        self.assertRaises(TypeError, lambda: p.checkset("b.a", 2))

        self.assert_(p_before == p)

    def testDrySet_10_makeBranch_Frozen_ValuesOnly_02(self):
        p = makeTDInstance()
        p.b.a = 1
        p.b.freeze(structure_only = True)

        p_before = p.copy()

        p.checkset("c.a", 2)

        self.assert_(p_before == p)

    ############################################################
    # Setting arguments from string

    def testSetFromString_01(self):
        p = sample_tree()

        self.assert_(p.setFromString("a", "(0,1,2)"))
        self.assert_(p.a == (0,1,2))

    def testSetFromString_02(self):
        p = sample_tree()

        self.assert_(p.setFromString("a", "'string'"))
        self.assert_(p.a == 'string')

    def testSetFromString_03(self):
        p = sample_tree()

        self.assert_(p.setFromString("a", "123 + 345"))
        self.assert_(p.a == 123 + 345)

    def testSetFromString_04(self):
        p = sample_tree()

        self.assert_(not p.setFromString("a", "123 345"))
        self.assert_(p.a == "123 345")

    def testSetFromString_05(self):
        p = sample_tree()

        self.assert_(p.setFromString("a", "x/2", {"x" : 4}))
        self.assert_(p.a == 2)


    ################################################################################
    # Testing the dict interface

    def testSet_nochange_on_failure(self):
        p = sample_tree()

        p1 = p.copy(deep=True)
        p2 = p.copy(deep=True)

        def f():
            p1.set("a.b.c.d.123", 1)

        self.assertRaises(NameError, f)

        self.assert_(p1 == p2)

    def testDictSet_nochange_on_failure(self):
        p = sample_tree()

        p1 = p.copy(deep=True)
        p2 = p.copy(deep=True)

        def f():
            p1["a.b.c.d.123"] = 1

        self.assertRaises(NameError, f)

        self.assert_(p1 == p2)

    def testFromKeys_01_setting(self):

        key_iterable = ["a", "b", "cdef"]

        p = TreeDict.fromkeys(key_iterable)

        for n in key_iterable:
            self.assert_(p.get(n) is None)


    def testFromKeys_02_setting(self):
        v = ["asdf"]

        key_iterable = ["a", "b", "cdef"]

        p = TreeDict.fromkeys(key_iterable, v)

        for n in key_iterable:
            self.assert_(p.get(n) is v)


    def testFromKeys_03_checking_01(self):

        key_iterable = ["alphabet", 123]

        def f():
            TreeDict.fromkeys(key_iterable)

        self.assertRaises(TypeError, f)

    def testFromKeys_03_checking_02(self):

        key_iterable = "alphabet1"

        def f():
            p = TreeDict.fromkeys(key_iterable)

        self.assertRaises(NameError, f)

    def testFromKeys_04_nochangetostring(self):

        p = sample_tree()
        key_iterable = ["abcdefg"]

        p.fromkeys(key_iterable)

        self.assert_(p == sample_tree())

    # Add in fromdict testing here

    def testFromDict_01(self):
        t = TreeDict.fromdict({'a.x' : 1, 'a.y' : 2, 'z' : 3})

        t2 = makeTDInstance()
        t2.z = 3
        t2.a.x = 1
        t2.a.y = 2

        self.assert_(t == t2)

    def testFromDict_02(self):
        t = TreeDict.fromdict({'a' : {'x' : 1, 'y' : 2}, 'z' : 3},
                              expand_nested = True)

        t2 = makeTDInstance()
        t2.z = 3
        t2.a.x = 1
        t2.a.y = 2

        self.assert_(t == t2)

    def testFromDict_03_root_linked(self):

        # A self-referencing dictionary
        d = {}
        d['a'] = d

        t = TreeDict.fromdict(d, expand_nested = True)

        self.assert_(t.a is t)

    def testOrdering_01(self):
        t = makeTDInstance()

        t.a = 1
        t.b = 2

        self.assert_(t._getSettingOrderPosition('a') == (0,), t._getSettingOrderPosition('a'))
        self.assert_(t._getSettingOrderPosition('b') == (1,), t._getSettingOrderPosition('b'))

    def testOrdering_02(self):

        t = makeTDInstance()

        t.a   = 1
        t.b.c = 2
        t.x.y = 3
        t.b.a = 4

        self.assert_(t._getSettingOrderPosition('a') == (0,),  t._getSettingOrderPosition('a'))
        self.assert_(t._getSettingOrderPosition('b') == (1,), t._getSettingOrderPosition('b'))
        self.assert_(t._getSettingOrderPosition('x') == (2,), t._getSettingOrderPosition('x'))
        self.assert_(t._getSettingOrderPosition('b.c') == (1,0), t._getSettingOrderPosition('b.c'))
        self.assert_(t._getSettingOrderPosition('b.a') == (1,1), t._getSettingOrderPosition('b.a'))
        self.assert_(t._getSettingOrderPosition('x.y') == (2,0), t._getSettingOrderPosition('x.y'))

if __name__ == '__main__':
    unittest.main()

