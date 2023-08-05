#!/usr/bin/env python

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys, os, os.path

from MiscUtils import TestUtils

def runTestSuite():
    """
    Transfer function for setup.py script ro-manager-test
    """
    base = os.path.dirname(__file__)
    os.chdir(base)
    #print "Run test suite assuming base path "+base
    sys.path.insert(0, os.path.normpath(base+"/..") )
    sys.path.insert(0, os.path.normpath(base+"/../..") )
    sys.path.insert(0, os.path.normpath(base+"/../../iaeval/test") )
    sys.path.insert(0, os.path.normpath(base+"/../../sync/test") )
    sys.path.insert(0, os.path.normpath(base+"/../../checklist/test") )
    sys.path.insert(0, os.path.normpath(base+"/../../roweb") )
    sys.path.insert(0, os.path.normpath(base+"/../../roweb/test") )
    #print "Path: "+repr(sys.path)
    import TestAll
    TestUtils.runTests("TestAll", TestAll.getTestSuite, sys.argv)
    return 0
