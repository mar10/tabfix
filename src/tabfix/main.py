# (c) 2010, 2013 Martin Wendt; see https://github.com/mar10/tabfix
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Cleanup whitespace in text files:

- Unify indentation by replacing leading tabs with spaces (or vice versa)
- Strip trailing whitespace
- Make sure the file ends with exactly one line break
- Unify line delimiters to Unix, Windows, or Mac style
- Optionally change indentation depth
"""
from __future__ import print_function
from __future__ import absolute_import

from optparse import OptionParser
import os
from .cmd_walker import WalkerOptions, addCommonOptions, checkCommonOptions,\
    process, isTextFile, incrementData
from ._version import __version__
import sys


#IS_PY3 = sys.version_info[0] >= 3
IS_PY2 = sys.version_info[0] < 3

DELIM_CR = b"\r"
DELIM_LF = b"\n"
DELIM_CRLF = b"\r\n"

_separatorMap = {
    "CR": chr(13),
    "MAC": chr(13),
    "LF": chr(10),
    "UNIX": chr(10),
    "CRLF": chr(13) + chr(10),
    "WINDOWS": chr(13) + chr(10),
    }


class Opts(WalkerOptions):
    """Options object, may be used instead of command line args."""
    def __init__(self):
        WalkerOptions.__init__(self)
        self.tabSize = 4
        self.inputTabSize = None
        self.tabbify = False
        self.lineSeparator = None



def _hexString(s):
    """Return string as readable hex dump for debugging."""
    return "[%s]" % ", ".join([ "x%02X" % ord(c) for c in s ])


def read_text_lines(fname, newline_dict=None):
    """Read a text file as separate binary lines (works in Python 2 and 3).
    
    '\r', '\n', and '\r\n' are accepted as delimiter.

    Return an a tuple (lines, stats) with
    lines: binary string with line ending stripped
    iterator of (binary_line_string, delimiter.)
    """
    # Note Python 3:
    #
    # We use binary mode, because otherwise Python 3 would try to decode
    # to unicode. But we don't know the encoding (and are not interested in
    # the line's content anyway, except for leading and trailing tabs and spaces).
    #
    # In Python 3 'universal newlines' mode is on by default.
    # Lines that end with `\r\n` or `\n` are recognized even when the file 
    # was opened in binary mode. The original line ending will be part of the line string.
    # BUT reading lines from a file will NOT recognize Mac line endings
    # (`\r`), when the file was opened in binary mode.
    if not newline_dict:
        newline_dict = { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 0 }
    # Don't use 'U': (default in Python 3), but would replace line endings with `\n` Python 2
    with open(fname, "rb") as f:
        for line in f.readlines():
#            print("%r" % line)
            ending = b""
            if line.endswith(DELIM_CRLF):
                ending = DELIM_CRLF
                newline_dict[DELIM_CRLF] += 1 
            elif line.endswith(DELIM_CR):
                ending = DELIM_CR
                newline_dict[DELIM_CR] += 1
            elif line.endswith(DELIM_LF):
                ending = DELIM_LF
                newline_dict[DELIM_LF] += 1
            # Strip all trailing `\r` and/or `\n`
            line = line.rstrip(DELIM_CRLF)
            # Handle `\r` (Mac, CR) separators, as they are not recognized by python 3
            count_lf = line.count(DELIM_CR)
            if count_lf > 0:
                newline_dict[DELIM_CR] += count_lf
                l2 = [ l + DELIM_CR for l in line.split(DELIM_CR) ]
            else:
                l2 = [ line + ending ]
                
            for l in l2:
#                print("%r" % l)
                yield l
#    print(newline_dict)
    return
    

#===============================================================================
# fixTabs
#===============================================================================

def fixTabs(fspec, targetFspec, opts, data):
    """Unify leading spaces and tabs and strip trailing whitespace.
    
    Caller made sure that 
    - fspec exists
    - targetFSpec does not exist.
      In replace mode, a targetFSpec is a temp file. 
    
    Afterwards, if this function returns True, the caller will 
    - Make a backup of fspec 
    - If running in replace mode, move targetFSpec to fspec   

    If this function returns False, or opts.dryRun is True, the caller will 
    - not make a backup
    - remove targetFSpec, if it exists  
    """
    # Assert what cmd_walker gives us
    if not os.path.isfile(fspec):
        ValueError("Invalid source fspec: %r" % fspec)
    if os.path.exists(targetFspec):
        ValueError("Target fspec must not exist: %r" % targetFspec)
    assert os.path.abspath(fspec) != os.path.abspath(targetFspec) 

#    if opts.dryRun and opts.verbose >= 1:
#        print "Dry-run %s" % fspec

    if not isTextFile(fspec):
        if opts.verbose >= 1:
            print("Skipping non-text file %s" % fspec) 
        incrementData(data, "files_skipped")
        return False
    elif opts.verbose >= 1:
        print("Processing %s" % fspec) 
    fspec = os.path.abspath(fspec)
    inputTabSize = opts.inputTabSize or opts.tabSize

    modified = False
    lines = []
    lineNo = 0
    changedLines = 0
    # Read lines as binary strings (keeping original endings)
    stats = { DELIM_CR: 0, DELIM_LF: 0, DELIM_CRLF: 0 }
    for line in read_text_lines(fspec, stats):
#        print("%r" % line)
        lineNo += 1
        # Note: this strips '\r' and/or '\n'
        orgLine = line.rstrip(DELIM_CRLF)
        # TODO: add shift-space
        line = orgLine.rstrip(b" \t")
#        print("%r" % line)
        s = b""
        indent = 0
        chars = 0
        for c in line:
            # Python 3 returns int, Python 2 returns str
            if IS_PY2:
                c = ord(c)
#            if c in (b" ", b" "): # Space, shift-space
            if c in (32, 160): # Space, shift-space
                chars += 1
                indent += 1
#            elif c == b"\t":
            elif c == 9: # TAB
                chars += 1
                # Use integer division '//' (Py3k)
                indent = inputTabSize * ((indent + inputTabSize) // inputTabSize)
            else:
                break

        if opts.tabbify:
            # Use '//' integer division (Py3k)
            s = b"\t" * (indent // opts.tabSize) + b" " * (indent % opts.tabSize) + line[chars:]
        else:
            s = b" " * indent + line[chars:]

        lines.append(s)
        if s != orgLine:
#            print("    old: %r" % orgLine)
#            print("    new: %r" % s)
            modified = True
            changedLines += 1
            if opts.verbose >= 3:
                print("    #%04i: %s" % (lineNo, orgLine.replace(" ", ".").replace("\t", "<tab>"))) 
                print("         : %s" % s.replace(" ", ".").replace("\t", "<tab>")) 
    
    # Line delimiter of input file (`None` if ambiguous)
    ending_types = []
#    max_ending_type = None
#    max_ending_count = 0
    for type_, count in stats.items():
        if count:
            ending_types.append(type_)
#        if count > max_ending_count:
#            max_ending_type = type_
    if len(ending_types) == 1:
        sourceLineSeparator = ending_types[0]
    else:
        sourceLineSeparator = None
        
    if opts.lineSeparator:
        lineSeparator = _separatorMap[opts.lineSeparator.upper()]
    elif sourceLineSeparator:
        lineSeparator = sourceLineSeparator
    else:
        lineSeparator = os.linesep

    if sourceLineSeparator != lineSeparator:
        modified = True
        if opts.verbose >= 2:
            print("    Changing line separator to %s" % (_hexString(lineSeparator)))
    # Strip trailing empty lines
    while len(lines) > 1 and lines[-1] == b"":
        modified = True
        lines.pop()

    # Open with 'b', so we can have our own line endings
    with open(targetFspec, "wb") as fout:
        # TODO: when we optimize this ('if' before with, and remove close) , we get errors ???
        if modified:
#            print("%r" % lineSeparator.join(lines))
#            fout.writelines(bytes(lineSeparator.join(lines), "utf8"))
            fout.write(lineSeparator.join(lines))
            fout.write(lineSeparator)
        fout.close()
    
    srcSize = os.path.getsize(fspec)
    targetSize = os.path.getsize(targetFspec)
    incrementData(data, "bytes_read", srcSize)
    incrementData(data, "bytes_written", targetSize)
    incrementData(data, "lines_modified", changedLines)
    
    if modified:
        if opts.verbose >= 2:
            print("    Changed %s lines (size %s -> %s bytes)" % (changedLines, srcSize, targetSize))
    else:
        if opts.verbose >= 2:
            print("    Unmodified.")
    
    # Return false, if nothing changed.
    # In this case cmd_walker discards the output file
    return modified




def run():
    # Create option parser for common and custom options
    parser = OptionParser(usage="usage: %prog [options] [PATH]",
                          prog="tabfix", # Otherwise 'tabfix-script.py' gets displayed
                          version=__version__,
                          epilog="See also http://tabfix.googlecode.com")

    parser.add_option("-s", "--tab-size",
                      action="store", dest="tabSize", type="int", default=4,
                      metavar="N",
                      help="set target tab size (default: %default)")
    parser.add_option("", "--input-tab-size",
                      action="store", dest="inputTabSize", type="int", default=None,
                      metavar="N",
                      help="assume tab size of input file to be N "
                      "(default: target tab size)")
    parser.add_option("-t", "--tabbify",
                      action="store_true", dest="tabbify", default=False,
                      help="uses tabs for indentation (default: use spaces")
    parser.add_option("", "--line-separator",
                      action="store", dest="lineSeparator", default=None,
                      metavar="MODE",
                      help="line separator used for output file. "
                      "Possible values: Unix, Windows, Mac, LF, CRLF, CR "
                      "(default: keep mode from input file)")

    addCommonOptions(parser)
    
    # Parse command line
    (options, args) = parser.parse_args()

    # Check syntax  
    checkCommonOptions(parser, options, args)

    if options.lineSeparator and options.lineSeparator.upper() not in list(_separatorMap.keys()):
        parser.error("--line-separator must be one of '%s'" % "', '".join(list(_separatorMap.keys())))

    # Call processor
    data = {}
    process(args, options, fixTabs, data)
    
    # Print summary
    if options.verbose >= 1 and data.get("zipfile"):
        print() 
        print(("Backup archive:\n    %s" % data.get("zipfile_fspec")))
        
    if options.verbose >= 1:
        print() 
        print(("Modified %s/%s files in %s folders (elap %s)" 
              % (data["files_modified"], data["files_processed"], 
                 data["dirs_processed"], data["elapsed_string"]))) 

    if options.dryRun and options.verbose >= 1:
        print("\n*** Dry-run mode: no files have been modified!\n"
              "*** Use -x or --execute to process files.")


if __name__ == "__main__":
    run()
