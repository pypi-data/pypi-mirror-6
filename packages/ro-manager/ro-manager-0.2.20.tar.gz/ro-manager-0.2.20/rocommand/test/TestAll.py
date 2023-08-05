#!/usr/bin/env python

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys, unittest, os

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "..")
    sys.path.insert(0, "../..")
    sys.path.insert(0, "../../iaeval/test")
    sys.path.insert(0, "../../checklist/test")
    sys.path.insert(0, "../../sync/test")
    sys.path.insert(0, "../../roweb")
    sys.path.insert(0, "../../roweb/test")

import TestConfig
import TestSparqlQueries
import TestBasicCommands
import TestAnnotationUtils
import TestManifest
import TestROMetadata
import TestAnnotations
import TestLinks
import TestROSRS_Session
import TestROSRSMetadata
import TestSyncCommands
import TestRemoteROMetadata
import TestRosrsSync
import TestEvoCommands
import TestMinimAccess
import TestMinimAccess2
import TestEvalChecklist
import TestEvalQueryMatch
import TestRdfReport
import TestGridMatch
import TestMkMinim

# Code to run unit tests from all library test modules
def getTestSuite(select="unit"):
    suite = unittest.TestSuite()
    suite.addTest(TestSparqlQueries.getTestSuite(select=select))
    suite.addTest(TestBasicCommands.getTestSuite(select=select))
    suite.addTest(TestAnnotationUtils.getTestSuite(select=select))
    suite.addTest(TestManifest.getTestSuite(select=select))
    suite.addTest(TestROMetadata.getTestSuite(select=select))
    suite.addTest(TestAnnotations.getTestSuite(select=select))
    suite.addTest(TestLinks.getTestSuite(select=select))
    suite.addTest(TestMinimAccess.getTestSuite(select=select))
    suite.addTest(TestMinimAccess2.getTestSuite(select=select))
    suite.addTest(TestEvalChecklist.getTestSuite(select=select))
    suite.addTest(TestEvalQueryMatch.getTestSuite(select=select))
    suite.addTest(TestRdfReport.getTestSuite(select=select))
    suite.addTest(TestGridMatch.getTestSuite(select=select))
    suite.addTest(TestMkMinim.getTestSuite(select=select))
    if select != "unit":
        suite.addTest(TestROSRS_Session.getTestSuite(select=select))
        suite.addTest(TestRemoteROMetadata.getTestSuite(select=select))
        suite.addTest(TestROSRSMetadata.getTestSuite(select=select))
        suite.addTest(TestRosrsSync.getTestSuite(select=select))
        suite.addTest(TestSyncCommands.getTestSuite(select=select))
        suite.addTest(TestEvoCommands.getTestSuite(select));
    return suite

from MiscUtils import TestUtils

def runTestSuite():
    """
    Transfer function for setup.py script ro-manager-test
    """
    base = os.path.dirname(__file__)
    #print "Run test suite assuming base path "+base
    sys.path.insert(0, os.path.normpath(base+"/..") )
    sys.path.insert(0, os.path.normpath(base+"/../..") )
    sys.path.insert(0, os.path.normpath(base+"/../../iaeval/test") )
    sys.path.insert(0, os.path.normpath(base+"/../../sync/test") )
    #print "Path: "+repr(sys.path)
    TestUtils.runTests("TestAll", getTestSuite, sys.argv)
    return 0

if __name__ == "__main__":
    print "By default, runs quick tests only."
    print "Use \"python TestAll.py all\" to run all tests"
    TestUtils.runTests("TestAll", getTestSuite, sys.argv)

# End.
