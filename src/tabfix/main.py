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
        ValueError("Target fspec must nt exist: %r" % targetFspec)
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

    # Open with 'U', so we get file.newline 
    with open(fspec, "Ur") as fin:
        modified = False
        lines = []
        lineNo = 0
        changedLines = 0
        for line in fin:
            lineNo += 1
            orgLine = line.rstrip(chr(0x0A) + chr(0x0D))
            line = orgLine.rstrip(" \t")
            s = ""
            indent = 0
            chars = 0
            for c in line:
                if c in (" ", " "): # Space, shift-space
                    chars += 1
                    indent += 1
                elif c == "\t":
                    chars += 1
                    # Use integer division '//' (Py3k)
                    indent = inputTabSize * ((indent + inputTabSize) // inputTabSize)
                else:
                    break
    
            if opts.tabbify:
                # TODO: use '//' integer division??
                s = "\t" * (indent // opts.tabSize) + " " * (indent % opts.tabSize) + line[chars:]
            else:
                s = " " * indent + line[chars:]
    
            lines.append(s)
            if s != orgLine:
                modified = True
                changedLines += 1
                if opts.verbose >= 3:
                    print("    #%04i: %s" % (lineNo, orgLine.replace(" ", ".").replace("\t", "<tab>"))) 
                    print("         : %s" % s.replace(" ", ".").replace("\t", "<tab>")) 
        
        # Line delimiter of input file (None, if ambiguous)
        sourceLineSeparator = None
        try:
            if type(fin.newlines) is str:
                sourceLineSeparator = fin.newlines
        except Exception:  
            pass
        fin.close()

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
    while len(lines) > 1 and lines[-1] == "":
        modified = True
        lines.pop()

    # Open with 'b', so we can have our own line endings
    with open(targetFspec, "wb") as fout:
        # TODO: when we optimize this ('if' before with, and remove close) , we get errors ???
        if modified:
#            print(lineSeparator.join(lines))
            fout.writelines(lineSeparator.join(lines))
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
