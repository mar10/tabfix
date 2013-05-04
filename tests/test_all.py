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
from tabfix.main import read_text_lines, DELIM_CR, DELIM_CRLF, DELIM_LF
#import subprocess
#import StringIO
#IS_PY3 = (sys.version_info[0] >= 3)

USE_FIXED_FOLDER = False


class TestBasic(unittest.TestCase):
    """Basic tests.

    Create a temp folder, extract test data there, and CWD to <temp>/test_files:

    We have this structure:
    <temp root>/
        test_files/
            sub1/
                (some text and other files)
            sub2/
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

        stats = { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 0 }
        res = read_text_lines("test_mixed.txt", stats)
        res = list(res)
        self.assertEqual(len(res), 45)
        self.assertEqual(type(res[0]), type(b""))
        self.assertTrue(res[0].endswith(DELIM_CRLF))
        self.assertEqual(stats, { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 44 })

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
        cmd_walker.process(args, opts, main.fix_tabs, data)
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
        cmd_walker.process(args, opts, main.fix_tabs, data)
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
        cmd_walker.process(args, opts, main.fix_tabs, data)

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
        cmd_walker.process(args, opts, main.fix_tabs, data)

        self.assertEqual(data.get("files_processed"), 22)


    def test_match_all_recursive_ignore(self):
        args = ["."]
        opts = main.Opts()
        opts.ignoreList = ["*.html", "*.js", "sub2"]
        opts.matchList = ["*.*"]
        opts.recursive = True
        opts.verbose = 4

        data = {}
        cmd_walker.process(args, opts, main.fix_tabs, data)

        print(data)
        self.assertEqual(data.get("files_processed"), 14)
        self.assertEqual(data.get("files_skipped"), 5)
        self.assertEqual(data.get("files_ignored"), 4)
        self.assertEqual(data.get("dirs_processed"), 2)
        self.assertEqual(data.get("dirs_ignored"), 1)


#class TestShell(unittest.TestCase):
#    """Basic tests.
#
#    Create a temp folder, extract test data there, and CWD to <temp>/test_files:
#
#    We have this structure:
#    <temp root>/
#        test_files/
#            sub1/
#                (some text and other files)
#            sub2/
#                (some text and other files)
#            (some text and other files)
#    """
#    def setUp(self):
#        #
#        if USE_FIXED_FOLDER:
#            self.temp_path = os.path.join(os.path.expanduser("~"), "tabfix_test_")
#            if not os.path.exists(self.temp_path):
#                os.mkdir(self.temp_path)
#        else:
#            self.temp_path = tempfile.mkdtemp()
#        data_path = os.path.dirname(__file__)
#        zf = ZipFile(os.path.join(data_path, "test_files.zip"))
#        zf.extractall(self.temp_path)
#        self.prev_cwd = os.getcwd()
#        os.chdir(os.path.join(self.temp_path, "test_files"))
#
#        script_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                                        "..", "tabfix"))
#        if not script_folder in sys.path:
#            sys.path.append(script_folder)
#        self.script_path = os.path.abspath(os.path.join(script_folder, "main.py"))
#
#    def tearDown(self):
#        os.chdir(self.prev_cwd)
#        shutil.rmtree(self.temp_path)
#
#    def test_cmd_help(self):
##        res = subprocess.call(["tabfix", "-h"])
#        p = subprocess.Popen(["python", self.script_path, "-h"],
#                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#        out, _err = p.communicate()
#        print(out)
#        self.assertEqual(p.returncode, 0)


#def test_suite():
#    """Called by 'setup.py test'."""
#    suite = unittest.TestSuite()

if __name__ == "__main__":
    print(sys.version)
    unittest.main()

#    suite = unittest.TestSuite()
#    suite.addTest(TestShell("test_cmd_help"))
##    suite.addTest(TestBasic("test_read_text_lines"))
##    suite.addTest(TestBasic("test_tabbify_txt_flat"))
#    unittest.TextTestRunner().run(suite)
