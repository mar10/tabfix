# -*- coding: iso-8859-1 -*-
# (c) 2010-2013 Martin Wendt; see https://github.com/mar10/tabfix
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Unit tests for this package.
"""
import tempfile
import filecmp
from zipfile import ZipFile
import unittest
import os
import shutil
import sys
from tabfix import main, cmd_walker
from unittest.suite import TestSuite
from tabfix.main import read_text_lines, DELIM_CR, DELIM_CRLF, DELIM_LF

IS_PY3 = (sys.version_info[0] >= 3) 

USE_FIXED_FOLDER = True

#class TextFileReader(object):
#    def __init__(self, fname):
#        if sys.version_info[0] >= 3:
#            # Python 3: read binary, because we don't know the encoding.
#            # We still want line-breaks, so U is added.
#            # NOTE: '\n' and '\r\n' are recognized, but '\r' NOT
#            mode = "Urb"
#            self.f = open(fname, "Urb")
#        else:
#            # Python 2: we get 
#            self.f = open(fname, "Urt")
#    def read_text_as_binary(self, fname):
#        """"""
#        is_py3 = (sys.version_info[0] >= 3) 
#        if is_py3:
#            # Python 3: read binary, because we don't know the encoding.
#            # We still want line-breaks, so U is added.
#            # NOTE: '\n' and '\r\n' are recognized, but '\r' NOT
#            mode = "Urb"
#        else:
#            # Python 2: we get 
#            mode = "Urt"

class TestBasic(unittest.TestCase):
    """Basic tests.
    
    Create a temp folder, extract test data there, and CWD to <temp>/test_files:
    
    We have this structure:
    <temp root>/
        test_files/
            sub1/
                (some text and other files)
            sub1/
                (some text and other files)
            (some text and other files)
    """
    def setUp(self):
        # 
        if USE_FIXED_FOLDER:
            self.temp_path = os.path.join(os.path.expanduser("~"), "tabfix_test_")
            if not os.path.exists(self.temp_path):
                os.mkdir(self.temp_path)
        else:
            self.temp_path = tempfile.mkdtemp()
        data_path = os.path.dirname(__file__) 
        zf = ZipFile(os.path.join(data_path, "test_files.zip"))
        zf.extractall(self.temp_path)
        self.prev_cwd = os.getcwd()
        os.chdir(os.path.join(self.temp_path, "test_files"))
        
    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.temp_path)
        
    def test_spacify_txt_flat(self):
        
#        args = [self.temp_path]
        args = ["."]
        
        opts = main.Opts()
        opts.backup = True
        opts.dryRun = False
        opts.ignoreList = None
        opts.inputTabSize = None
        opts.lineSeparator = None
        opts.matchList = ["*.txt"]
        opts.recursive = False
        opts.tabbify = False
        opts.tabSize = 4
        opts.targetPath = None
        opts.verbose = 1
        opts.zipBackup = False
                
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        self.assertEqual(data.get("files_processed"), 10)
        self.assertEqual(data.get("files_modified"), 5)
        self.assertEqual(data.get("lines_modified"), 125)
        self.assertTrue(os.path.isfile(os.path.join(self.temp_path, "test_files", "test_mixed.txt.bak")))
        # TODO: use difflib
        # http://docs.python.org/2/library/difflib.html
        self.assertTrue(filecmp.cmp(os.path.join(self.temp_path, "test_files", "test_mixed.txt"), 
                                    os.path.join(os.path.dirname(__file__), "test_mixed_expect_spaced.txt")))
        
        # TODO: test directly using shell exec & command line

    def test_tabbify_txt_flat(self):
        
        args = ["."]
        
        opts = main.Opts()
        opts.backup = True
        opts.dryRun = False
        opts.ignoreList = None
        opts.inputTabSize = None
        opts.lineSeparator = None
        opts.matchList = ["*.txt"]
        opts.recursive = False
        opts.tabbify = True
        opts.tabSize = 4
        opts.targetPath = None
        opts.verbose = 1
        opts.zipBackup = False
        
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        self.assertEqual(data.get("files_processed"), 10)
        self.assertEqual(data.get("files_modified"), 8)
        self.assertEqual(data.get("lines_modified"), 154)
        # created .bak file
        self.assertTrue(os.path.isfile(os.path.join(self.temp_path, "test_files", "test_mixed.txt.bak")))
        # TODO: use difflib
        # http://docs.python.org/2/library/difflib.html
        self.assertTrue(filecmp.cmp(os.path.join(self.temp_path, "test_files", "test_mixed.txt"), 
                                    os.path.join(os.path.dirname(__file__), "test_mixed_expect_tabbed.txt")))
        
        # TODO: test directly using shell exec & command line

    def test_match_all_flat(self):
        args = ["."]
        opts = main.Opts()
        opts.matchList = ["*.*"]
        opts.tabbify = False
        
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        
        # Note: if this fails with '9 != 8', there might be a '.DS_Store' 
        # in 'test_files.zip':
        self.assertEqual(data.get("files_processed"), 14)
        self.assertEqual(data.get("files_modified"), 7)


    def test_match_all_recursive(self):
        args = ["."]
        opts = main.Opts()
        opts.matchList = ["*.*"]
        opts.recursive = True
        
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        
        self.assertEqual(data.get("files_processed"), 22)


    def test_match_all_recursive_ignore(self):
        args = ["."]
        opts = main.Opts()
        opts.ignoreList = ["*.html", "*.js"]
        opts.matchList = ["*.*"]
        opts.recursive = True
        
        data = {}
        cmd_walker.process(args, opts, main.fixTabs, data)
        
        self.assertEqual(data.get("files_processed"), 16)


    def test_read_text_lines(self):
        
        stats = { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 0 }
        res = read_text_lines("test_cr.txt", stats)
        res = list(res)
        self.assertEqual(len(res), 7)
        self.assertEqual(type(res[0]), type(b""))
        self.assertTrue(res[0].endswith(DELIM_CR))
        self.assertEqual(stats, { DELIM_CR: 6, DELIM_LF: 0, DELIM_CRLF: 0 })
        
        stats = { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 0 }
        res = read_text_lines("test_crlf.txt", stats)
        res = list(res)
        self.assertEqual(len(res), 7)
        self.assertEqual(type(res[0]), type(b""))
        self.assertTrue(res[0].endswith(DELIM_CRLF))
        self.assertEqual(stats, { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 6 })
        
        stats = { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 0 }
        res = read_text_lines("test_lf.txt", stats)
        res = list(res)
        self.assertEqual(len(res), 7)
        self.assertEqual(type(res[0]), type(b""))
        self.assertTrue(res[0].endswith(DELIM_LF))
        self.assertEqual(stats, { DELIM_CR: 0, DELIM_LF: 6, DELIM_CRLF: 0 })
        
        read_text_lines("test_mixed.txt")        
        

if __name__ == "__main__":
    print(sys.version)
    unittest.main()
    
#    suite = TestSuite()
##    suite.addTests(TestBasic)
##    suite.addTest(TestBasic("test_read_text_lines"))
#    suite.addTest(TestBasic("test_tabbify_txt_flat"))
#    unittest.TextTestRunner().run(suite)