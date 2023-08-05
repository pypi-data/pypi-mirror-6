#!/usr/bin/python

"""
Module to test ROSRS synchronization RO manager commands

See: http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool
"""

__author__      = "piotrhol"
__copyright__   = "PNSC (@@check)"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os.path
import filecmp
import logging
import shutil
import urlparse
import time
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json
    
log = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

from MiscUtils import TestUtils
from rocommand import ro, ro_metadata, ro_remote_metadata, ro_annotation, ro_settings
from rocommand.ROSRS_Session import ROSRS_Session
from TestConfig import ro_test_config
from StdoutContext import SwitchStdout
from ro_utils import parse_job
import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

# Local ro_config for testing
ro_config = {
    "annotationTypes":      ro_annotation.annotationTypes,
    "annotationPrefixes":   ro_annotation.annotationPrefixes
    }


class TestSyncCommands(TestROSupport.TestROSupport):
    """
    Test sync ro commands
    """
    
    def setUp(self):
        super(TestSyncCommands, self).setUp()
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        return

    def tearDown(self):
        super(TestSyncCommands, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'
    
    def testPushZip(self):
        """
        Push a Research Object in zip format to ROSRS.

        ro push <zip> | -d <dir>  [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ] 
        """
        args = [
            "ro", "push", "zips/pushro-6.zip",
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
            ]
        
        #preparing
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
        accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)        
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("Job URI"),1)
        self.assertEqual(self.outstr.getvalue().count("ENTER"),1)
        for line in self.outstr.getvalue().split("\n"):
            if "RO URI:" in line:
                id = line.split("RO URI:")[1].strip()
                self.rosrs.deleteRO(id)

    def testPushZipWithNewOption(self):
        """
        Push a Research Object in zip format to ROSRS.

        ro push <zip> | -d <dir>  [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ] 
        """
        args = [
            "ro", "push", "data/newro.zip", "--new",
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
            ]
        
        #preparing
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
        accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)        
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("new"),1)
        self.assertEqual(self.outstr.getvalue().count("Job URI"),1)
        self.assertEqual(self.outstr.getvalue().count("ENTER"),1)
        for line in self.outstr.getvalue().split("\n"):
            if "RO URI:" in line:
                id = line.split("RO URI:")[1].strip()
                self.rosrs.deleteRO(id)


    def testPushZipSynchronous(self):
        """
        Push a Research Object in zip format to ROSRS.

        ro push <zip> | -d <dir>  [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ] 
        """
        args = [
            "ro", "push", "zips/pushro-6.zip",
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
            ]
        
        #preparing
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
        accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        
        #cleaning
        ro_remote_metadata.deleteRO(httpsession, ro_test_config.ROSRS_URI + "ro1/")
        
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("Job URI"),1)
        for line in self.outstr.getvalue().split("\n"):
            if "RO URI:" in line:
                id = line.split("RO URI:")[1].strip()
                ro_remote_metadata.deleteRO(httpsession,id)
        
    def testPushZipAsynchronous(self):
        """
        Push a Research Object in zip format to ROSRS.

        ro push <zip> | -d <dir>  [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ] 
        """
        args = [
            "ro", "push", "zips/pushro-6.zip",
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "--asynchronous",
            "-v"
            ]
        
        #preparing
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
        accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        ro_remote_metadata.deleteRO(httpsession, ro_test_config.ROSRS_URI + "ro/")
        
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("Job URI"),1)
        #self.assertEqual(self.outstr.getvalue().count("Job Status:"),1)
        for line in self.outstr.getvalue().split("\n"):
            if "Job URI:" in line:
                jobLocation = line.split("Job URI:")[1].strip()
                status = "RUNNING"
                while status == "RUNNING":
                    time.sleep(1)
                    (status, id, processed_resources, submitted_resources) = parse_job(self.rosrs, jobLocation)
                assert status == "DONE"
                self.rosrs.deleteRO(id)
        
    def testPush(self):
        """
        Push a Research Object to ROSRS.

        ro push <zip> | -d <dir>  [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ]
        """

        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test ro push", "ro-testRoPush")
        localRo  = ro_metadata.ro_metadata(ro_config, rodir)
        localRo.addAggregatedResources(rodir, recurse=True)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        localRo.addSimpleAnnotation(roresource, "type",         "Test file")
        localRo.addSimpleAnnotation(roresource, "description",  "File in test research object")
        args = [
            "ro", "push",
            "-d", rodir,
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
            ]
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
            accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        ro_remote_metadata.deleteRO(httpsession, urlparse.urljoin(httpsession.baseuri(), "RO_test_ro_push/"))
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("Resource uploaded:"), 8)
        self.assertEqual(self.outstr.getvalue().count("Resource deleted in ROSRS:"), 0)
        self.assertEqual(self.outstr.getvalue().count("Annotation pushed:"), 3)
        self.assertEqual(self.outstr.getvalue().count("Annotation deleted in ROSRS:"), 0)
        # Clean up
        self.deleteTestRo(rodir)
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
            accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        for line in self.outstr.getvalue().splitlines():
            if "Created RO:" in line:
                createdRO = line.split("Created RO:")[1].strip()
                ro_remote_metadata.deleteRO(httpsession, createdRO)

        return

    def testCheckout(self):
        """
        Checkout a Research Object from ROSRS.

        ro checkout [ <RO-identifier> ] [ -d <dir> ] [ -r <rosrs_uri> ] [ -t <access_token> ]
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test ro checkout", "ro-testRoPush")
        localRo  = ro_metadata.ro_metadata(ro_config, rodir)
        localRo.addAggregatedResources(rodir, recurse=True)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        ann1 = localRo.addSimpleAnnotation(roresource, "type",         "Test file")
        ann2 = localRo.addSimpleAnnotation(roresource, "description",  "File in test research object")
        # remove previous RO
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
            accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        ro_remote_metadata.deleteRO(httpsession, urlparse.urljoin(httpsession.baseuri(), "RO_test_ro_checkout/"))

        # push an RO
        args = [
            "ro", "push",
            "-d", rodir,
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        
        createdUri = self.outstr.getvalue().splitlines()[1].split("Created RO: ")[1].split(ro_test_config.ROSRS_URI)[1]
        
        # check it out as a copy
        rodir2 = os.path.join(ro_test_config.ROBASEDIR, createdUri)
        
        rodir_original_path = os.path.join(ro_test_config.ROBASEDIR, "origin")
        shutil.rmtree(rodir_original_path, ignore_errors = True)
        shutil.rmtree(rodir2, ignore_errors = True)
        shutil.move(rodir, rodir_original_path)
        
        args = [
            "ro", "checkout", createdUri,
            "-d", ro_test_config.ROBASEDIR,
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        
        files = [ "robase/"+ createdUri +"README-ro-test-1"
          , "robase/"+ createdUri + "minim.rdf"
          , "robase/"+ createdUri + "subdir1/subdir1-file.txt"
          , "robase/"+ createdUri + "subdir2/subdir2-file.txt"
          , "robase/"+ createdUri + "filename with spaces.txt"
          , "robase/"+ createdUri + "filename#with#hashes.txt"
          , "robase/"+ createdUri + ".ro/manifest.rdf"
          , "robase/"+ createdUri + ann1
          , "robase/"+ createdUri + ann2
          , "robase/"+ createdUri + ".ro/evo_info.ttl"
          ]

        self.assertEqual(self.outstr.getvalue().count("ro checkout"), 1)
        for f in files:
            self.assertEqual(self.outstr.getvalue().count(f), 1, "%s"%f)
        self.assertEqual(self.outstr.getvalue().count("%d files checked out" % len(files)), 1)
        
        # compare they're identical, with the exception of registries.pickle
       
        cmpres = filecmp.dircmp(rodir_original_path,rodir2)
        self.assertEquals(cmpres.left_only, [ro_settings.REGISTRIES_FILE])
        self.assertEquals(cmpres.right_only, [])
        self.assertListEqual(cmpres.diff_files, [], "Files should be the same (manifest is ignored)")

        # delete the checked out copy
        self.deleteTestRo(rodir2)
        self.deleteTestRo(rodir_original_path)
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI,
            accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        ro_remote_metadata.deleteRO(httpsession, urlparse.urljoin(httpsession.baseuri(), createdUri))
        return
    
    # Sentinel/placeholder tests

    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "Pending tests follow"

# Assemble test suite

def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit":
            [ "testUnits"
            , "testNull"
            ],
        "component":
            [ "testComponents"
            , "testPush"
            , "testPushZip"
            , "testPushZipSynchronous"
            , "testPushZipAsynchronous"
            , "testCheckout"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestSyncCommands, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestSyncCommands.log", getTestSuite, sys.argv)

# End.
