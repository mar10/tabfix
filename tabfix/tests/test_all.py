# -*- coding: iso-8859-1 -*-
# (c) 2010-2011 Martin Wendt; see http://tabfix.googlecode.com/
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Unit tests for this package.
"""
import tempfile
from zipfile import ZipFile
import unittest
import os
import shutil
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
        self.assertEqual(data.get("files_processed"), 2)
        self.assertEqual(data.get("files_modified"), 2)

    def test_2(self):
        args = [self.temp_path]
        opts = main.Opts()
        opts.matchList = ["*.*"]
        opts.dryRun = True
#        opts.tabbify = False
        
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        self.assertEqual(data.get("files_processed"), 2)
        self.assertEqual(data.get("files_modified"), 2)


def test_suite():
    suite = unittest.makeSuite(TestCase1)
    return suite
