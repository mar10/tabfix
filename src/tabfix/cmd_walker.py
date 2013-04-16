# (c) 2010, 2013 Martin Wendt; see http://tabfix.googlecode.com/
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Helpers to implement a recursive file processing command line script.
"""
from __future__ import print_function
from __future__ import absolute_import

from optparse import OptionParser
import os
import shutil
from fnmatch import fnmatch
import time
from zipfile import ZipFile
from datetime import datetime

TEMP_SUFFIX = ".$temp"
BACKUP_SUFFIX = ".bak"

#===============================================================================

def isTextFile(filename, blocksize=512):
    # Author: Andrew Dalke
    # http://code.activestate.com/recipes/173220-test-if-a-file-or-string-is-text-or-binary/
    try:
        s = open(filename, "rb").read(blocksize)
    except IOError:
        return False

    if b"\0" in s:
        return False
    if not s:  # Empty files are considered text
        return True
    return True


#===============================================================================

def incrementData(data, key, inc=1):
    if type(data) is dict:
        if key in data:
            data[key] += inc
        else:
            data[key] = inc
    return


#===============================================================================
# WalkerOptions
#===============================================================================
class WalkerOptions(object):
    """Common options used by cmd_walker.process().
    
    This object, may be used instead of command line args.
    An implementation should derive its options from this base class and call
    cmd_walker.addCommonOptions().
    """
    def __init__(self):
        self.backup = True
        self.dryRun = False
        self.ignoreErrors = False
        self.ignoreList = None
        self.matchList = None
        self.recursive = False
        self.targetPath = None
        self.verbose = 1
        self.zipBackup = False


#===============================================================================
# Walker 
#===============================================================================
def _processFile(fspec, opts, func, data):
    fspec = os.path.abspath(fspec)
    if not os.path.isfile(fspec):
        ValueError("Invalid fspec: %s" % fspec)

    try:
        targetFspec = opts.targetPath or fspec
        targetFspec = os.path.abspath(targetFspec)

        assert not fspec.endswith(TEMP_SUFFIX)
        assert not targetFspec.endswith(TEMP_SUFFIX)
        tempFspec = fspec + TEMP_SUFFIX
        if os.path.exists(tempFspec):
            os.remove(tempFspec)

        try:
            data["files_processed"] += 1
            res = func(fspec, tempFspec, opts, data)
            if res is not False:
                data["files_modified"] += 1
        except Exception:
            data["exceptions"] += 1
            raise
        # 
        if res is False or opts.dryRun:
            # If processor returns False (or we are in dry run mode), don't 
            # change the file
            if os.path.exists(tempFspec):
                os.remove(tempFspec)
        elif opts.backup:
            if opts.zipBackup:
                if os.path.exists(targetFspec):
                    if not data.get("zipfile"):
                        data["zipfile"] = ZipFile(data["zipfile_fspec"], "w")
                    relPath = os.path.relpath(targetFspec, data["zipfile_folder"])
                    data["zipfile"].write(targetFspec, arcname=relPath) 
            else:
                bakFilePath = "%s%s" % (targetFspec, BACKUP_SUFFIX)
                if os.path.exists(bakFilePath):
                    os.remove(bakFilePath)
                if os.path.exists(targetFspec):
                    shutil.move(targetFspec, bakFilePath)
            shutil.move(tempFspec, targetFspec)
        else:
            if os.path.exists(targetFspec):
                os.remove(targetFspec)
            shutil.move(tempFspec, targetFspec)
    except Exception:
        raise
    return


def _processPattern(path, opts, func, data):
    assert opts.matchList
    assert os.path.isdir(path)
    assert not opts.targetPath
    try:
        for f in os.listdir(path):
            # handle --ignore
            if opts.ignoreList:
                ignore = False
                for m in opts.ignoreList: 
                    if m and fnmatch(f, m):
                        ignore = True
                        break
                if ignore:
                    continue
            # handle --match
            match = False
            for m in opts.matchList: 
                if m and fnmatch(f, m):
                    match = True
                    break
            if not match:
                continue
            
            f = os.path.join(path, f)
            if os.path.isfile(f):
                _processFile(f, opts, func, data)
    except Exception as e:
        if opts.ignoreErrors:
            if opts.verbose >= 1:
                print("Skipping due to ERROR", e)
        else:
            raise
    return


def _processRecursive(path, opts, func, data):
    """Handle recursion or file patterns."""
    assert opts.recursive
    assert opts.matchList
    assert os.path.isdir(path)
    data["dirs_processed"] += 1
    _processPattern(path, opts, func, data)
    for root, dirnames, _filenames in os.walk(path):
        for dirname in dirnames:
            data["dirs_processed"] += 1
            _processPattern(os.path.join(root, dirname), opts, func, data)
    return


def process(args, opts, func, data):
    data.setdefault("elapsed", 0)
    data.setdefault("elapsed_string", "n.a.")
    data.setdefault("files_processed", 0)
    data.setdefault("files_modified", 0)
    data.setdefault("files_skipped", 0)
    data.setdefault("exceptions", 0)
    data.setdefault("dirs_processed", 1)
    if opts.zipBackup:
        zipFolder = os.path.abspath(args[0]) 
        assert os.path.isdir(zipFolder) 
        zipFspec = os.path.join(zipFolder, 
                                "backup_%s.zip" 
                                % datetime.now().strftime("%Y%m%d-%H%M%S"))
        data["zipfile_folder"] = zipFolder
        data["zipfile_fspec"] = zipFspec
    start = time.clock()
    
    if opts.recursive:
        assert len(args) == 1
        _processRecursive(args[0], opts, func, data)
    elif opts.matchList:
        assert len(args) == 1
        _processPattern(args[0], opts, func, data)
    else:
        for f in args:
            _processFile(f, opts, func, data)

    if data.get("zipfile"):
        data["zipfile"].close()

    data["elapsed"] = time.clock() - start
    data["elapsed_string"] = "%.3f sec" % data["elapsed"]
    
#    if opts.dryRun and opts.verbose >= 1:
#        print("\n*** Dry-run mode: no files have been modified!\n"
#              " ***Use -x or --execute to process files.\n")
    return




def addCommonOptions(parser):
    """Return a valid options object.
    @param parser: OptionParser
    """
#    parser.add_option("-d", "--dry-run",
#                      action="store_true", dest="dryRun", default=False,
#                      help="dry run: just print converted lines to screen")
    parser.add_option("-x", "--execute",
                      action="store_false", dest="dryRun", default=True,
                      help="turn off the dry-run mode (which is ON by default), " 
                      "that would just print status messages but does not change "
                      "anything")
    parser.add_option("-i", "--ignore",
                      action="append", dest="ignoreList",
                      help="skip this file name pattern (option may be repeated)")
    parser.add_option("-m", "--match",
                      action="append", dest="matchList",
                      help="match this file name pattern (option may be repeated)")
    parser.add_option("-r", "--recursive",
                      action="store_true", dest="recursive", default=False,
                      help="visit sub directories")
    parser.add_option("-o", "--target",
                      action="store", dest="targetPath", default=None,
                      metavar="FILENAME",
                      help="name of output file")
    parser.add_option("", "--no-backup",
                      action="store_false", dest="backup", default=True,
                      help="prevent creation of backup files (*.bak)")
    parser.add_option("-q", "--quiet",
                      action="store_const", const=0, dest="verbose", 
                      help="don't print status messages to stdout (verbosity 0)")
#    parser.add_option("-q", "--quiet",
#                      action="store_true", const=0, dest="quiet", default=False,
#                      help="don't print status messages (verbose 0)")
#    def quietCallback(option, opt_str, value, parser, *args, **kwargs):
#        pass
#    parser.add_option("-q", "--quiet",
#                      action="callback", callback=quietCallback,
#                      help="don't print status messages (verbosity 0).")
    parser.add_option("-v", "--verbose",
                      action="count", dest="verbose", default=1,
                      help="increment verbosity to 2 (use -vv for 3, ...)")
    parser.add_option("", "--zip-backup",
                      action="store_true", dest="zipBackup", default=False,
                      help="add backups of modified files to a zip-file")
    parser.add_option("", "--ignore-errors",
                      action="store_true", dest="ignoreErrors", default=False,
                      help="ignore errors during processing")
    return




def checkCommonOptions(parser, options, args):
    """Validate common options."""
#    if len(args) != 1:
#        parser.error("expected exactly one source file or folder")
    # TODO:
#    if options.quiet and options.verbose:
#        parser.error("options -q and -v are mutually exclusive")
    if options.matchList and not args:
        args.append(".")

    if len(args) < 1:
        parser.error("missing required PATH")
    elif options.targetPath and len(args) != 1:
        parser.error("-o option requires exactly one source file")
    elif options.recursive and len(args) != 1:
        parser.error("-r option requires exactly one source directory")
    elif options.recursive and not options.matchList:
        parser.error("-r option requires -m")

    for f in args:
        if not os.path.exists(f):
            parser.error("input not found: %r" % f)
        elif os.path.isdir(f) and not options.matchList:
            parser.error("must specify a match pattern, if source is a folder")
        elif os.path.isfile(f) and options.matchList:
            parser.error("must not specify a match pattern, if source is a file")
#    if not os.path.exists(args[0]):
#        parser.error("input not found: %r" % args[0])
#    elif os.path.isdir(args[0]) and not options.match:
#        parser.error("must specify a match pattern, if source is a folder")
#    elif os.path.isfile(args[0]) and options.match:
#        parser.error("must not specify a match pattern, if source is a file")
    
    if options.targetPath and options.matchList:
        parser.error("-m and -o are mutually exclusive")

    if options.zipBackup and not options.backup:
        parser.error("--zip-backup and --no-backup are mutually exclusive")
    elif options.zipBackup and (len(args) != 1 or not os.path.isdir(args[0])):
        parser.error("--zip-backup requires exactly one source directory")
    return True




#===============================================================================
# Sample processor
#===============================================================================
def piggify(fspec, targetFspec, opts, data):
    """Sample file processor."""
    pass




def test():
    # Create option parser for common and custom options
    parser = OptionParser(usage="usage: %prog [options] PATH",
                          version="0.0.1")

    parser.add_option("-c", "--count",
                      action="store", dest="count", default=3,
                      metavar="COUNT",
                      help="number of '.' to prepend (default: %default)")

    addCommonOptions(parser)
    
    # Parse command line
    (options, args) = parser.parse_args()

    # Check syntax  
    checkCommonOptions(parser, options, args)

    try:
        count = int(options.count)
    except:
        count = 0
    if count < 1:
        parser.error("count must be numeric and greater than 1")
    
    # Call processor
    data = {}
    process(args, options, piggify, data)
    


if __name__ == "__main__":
    test()
