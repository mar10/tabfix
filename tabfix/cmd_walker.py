# (c) 2010, 2013 Martin Wendt; see https://github.com/mar10/tabfix
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Helpers to implement a recursive file processing command line script.

Verbosity:
Verbose modes (default: 3)
    0: quiet
    1: errors only
    2: errors and summary
    3: errors, changed files, and summary
    4: errors, visited files, and summary
    5: debug output
"""
from __future__ import print_function
from __future__ import absolute_import

from datetime import datetime
from fnmatch import fnmatch
from optparse import OptionParser
import os
import shutil
import time
from zipfile import ZipFile


TEMP_SUFFIX = ".$temp"
BACKUP_SUFFIX = ".bak"


def is_text_file(filename, blocksize=512):
    try:
        with open(filename, "rb") as f:
            s = f.read(blocksize)
    except IOError:
        return False

    if b"\0" in s:
        return False
    if not s:  # Empty files are considered text
        return True
    return True


def increment_data(data, key, inc=1):
    if type(data) is dict:
        if key in data:
            data[key] += inc
        else:
            data[key] = inc
    return


def is_matching(fspec, match_list):
    """Return True if the name part of fspec matches the pattern (using fnmatch)."""
    if match_list:
        assert isinstance(match_list, (tuple, list))
        name = os.path.basename(fspec)
        for m in match_list:
            if fnmatch(name, m):
                return True
    return False


# ==============================================================================
# WalkerOptions
# ==============================================================================
class WalkerOptions(object):
    """Common options used by cmd_walker.process().

    This object, may be used instead of command line args.
    An implementation should derive its options from this base class and call
    cmd_walker.add_common_options().
    """
    def __init__(self):
        self.backup = True
        self.dry_run = False
        self.ignore_errors = False
        self.ignore_list = None
        self.match_list = None
        self.recursive = False
        self.target_path = None
        self.verbose = 3
        self.zip_backup = False


# ==============================================================================
# Walker
# ==============================================================================
def _process_file(fspec, opts, func, data):
    # handle --ignore
    if is_matching(fspec, opts.ignore_list):
        data["files_ignored"] += 1
        return False

    fspec = os.path.abspath(fspec)
    if not os.path.isfile(fspec):
        ValueError("Invalid fspec: %s" % fspec)

    try:
        target_fspec = opts.target_path or fspec
        target_fspec = os.path.abspath(target_fspec)

        assert not fspec.endswith(TEMP_SUFFIX)
        assert not target_fspec.endswith(TEMP_SUFFIX)
        temp_fspec = fspec + TEMP_SUFFIX
        if os.path.exists(temp_fspec):
            os.remove(temp_fspec)

        try:
            data["files_processed"] += 1
            res = func(fspec, temp_fspec, opts, data)
            if res is not False:
                data["files_modified"] += 1
        except Exception:
            raise
        #
        if res is False or opts.dry_run:
            # If processor returns False (or we are in dry run mode), don't
            # change the file
            if os.path.exists(temp_fspec):
                os.remove(temp_fspec)
        elif opts.backup:
            if opts.zip_backup:
                if os.path.exists(target_fspec):
                    if not data.get("zipfile"):
                        data["zipfile"] = ZipFile(data["zipfile_fspec"], "w")
                    relPath = os.path.relpath(target_fspec, data["zipfile_folder"])
                    data["zipfile"].write(target_fspec, arcname=relPath)
            else:
                bakFilePath = "%s%s" % (target_fspec, BACKUP_SUFFIX)
                if os.path.exists(bakFilePath):
                    os.remove(bakFilePath)
                if os.path.exists(target_fspec):
                    shutil.move(target_fspec, bakFilePath)
            shutil.move(temp_fspec, target_fspec)
        else:
            if os.path.exists(target_fspec):
                os.remove(target_fspec)
            shutil.move(temp_fspec, target_fspec)
    except Exception:
        data["exceptions"] += 1
        raise
    return


def _process_folder(path, opts, func, data):
    """Process matching files inside <path> folder (potentially recursive)."""
    assert opts.match_list
    assert os.path.isdir(path)
    assert not opts.target_path

    data["dirs_processed"] += 1
    try:
        for name in os.listdir(path):
            f = os.path.join(path, name)
            is_file = os.path.isfile(f)
            # handle --ignore
            if is_matching(name, opts.ignore_list):
                if is_file:
                    data["files_ignored"] += 1
                else:
                    data["dirs_ignored"] += 1
                continue

            if is_file:
                # handle --match (only applied to files)
                if opts.match_list and not is_matching(name, opts.match_list):
                    data["files_ignored"] += 1
                    continue
                _process_file(f, opts, func, data)
            elif opts.recursive:
                _process_folder(f, opts, func, data)
    except Exception as e:
        if opts.ignore_errors:
            if opts.verbose >= 1:
                print("Skipping due to ERROR", e)
        else:
            raise
    return


def process(args, opts, func, data):
    data.setdefault("elapsed", 0)
    data.setdefault("elapsed_string", "n.a.")
    data.setdefault("files_processed", 0)
    data.setdefault("files_modified", 0)
    data.setdefault("files_skipped", 0)  # rejected by processor (e.g. binary or empty files)
    data.setdefault("files_ignored", 0)  # due to --match or --ignore
    data.setdefault("dirs_processed", 0)
    data.setdefault("dirs_ignored", 0)  # due to --ignore
    data.setdefault("lines_processed", 0)
    data.setdefault("lines_modified", 0)
    data.setdefault("bytes_read", 0)
    data.setdefault("bytes_written", 0)   # count 0 for unmodified files
    data.setdefault("bytes_written_if", 0)  # count full bytes for unmodified files
    data.setdefault("exceptions", 0)

    if opts.zip_backup:
        zip_folder = os.path.abspath(args[0])
        assert os.path.isdir(zip_folder)
        zip_fspec = os.path.join(
            zip_folder, "backup_{}.zip".format(datetime.now().strftime("%Y%m%d-%H%M%S")))
        data["zipfile_folder"] = zip_folder
        data["zipfile_fspec"] = zip_fspec
    start = time.clock()

    if opts.recursive:
        for path in args:
            _process_folder(path, opts, func, data)
    elif opts.match_list:
        assert len(args) == 1
#        data["dirs_processed"] += 1
        _process_folder(args[0], opts, func, data)
    else:
        for f in args:
            _process_file(f, opts, func, data)

    if data.get("zipfile"):
        data["zipfile"].close()

    data["elapsed"] = time.clock() - start
    data["elapsed_string"] = "%.3f sec" % data["elapsed"]

#    if opts.dry_run and opts.verbose >= 1:
#        print("\n*** Dry-run mode: no files have been modified!\n"
#              " ***Use -x or --execute to process files.\n")
    return


def add_common_options(parser):
    """Return a valid options object.

    @param parser: OptionParser
    """
    parser.add_option("-q", "--quiet",
                      action="count", default=0, dest="verboseDecrement",
                      help="decrease verbosity to 2 (use -qq for 1, ...)")
    parser.add_option("-v", "--verbose",
                      action="count", dest="verbose", default=3,
                      help="increment verbosity to 4 (use -vv for 5, ...)")
    parser.add_option("-n", "--dry-run",
                      action="store_true", dest="dry_run", default=False,
                      help="dry run: just print status messages; don't change anything")
    parser.add_option("-m", "--match",
                      action="append", dest="match_list",
                      help="match this file name pattern (separate by ',' or repeat this option)")
    parser.add_option("-x", "--exclude",
                      action="append", dest="ignore_list",
                      help="skip this file or folder name patterns "
                            "(separate by ',' or repeat this option)")
    parser.add_option("-r", "--recursive",
                      action="store_true", dest="recursive", default=False,
                      help="visit sub directories")
    parser.add_option("-o", "--target",
                      action="store", dest="target_path", default=None,
                      metavar="FILENAME",
                      help="name of output file")
    parser.add_option("-b", "--backup",
                      action="store_true", dest="backup", default=False,
                      help="create backup files (*.bak)")
    parser.add_option("", "--zip-backup",
                      action="store_true", dest="zip_backup", default=False,
                      help="add backups of modified files to a zip-file (implies -b)")
    parser.add_option("", "--ignore-errors",
                      action="store_true", dest="ignore_errors", default=False,
                      help="ignore errors during processing")
    return




def check_common_options(parser, options, args):
    """Preprocess and validate common options."""
#    if len(args) != 1:
#        parser.error("expected exactly one source file or folder")

    # allow multiple patterns in one -m option (separated by ',')
    if options.match_list:
        match_list = []
        for matches in options.match_list:
            for pattern in matches.split(","):
                if pattern not in match_list:
                    match_list.append(pattern)
        options.match_list = match_list

    # allow multiple patterns in one -i option (separated by ',')
    if options.ignore_list:
        match_list = []
        for matches in options.ignore_list:
            for pattern in matches.split(","):
                if pattern not in match_list:
                    match_list.append(pattern)
        options.ignore_list = match_list

    # TODO:
#    if options.quiet and options.verbose:
#        parser.error("options -q and -v are mutually exclusive")
    if options.match_list and not args:
        args.append(".")

    # decrement vorbisity by 1 for every -q option
    if options.verboseDecrement:
        options.verbose = max(0, options.verbose - options.verboseDecrement)
    del options.verboseDecrement

    # --zip-backup implies -b
    if options.zip_backup:
        options.backup = True

    if len(args) < 1:
        parser.error("missing required PATH")
    elif options.target_path and len(args) != 1:
        parser.error("-o option requires exactly one source file")
#    elif options.recursive and len(args) != 1:
#        parser.error("-r option requires exactly one source directory")
    elif options.recursive and len(args) < 1:
        parser.error("-r option requires one or more source directories")
    elif options.recursive and not options.match_list:
        parser.error("-r option requires -m")

    for f in args:
        if not os.path.exists(f):
            parser.error("input not found: %r" % f)
        elif os.path.isdir(f) and not options.match_list:
            parser.error("must specify a match pattern, if source is a folder")
        elif os.path.isfile(f) and options.match_list:
            parser.error("must not specify a match pattern, if source is a file")
#    if not os.path.exists(args[0]):
#        parser.error("input not found: %r" % args[0])
#    elif os.path.isdir(args[0]) and not options.match:
#        parser.error("must specify a match pattern, if source is a folder")
#    elif os.path.isfile(args[0]) and options.match:
#        parser.error("must not specify a match pattern, if source is a file")

    if options.target_path and options.match_list:
        parser.error("-m and -o are mutually exclusive")

    if options.zip_backup and not options.backup:
        parser.error("--zip-backup and --no-backup are mutually exclusive")
    elif options.zip_backup and (len(args) != 1 or not os.path.isdir(args[0])):
        parser.error("--zip-backup requires exactly one source directory")
    return True


# ==============================================================================
# Sample processor
# ==============================================================================
def piggify(fspec, target_fspec, opts, data):
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

    add_common_options(parser)

    # Parse command line
    (options, args) = parser.parse_args()

    # Check syntax
    check_common_options(parser, options, args)

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
