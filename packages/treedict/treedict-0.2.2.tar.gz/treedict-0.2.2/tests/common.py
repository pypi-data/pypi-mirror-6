"""
Just a bunch of functions common to the entire test suite
"""
import random, unittest, collections
from treedict import TreeDict, getTree
import treedict
from copy import deepcopy, copy

from hashlib import md5
import base64, time

# a global switch to determine whether the inheritance method is used or not.

_inheritance_level = 0

class TDLvl1(TreeDict):
    pass

class TDLvl2(TDLvl1):
    pass

def makeTDInstance(*args, **kwargs):
    if _inheritance_level == 0:
        return TreeDict(*args, **kwargs)
    elif _inheritance_level == 1:
        return TDLvl1(*args, **kwargs)
    elif _inheritance_level == 2:
        return TDLvl2(*args, **kwargs)
    else:
        assert False

md5keyhash = md5(str(time.clock()).encode('ascii'))

def unique_name():
    md5keyhash.update(str(time.clock()).encode('ascii'))

    return 'u' + (''.join(str(c) for c in base64.b64encode(md5keyhash.digest()).decode('ascii')
                          if str(c).isalnum()))[:6]

def empty_tree():
    return makeTDInstance(unique_name())

def sample_tree():
    p = makeTDInstance(unique_name())
    p.adsfff = 34
    p.bddkeed = 45
    p.cwqod.ada = "ads"
    p.cwqod.ddd = "232"

    p.asddfds.asdffds.asd
    p.single_dangling_node

    return p

def basic_walking_test():
    p = makeTDInstance()

    p.a.b.v = 1
    p.a.v = 1
    p.makeBranch("b")
    p.v = 1

    p.freeze()

    required_item_dict = { 
        (True, "none"): set([ ("a.b.v", 1), 
                              ("v",     1),       
                              ("a.v",   1) ]),

        (True, "all") : set([ ("a.b.v", 1), 
                              ("v",     1),       
                              ("a.v",   1),
                              ("a",     p.a),   
                              ("a.b",   p.a.b), 
                              ("b",     p.b)  ]),

        (True, "only"): set([ ("a",     p.a),   
                              ("a.b",   p.a.b), 
                              ("b",     p.b) ]),

        (False, "none"): set([("v",     1)  ]),

        (False, "all") : set([("v",     1), 
                              ("a",     p.a), 
                              ("b",     p.b)]),
        
        (False, "only"): set([ ("a",    p.a),   
                               ("b",    p.b) ])}
    
    return (p, required_item_dict)

def frozen_tree():
    p = sample_tree()
    p.freeze()
    return p

def random_node_list(seed, n, dp):
    random.seed(seed)

    idxlist = list(range(n))
    l = [unique_name() for i in idxlist]
    
    while idxlist:

        delstack = []

        for ii, i in enumerate(idxlist):
            if random.random() < dp:
                l[i] += '.' + unique_name()
            else:
                delstack.append(ii)

        for ii in reversed(delstack):
            del idxlist[ii]
            
    return l

def random_tree(seed = 0, n = 100):

    t = makeTDInstance()

    for k in random_node_list(seed, n, 0.75):
        t[k] = unique_object()

    return t

def random_selflinked_tree(seed = 0, n = 100):
    random.seed(seed)

    def slt(m):
        p = random_tree(0, m)

        p_links = list(p.itervalues(branch_mode='only', recursive=True))

        random.seed(1)
        random.shuffle(p_links)

        for name, branch in zip(random_node_list(0,2*m, 0.75), p_links):
            p[name] = branch
            
        return p

    # Now a bunch of branches that reference themselves
    q = slt(n)
    
    for name in random_node_list(0,n,0):
        q.attach(name, slt(10))

    return q

class TestObject:
    def __init__(self, v1, v2, v3):
        self.v1 = v1 
        self.v2 = v2
        self.v3 = v3

test_object = TestObject("bork,", 123, "12321")
test_tuple = (1,324, TestObject(12321, "adsfs", 123))
test_list  = [1,324, TestObject(12321, "adsfs", 123)]
test_dict  = {1:2, "3323" : "dfas"} 

def unique_object():
    return [unique_name()]
