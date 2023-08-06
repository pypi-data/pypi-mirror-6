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

class TestAttachPop(unittest.TestCase):

    def testAttaching_01(self):
        p1 = makeTDInstance('root')
        p2 = makeTDInstance('node')

        p2.a = 123
        p1.attach(p2)

        self.assert_(p1.node.a == 123)
        self.assert_(p1.node.rootNode() is p1)
        self.assert_(p2.rootNode() is p2)

    def testAttaching_02(self):
        p1 = makeTDInstance('root')
        p2 = makeTDInstance('node')

        p2.a = 123
        p1.attach(p2, copy=False)

        self.assert_(p1.node.a == 123)
        self.assert_(p1.node.rootNode() is p1)
        self.assert_(p1.node is p2)
        self.assert_(p2.rootNode() is p1)

    def testAttaching_03(self):
        p1 = makeTDInstance('root')
        p2 = makeTDInstance('node')

        p2.a = 123
        p1.attach('attachnode', p2)

        self.assert_(p1.attachnode.a == 123)
        self.assert_(p1.attachnode.rootNode() is p1)
        self.assert_(p1.attachnode == p2)
        self.assert_(p1.attachnode.branchName(True,True) == "root.attachnode")
        self.assert_(p2.rootNode() is p2)

    def testAttaching_04(self):
        p1 = makeTDInstance('root')
        p2 = makeTDInstance('node')

        p2.a = 123
        p1.attach('attachnode', p2, copy=False)

        self.assert_(p1.attachnode.a == 123)
        self.assert_(p1.attachnode.rootNode() is p1)

        self.assert_(p1.attachnode == p2)
        self.assert_(p1.attachnode.branchName(True,True) == "root.attachnode")
        self.assert_(p2.branchName(True,True) == "root.attachnode")
        self.assert_(p2.rootNode() is p1)

    def testAttaching_05(self):
        p1 = makeTDInstance('root')
        p1.a.b = 123

        self.assertRaises(ValueError, lambda: p1.a.attach(p1))

    def testAttaching_06(self):
        p1 = makeTDInstance('root')
        p1.a.b.c = 123

        def f(): p1.attach(p1.a.b, copy=False)

        self.assertRaises(ValueError, f)

    def testAttaching_07(self):
        p1 = makeTDInstance('root')
        p1.a.n.v = 123
        p1.b.n.v = 421

        p1.a.attach('m', p1.b.n)

    def testAttaching_08(self):

        p1 = makeTDInstance('root')
        p1.a.n.v = 123
        p1.b.n.v = 421

        def f(): p1.a.attach(p1.a.n, copy=False)

        self.assertRaises(ValueError, f)

    def testAttaching_09_frozen_1(self):
        p = makeTDInstance('p')
        p.b.c = 1
        p.freeze()

        p2 = makeTDInstance()
        p2.attach(p, copy=False)

        self.assert_(p2.p.b.c == 1)
        self.assert_(p2.p.isFrozen())
        self.assert_(p2.p.b.isFrozen())
        self.assert_(not p2.isFrozen())

    def testAttaching_09_frozen_2(self):
        p = makeTDInstance('p')
        p.b.c = 1
        p.freeze()

        p2 = makeTDInstance()
        p2.attach(p, copy=True)

        self.assert_(p2.p.b.c == 1)
        self.assert_(not p2.p.isFrozen())
        self.assert_(not p2.p.b.isFrozen())
        self.assert_(not p2.isFrozen())

    def testAttaching_10_Atomic_01_noImplicitOverwrite(self):
        p = makeTDInstance()
        p.a.b = 1

        self.assertRaises(TypeError, lambda: p.attach("a.b.c.d", makeTDInstance(x = 1),
                                                      protect_structure=True))

        self.assert_(p.a.b == 1)

    def testAttaching_10_Atomic_02_noImplicitOverwrite(self):
        p = makeTDInstance()
        p.makeBranch('a')
        p.freeze()

        self.assert_('a' in p.keys(branch_mode = 'only', recursive=False))

        self.assertRaises(TypeError, lambda: p.attach("a.b.c.d", makeTDInstance(x = 1),
                                                      protect_structure=True))

        self.assert_('a' in p.keys(branch_mode = 'only', recursive=False))

        self.assert_(p.a.size() == 0)

    def testAttaching_11_BadParameters_01(self):

        p = makeTDInstance()

        self.assertRaises(TypeError, lambda: p.attach(makeTDInstance(), "name"))

    def testAttaching_11_BadParameters_02(self):
        p = makeTDInstance()
        self.assertRaises(TypeError, lambda: p.attach(makeTDInstance(), makeTDInstance()))

    def testAttaching_11_BadParameters_03(self):
        p = makeTDInstance()
        self.assertRaises(TypeError, lambda: p.attach(copy = True))

    def testAttaching_11_BadParameters_04(self):
        p = makeTDInstance()
        self.assertRaises(TypeError, lambda: p.attach(copy = False))

    def testRecursiveAttach_01(self):
        p1 = makeTDInstance('root')
        p1.b1 = makeTDInstance('new_branch')
        p1.b1.b2 = makeTDInstance('new_branch')
        p1.b1.b2.b3 = makeTDInstance('new_branch')

        self.assert_(p1.b1.isRoot())
        self.assert_(p1.b1.b2.isRoot())
        self.assert_(p1.b1.b2.b3.isRoot())
        self.assert_(p1.b1.branchName(True,True) == 'new_branch')
        self.assert_(p1.b1.b2.branchName(True,True) == 'new_branch')
        self.assert_(p1.b1.b2.b3.branchName(True,True) == 'new_branch')

        p1.attach(copy=True, recursive=True)

        self.assert_(p1.b1.rootNode() is p1)
        self.assert_(p1.b1.b2.rootNode() is p1)
        self.assert_(p1.b1.b2.b3.rootNode() is p1)
        self.assert_(p1.b1.branchName(True,True) == 'root.b1')
        self.assert_(p1.b1.b2.branchName(True,True) == 'root.b1.b2')
        self.assert_(p1.b1.b2.b3.branchName(True,True) == 'root.b1.b2.b3')

    def testRecursiveAttach_02(self):
        p1 = makeTDInstance('root')
        p1.b1 = makeTDInstance('new_branch')
        p1.b1.b2 = makeTDInstance('new_branch')
        p1.b1.b2.b3 = makeTDInstance('new_branch')

        self.assert_(p1.b1.isRoot())
        self.assert_(p1.b1.b2.isRoot())
        self.assert_(p1.b1.b2.b3.isRoot())

        self.assert_(p1.b1.branchName(True,True) == 'new_branch')
        self.assert_(p1.b1.b2.branchName(True,True) == 'new_branch')
        self.assert_(p1.b1.b2.b3.branchName(True,True) == 'new_branch')

        p1.attach(copy=False, recursive=True)

        self.assert_(p1.b1.rootNode() is p1)
        self.assert_(p1.b1.b2.rootNode() is p1)
        self.assert_(p1.b1.b2.b3.rootNode() is p1)

        self.assert_(p1.b1.branchName(True,True) == 'root.b1')
        self.assert_(p1.b1.b2.branchName(True,True) == 'root.b1.b2')
        self.assert_(p1.b1.b2.b3.branchName(True,True) == 'root.b1.b2.b3')

    def testRecursiveAttach_03_recursive_with_linked_nodes(self):
        p = makeTDInstance()

        p.a = p.adef.a
        p.adef.a.v = 1

        p.attach(recursive=True)

    def testRecursiveAttach_04_error_on_frozen(self):

        p = makeTDInstance()
        p.b = makeTDInstance(x = 1)
        p.freeze()

        self.assertRaises(TypeError, lambda: p.attach(recursive = True))

        self.assert_(p.b.isRoot())
        self.assert_(p.b not in p.branches())
        self.assert_(p.size() == 1)

    def testRecursiveAttach_05_ValueFrozen(self):
        # Disable; not sure it's best anyway
        return

        p1 = makeTDInstance('root')
        p1.b1 = makeTDInstance('new_branch')

        p1.freeze(values_only = True)

        self.assert_(p1.b1.isRoot())
        self.assert_(p1.b1.branchName(True,True) == 'new_branch')

        p1.attach(copy=True, recursive=True)

        self.assert_(p1.b1.rootNode() is p1)
        self.assert_(p1.b1.branchName(True,True) == 'root.b1')

    # This one would be a lot of work to fix, for what gain?

    # def testRecursiveAttaching_05_no_error_on_okay_frozen(self):

    #     p = makeTDInstance()
    #     p.b.x = 1
    #     p.freeze()

    #     p.attach(recursive = True)


    def testAttaching_10_EqualityTestingWithRecursiveAttach(self):

        p1 = makeTDInstance('root')
        p1.b1 = makeTDInstance('new_branch')
        p1.b1.b2 = makeTDInstance('new_branch')
        p1.b1.b2.b3 = makeTDInstance('new_branch')

        p2 = p1.copy()

        self.assert_(p2 == p1)

        p1.attach(copy=False, recursive=True)

        self.assert_(p2 != p1)

    def testAttaching_11_equalityTesting_01(self):

        p1 = makeTDInstance('root')
        p1.b1 = makeTDInstance('new_branch')
        p1.b1.b2 = makeTDInstance('new_branch')
        p1.b1.b2.b3 = makeTDInstance('new_branch')

        p2 = p1.copy()

        self.assert_(p2 == p1)

        p1.attach(copy=False, recursive=True)

        self.assert_(p2 != p1)

    def testAttaching_12_propegatingFrozenFlags(self):
        p1 = makeTDInstance()

        p1.a.b = makeTDInstance()

        p1.freeze(values_only = True)

        p1.attach('c', makeTDInstance() )

        self.assert_(p1.c.valuesAreFrozen())


    def testDetaching_01(self):
        p1 = makeTDInstance('root')
        p1.node.a = 123
        p1.node.b = "12312321"
        p1.node2.a = 13
        p1.node3.a = "123312"
        p1.node4 = 123

        p1copy = deepcopy(p1)

        p2 = p1.node

        p3 = p1.pop("node")

        self.assert_(p2 is p3)
        self.assert_(p3.rootNode() is p3)
        self.assert_("node" not in p1)
        self.assert_(p2 == p1copy.node)
        self.assert_(p1 != p1copy)


    def testDetaching_02(self):

        # This covers the corner case of no elements remaining.
        p1 = makeTDInstance('root')
        p1.node.a = 123
        p1copy = deepcopy(p1)

        p2 = p1.node

        p3 = p1.pop("node")

        self.assert_(p2 is p3)
        self.assert_(p3.rootNode() is p3)
        self.assert_("node" not in p1)
        self.assert_(p2 == p1copy.node)
        self.assert_(p1 != p1copy)

    def testDetaching_03_Dangling_AttributeError(self):

        p = makeTDInstance()

        def f():
            q = p.a.b.pop()

        self.assertRaises(AttributeError, f)

    def testDetaching_04_dangling_AttributeError_correct_node(self):

        p = makeTDInstance()
        ae_msg = ''

        try:
            q = p.aduvulksjucmfiddkjdo.b.pop()
        except AttributeError as ae:
            ae_msg = str(ae)

        # Make sure it propegates up so the error message is sent from
        # the root dangling node.
        self.assert_('aduvulksjucmfiddkjdo' in ae_msg)


    def testDetach_05_self(self):
        p = makeTDInstance()

        p.a.b.c.d = 1

        b = p.a.b

        bd = p.a.b.pop()

        self.assert_(b is bd)
        self.assert_('a' in p)
        self.assert_('a.b' not in p)
        self.assert_(b.parentNode() == None)


    def testDetach_06_complex_key(self):
        p = makeTDInstance()
        p.a.b.c.d = 1
        b = p.a.b

        bd = p.pop('a.b')

        self.assert_(b is bd)
        self.assert_('a' in p)
        self.assert_('a.b' not in p)
        self.assert_(b.parentNode() == None)

    def testDetach_07_nonbranch(self):
        # Test to make sure the behavior is like pop() (perhaps we
        # should chang the name ??)

        p = makeTDInstance()
        p.a = 1

        v = p.pop('a')

        self.assert_(v == 1)
        self.assert_('a' not in p)


    def testDetach_08_nonbranch_complex(self):
        # Test to make sure the behavior is like pop() (perhaps we
        # should chang the name ??)

        p = makeTDInstance()
        p.a.b.c = 1

        v = p.pop('a.b.c')

        self.assert_(v == 1)
        self.assert_('a' in p)
        self.assert_('a.b' in p)
        self.assert_('a.b.c' not in p)
        self.assert_('c' not in p.a.b)

    def testClear_01_all(self):
        p, rid = basic_walking_test()
        p = p.copy()
        p.clear("all")

        self.assert_(len(p) == 0)

    def testClear_02_branches_only(self):
        p, rid = basic_walking_test()
        p = p.copy()

        p.clear("only")

        self.assert_(len(p) == len(rid[(False, "none")]))

        for k, v in rid[(False, "none")]:
            self.assert_(k in p)

    def testClear_03_branches_none(self):
        p, rid = basic_walking_test()

        p = p.copy()

        p.clear("none")

        self.assert_(len(p) == len(rid[(False, "only")]))

        for k, v in rid[(False, "only")]:
            self.assert_(k in p)

    def testClear_04_IsFrozenError(self):

        p = sample_tree()

        p.freeze()

        self.assertRaises(TypeError, lambda: p.clear())

    def testClear_05_IsDanglingError(self):

        p = sample_tree()

        self.assertRaises(AttributeError, lambda: p.a.clear())


class TestBranches(unittest.TestCase):

    def testBranch_01_basic(self):
        p = makeTDInstance()
        p.makeBranch('b')
        self.assert_('b' in p)
        self.assert_(not p.b.isDangling())

    def testBranch_02_ReturnsCorrectBranch(self):
        p = makeTDInstance()
        b = p.makeBranch('b')

        self.assert_(p.b is b)

    def testBranch_02b_ReturnsCorrectBranch(self):
        p = makeTDInstance()
        b = p.makeBranch('a').makeBranch('b')

        self.assert_(p.a.b is b)

    def testBranch_02c_ReturnsCorrectBranch(self):
        # Regression

        p = makeTDInstance()
        a = p.makeBranch('a')
        p.a.b

        self.assert_(p.a is a)

    def testBranch_03_KeyedValues(self):
        p = makeTDInstance()
        b = p.makeBranch('a.b.c')

        self.assert_(p.a.b.c is b)

    def testBranch_04_ReturnsCorrectBranch(self):
        p = makeTDInstance()
        b = p.makeBranch('b')

        self.assert_(p.b is b)

    def testBranch_05_Overwrite(self):
        # Decided this is okay

        p = makeTDInstance()
        p.d.a = 1
        p.d = 1


    def testBranch_05_BranchFunction(self):
        p = makeTDInstance()

        b = p.makeBranch("a")

        self.assert_(b is p.a)

    def testBranch_06_Branch_Sets_Dangling(self):

        p = makeTDInstance()

        b = p.a

        self.assert_("a" not in p)
        self.assert_(p.a.isDangling())

        b.makeBranch("b")

        self.assert_(not p.a.isDangling())
        self.assert_("a.b" in p)

    def testBranch_07_makeTDInstance_Values_Not_Frozen(self):

        p = makeTDInstance()
        p.a.x = 1
        p.c.t = makeTDInstance()
        p.c.t.x = 1

        self.assert_(not p.isFrozen())
        self.assert_(not p.a.isFrozen())
        self.assert_(not p.c.isFrozen())
        self.assert_(not p.c.t.isFrozen())

        p.freeze()

        self.assert_(p.isFrozen())
        self.assert_(p.a.isFrozen())
        self.assert_(p.c.isFrozen())
        self.assert_(not p.c.t.isFrozen())

    def testBranchStructureFrozen_01(self):

        p = makeTDInstance()
        p.a = makeTDInstance(x = 1)
        p.freeze(structure_only = True)

        self.assertRaises(TypeError, lambda: p.attach(recursive = True))


    def testBranchAllowedWhenValueFrozen_01(self):

        p = makeTDInstance()
        p.freeze(values_only = True)

        p.a.b = 1

    def testBranchHasValuePropegationFlags_01(self):

        p = makeTDInstance()
        p.a = 1
        p.freeze(values_only = True)
        p.b.c = 2

        self.assert_(p.b.valuesAreFrozen())

    def testBranchHasValuePropegationFlags_02(self):

        p = makeTDInstance()
        p.a = 1
        p.freeze(values_only = True)
        p.makeBranch('b')

        self.assert_(p.b.valuesAreFrozen())


class TestDangling(unittest.TestCase):

    def testDangling_01_BranchOverwrite(self):

        p1 = sample_tree()
        p1.a

        self.assert_("a" not in p1)

        p1.a.b = 2

        self.assert_("a" in p1)
        self.assert_(p1.a.b == 2)

    def testDangling_02_NotRetrieved(self):
        self.assertRaises(KeyError, lambda: makeTDInstance()["a"])


    def testDangling_03_OutOfOrderSetting(self):
        p = makeTDInstance()

        c = p.a.c
        d = p.a.d

        c.v = 1
        d.v = 2

        self.assert_('a.c.v' in p)
        self.assert_('a.d.v' in p)

        self.assert_(p.a.c.v == 1)
        self.assert_(p.a.d.v == 2)


    def testDangling_04_OutOfOrderSetting_same_names(self):
        p = makeTDInstance()

        c1 = p.a.c
        c2 = p.a.c

        self.assert_(c1 is c2)

        c1.v = 1
        c2.v = 2

        self.assert_('a.c.v' in p)
        self.assert_(p.a.c.v == 2)

    def testDangling_05_Retrieval(self):
        # tests to make sure that dangling nodes are retrieved properly

        p = makeTDInstance()

        self.assert_(p.a is p.a)


    def testDangling_06_Retrieval_SecondOrder(self):
        # tests to make sure that dangling nodes are retrieved properly

        p = makeTDInstance()

        self.assert_(p.a.b is p.a.b)

    def testDangling_07_Existance_01(self):
        p = makeTDInstance()

        p.a

        self.assert_('a' not in p)

    def testDangling_08_Freezing_01(self):
        p = makeTDInstance()

        b = p.a.b

        p.freeze()

        def f():
            b.v = 1

        self.assertRaises(TypeError, f)

    def testDangling_08_Freezing_02(self):
        p = makeTDInstance()

        b = p.a.b

        del p['a']

        p.freeze()

        # Okay now as it's disconnected from b
        b.v = 1

    def testDangling_09_Count_01(self):
        p = makeTDInstance()
        self.assert_(p._numDangling() == 0)
        p.a
        self.assert_(p._numDangling() == 1)

    def testDangling_09_Count_02(self):
        p = makeTDInstance()
        self.assert_(p._numDangling() == 0)
        p.a.b
        self.assert_(p._numDangling() == 1)

    def testDangling_09_Count_03_Deletion(self):
        p = makeTDInstance()
        self.assert_(p._numDangling() == 0)
        p.a
        self.assert_(p._numDangling() == 1)
        del p.a
        self.assert_(p._numDangling() == 0)

    def testDangling_09_Count_03b_Deletion(self):
        p = makeTDInstance()
        self.assert_(p._numDangling() == 0)
        p.a
        self.assert_(p._numDangling() == 1)
        del p["a"]
        self.assert_(p._numDangling() == 0)

    def testDangling_09_Count_04_Branching(self):
        p = makeTDInstance()
        self.assert_(p._numDangling() == 0)
        p.a
        self.assert_(p._numDangling() == 1)
        p.makeBranch("a")
        self.assert_(p._numDangling() == 0)

    def testDangling_09_Count_05_Branching(self):
        p = makeTDInstance()
        p.makeBranch("a")
        self.assert_(p._numDangling() == 0)

    def testDangling_09_Count_06_Branching(self):
        p = makeTDInstance()
        p.makeBranch("a")
        p.a.b
        self.assert_(p._numDangling() == 0)
        self.assert_(p.a._numDangling() == 1)

    def testDangling_10_ForwardReferenceSetsDangling(self):
        p = makeTDInstance()

        v = "ASDFFEVgdkshvfnjdsnfojsanjierf"

        p.l1 = p.l2
        p.l2.n = p.l3
        p.l3.n = p.l4
        p.l4.n = p.l5
        p.l5.n = p.l6
        p.l6.n = p.l7
        p.l7.v = v

        self.assert_(p.l7.v is v)
        self.assert_(p.l6.n.v is v)
        self.assert_(p.l5.n.n.v is v)
        self.assert_(p.l4.n.n.n.v is v)
        self.assert_(p.l3.n.n.n.n.v is v)
        self.assert_(p.l2.n.n.n.n.n.v is v)
        self.assert_(p.l1.n.n.n.n.n.v is v)

    def testDangling_11_ReferenceEquivalence_01(self):

        p = makeTDInstance()

        b = p.a = p.b

        self.assert_(p.a is p.b)

        p.b = 1

        self.assert_(p.a is b)

    def testDangling_11_ReferenceEquivalence_02(self):

        p = makeTDInstance()

        a1 = p.a1 = p.b
        a2 = p.a2 = p.b

        self.assert_(p.a1 is p.b)
        self.assert_(p.a2 is p.b)
        self.assert_(a1 is a2)

        p.b = 1

        self.assert_(p.a1 is a1)
        self.assert_(p.a2 is a1)

    def testDangling_12_ForwardAssingmentSetCorrectlyWithReference(self):

        p = makeTDInstance()
        v = unique_object()

        b = p.a = p.c
        p.c = v

        self.assert_(p.a is not v)
        self.assert_(p.a.isDangling() )

        p.a.v = v

        self.assert_(not p.a.isDangling() )
        self.assert_(p.a.v is v)
        self.assert_(b.v is v)
        self.assert_(b is p.a)
        self.assert_(p.c is v)

    def testDangling_13_CorrectCountsThroughSiblingReferences(self):

        p = makeTDInstance()

        p.a = p.d
        self.assert_(p._numDangling() == 2)

        # Overwrite p.d; p.a still points to the dangling node, so the
        # count should not go down.

        p.d = 1
        self.assert_(p._numDangling() == 1)

    def testDangling_14_CorrectParentingSetAtFixing_01(self):

        p = makeTDInstance()
        v = unique_object()

        p.b = p.c
        p.a = p.b

        # Set c and fix p.b
        p.c = 1
        p.b.x = 1

        # Now b should be
        self.assert_(p.b.branchName() == 'b')
        self.assert_(p.a is p.b)

    def testDangling_14_CorrectParentingSetAtFixing_02(self):

        p = makeTDInstance()
        v = unique_object()

        p.b = p.c
        p.a = p.b

        # Set c and fix p.b
        p.c = 1
        p.a.x = 1

        # Now b should be
        self.assert_(p.b.branchName() == 'b')
        self.assert_(p.a is p.b)

    def testDangling_14_CorrectParentingSetAtFixing_03(self):

        p = makeTDInstance()
        v = unique_object()

        p.b = p.c
        p.a = p.b

        # Set c and fix p.b
        p.c = 1
        p.b = 1
        p.a.x = 1

        # Now b should be
        self.assert_(p.a.branchName() == 'a')

    def testDangling_14_CorrectParentingSetAtFixing_04(self):

        p = makeTDInstance()

        p.makeBranch('cc')

        p.b = p.cc.c
        p.a = p.b

        # Set c and fix p.b
        p.cc.c = 1
        p.b.x = 1

        # Now b should be
        self.assert_(p.b.branchName() == 'b')
        self.assert_(p.a is p.b)

    def testDangling_14_CorrectParentingSetAtFixing_05(self):

        p = makeTDInstance()

        p.makeBranch('cc')

        p.b = p.cc.c
        p.aa.a = p.b

        # Set c and fix p.b
        p.cc.c = 1
        p.b = 1

        # Now b should be
        self.assert_(p.aa.a.branchName() == 'a')

    def testDangling_15_DanglingWhileValueFrozen_01(self):

        p = makeTDInstance()
        p.freeze(values_only = True)

        p.x = 1
        p.b.x = 2
        p.a.b.c.d = 3
        p.a.b.c.e = 4


if __name__ == '__main__':
    unittest.main()

