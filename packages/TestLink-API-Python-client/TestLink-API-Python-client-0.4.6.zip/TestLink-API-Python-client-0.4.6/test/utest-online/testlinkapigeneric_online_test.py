#! /usr/bin/python
# -*- coding: UTF-8 -*-

#  Copyright 2013 Luiko Czub, TestLink-API-Python-client developers
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# ------------------------------------------------------------------------

# this test requires an online TestLink Server, which connection parameters
# are defined in environment variables
#     TESTLINK_API_PYTHON_DEVKEY and TESTLINK_API_PYTHON_DEVKEY
#
# works with the example project NEW_PROJECT_API_GENERIC
#  (see TestLinkExampleGenericApi.py)
# FIME LC 29.10.29: test does not really interacts with test link
#                   only negative test with none existing IDs implemented
#                   ok to check every implemented server call one time but not
#                   to cover all possible responses or argument combinations

import unittest, os.path
from testlink import TestlinkAPIGeneric, TestLinkHelper
from testlink.testlinkerrors import TLResponseError


class TestLinkAPIOnlineTestCase(unittest.TestCase):
    """ TestCases for TestlinkAPIClient - interacts with a TestLink Server.
    works with the example project NEW_PROJECT_API (see TestLinkExample.py)
    """

    def setUp(self):
        self.client = TestLinkHelper().connect(TestlinkAPIGeneric)

#    def tearDown(self):
#        pass

    def test_checkDevKey(self):
        response = self.client.checkDevKey()
        self.assertEqual(True, response)
        
    def test_checkDevKey_unknownKey(self):
        with self.assertRaisesRegexp(TLResponseError, '2000.*invalid'):
            self.client.checkDevKey(devKey='unknownKey')
        
    def test_sayHello(self):
        response = self.client.sayHello()
        self.assertEqual('Hello!', response)

    def test_repeat(self):
        response = self.client.repeat('Yellow Submarine')
        self.assertEqual('You said: Yellow Submarine', response)
        
    def test_about(self):
        response = self.client.about()
        self.assertIn('Testlink API', response)

    def test_doesUserExist_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '10000.*Big Bird'):
            self.client.doesUserExist('Big Bird')
        
    def test_createTestProject_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7001.*Empty name'):
            self.client.createTestProject(testprojectname='', 
                                                 testcaseprefix='P4711')
 
    def test_getProjects(self):
        response = self.client.getProjects()
        self.assertIsNotNone(response)
         
    def test_createTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7011.*4712'):
            self.client.createTestPlan('plan 4711', 'project 4712')
 
    def test_createTestSuite_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7000.*4711'):
            self.client.createTestSuite( 4711, 'suite 4712', 'detail 4713')
        
    def test_createTestCase_unknownID(self):
        tc_steps = []
        with self.assertRaisesRegexp(TLResponseError, '7000.*4713'):
            self.client.createTestCase('case 4711', 4712, 4713, 
                                        'Big Bird', 'summary 4714', tc_steps)
 
    def test_getBuildsForTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.getBuildsForTestPlan(4711)
         
    def test_getFirstLevelTestSuitesForTestProject_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7000.*4711'):
            self.client.getFirstLevelTestSuitesForTestProject(4711)
 
    def test_getFullPath_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, 'getFullPath.*234'):
            self.client.getFullPath('4711')
 
    def test_getLastExecutionResult_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.getLastExecutionResult(4711, testcaseid=4712)
         
    def test_getLatestBuildForTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.getLatestBuildForTestPlan(4711)
         
    def test_getProjectTestPlans_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7000.*4711'):
            self.client.getProjectTestPlans(4711)
         
    def test_getProjectPlatforms_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7000.*4711'):
            self.client.getProjectPlatforms(4711)
        
    def test_getTestCase_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '5000.*4711'):
            self.client.getTestCase(testcaseid=4711)
         
    def test_getTestCase_unknownExternalID(self):
        with self.assertRaisesRegexp(TLResponseError, '5040.*GPROAPI-4711'):
            self.client.getTestCase(testcaseexternalid='GPROAPI-4711')
         
    def test_getTestCaseAttachments_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '5000.*4711'):
            self.client.getTestCaseAttachments(testcaseid=4711)
         
    def test_getTestCaseCustomFieldDesignValue_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7000.*4711'):
            self.client.getTestCaseCustomFieldDesignValue(
                   'TC-4712', 1, 4711, 'a_field', details='a_detail')
         
    def test_getTestCaseIDByName_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '5030.*Cannot find'):
            self.client.getTestCaseIDByName('Big Bird')
 
    def test_getTestCasesForTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.getTestCasesForTestPlan(4711)
 
    def test_getTestCasesForTestSuite_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '8000.*4711'):
            self.client.getTestCasesForTestSuite(4711)
 
    def test_getTestPlanByName_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7011.*4711'):
            self.client.getTestPlanByName('project 4711', 'plan 4712')
 
    def test_getTestPlanPlatforms_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.getTestPlanPlatforms(4711)
 
    def test_getTestProjectByName_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7011.*4711'):
            self.client.getTestProjectByName('project 4711')
 
    def test_getTestSuiteByID_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '8000.*4711'):
            self.client.getTestSuiteByID(4711)
 
    def test_getTestSuitesForTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.getTestSuitesForTestPlan(4711)
 
    def test_getTestSuitesForTestSuite_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '8000.*4711'):
            self.client.getTestSuitesForTestSuite(4711)
 
    def test_getTotalsForTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.getTotalsForTestPlan(4711)
 
    def test_createBuild_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.createBuild(4711, 'Build 4712', buildnotes='note 4713')
 
    def test_reportTCResult_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '5000.*4711'):
            self.client.reportTCResult(4712, 'p', testcaseid=4711, 
                                       buildname='build 4713', notes='note 4714' )
 
    def test_uploadExecutionAttachment_unknownID(self):
        attachemantFile = open(os.path.realpath(__file__), 'r')
        with self.assertRaisesRegexp(TLResponseError, '6004.*4712'):
            self.client.uploadExecutionAttachment(attachemantFile, 4712, 
                        title='title 4713', description='descr. 4714')
 
#     def test_getProjectIDByName_unknownID(self):
#         response = self.client.getProjectIDByName('project 4711')
#         self.assertEqual(-1, response)

    def test_createPlatform_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '7011.*4711'):
            self.client.createPlatform('Project 4711', 'Platform 4712', 
                                       notes='note 4713')
            
    def test_addPlatformToTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.addPlatformToTestPlan(4711, 'Platform 4712')
            
    def test_removePlatformFromTestPlan_unknownID(self):
        with self.assertRaisesRegexp(TLResponseError, '3000.*4711'):
            self.client.removePlatformFromTestPlan(4711, 'Platform 4712')
            
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()