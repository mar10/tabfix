# -*- coding: iso-8859-1 -*-
# (c) 2010-2013 Martin Wendt; see https://github.com/mar10/tabfix
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Unit tests for this package.
"""
import tempfile
from zipfile import ZipFile
import unittest
import os
import shutil
import sys
from tabfix import main, cmd_walker



class TestCase1(unittest.TestCase):
    def setUp(self):
        self.temp_path = tempfile.mkdtemp()
        data_path = os.path.dirname(__file__) 
        zf = ZipFile(os.path.join(data_path, "test_files.zip"))
        zf.extractall(self.temp_path)
        
    def tearDown(self):
        shutil.rmtree(self.temp_path)
        
    def test_1(self):
        args = [self.temp_path]
        opts = main.Opts()
        opts.matchList = ["*.txt"]
        opts.targetPath = None
        opts.backup = True
        opts.zipBackup = False
        opts.dryRun = True
        opts.recursive = False
        opts.verbose = 1
        opts.tabSize = 4
        opts.inputTabSize = None
        opts.tabbify = False
        opts.lineSeparator = None
        
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        self.assertEqual(data.get("files_processed"), 3)
        self.assertEqual(data.get("files_modified"), 2)

    def test_2(self):
        args = [self.temp_path]
        opts = main.Opts()
        opts.matchList = ["*.*"]
        opts.dryRun = True
#        opts.tabbify = False
        
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        self.assertEqual(data.get("files_processed"), 5)
        self.assertEqual(data.get("files_modified"), 2)


def test_suite():
    suite = unittest.makeSuite(TestCase1)
    return suite


if __name__ == "__main__":
    print(sys.version)
    unittest.main()

#    suite = unittest.TestSuite()
##    suite.addTest(FtpTest("test_upload_fs_fs"))
##    suite.addTest(FtpTest("test_download_fs_fs"))
#    suite.addTest(FtpTest("test_upload_fs_ftp"))
#    suite.addTest(FtpTest("test_download_fs_ftp"))
##    suite.addTest(PlainTest("test_json"))
##    suite.addTest(PlainTest("test_make_target"))
##    suite.addTest(FtpTest("test_readwrite"))
#    unittest.TextTestRunner(verbosity=1).run(suite)
