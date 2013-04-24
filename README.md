# tabfix [![Build Status](https://travis-ci.org/mar10/tabfix.png?branch=master)](https://travis-ci.org/mar10/tabfix)

Copyright (c) 2010, 2013 Martin Wendt

=== Status ===
*This project has beta status: use at your own risk!*

Please submit bugs as you find them.

This GitHub version is an exploration clone of the original project on Google Code:

https://code.google.com/p/tabfix/

(It may or may not replace the original code some time later.)

**Note**: the command line options have changed!  
**Read [CHANGES.md](https://github.com/mar10/tabfix/blob/master/CHANGES.md) for details!**

**It is recommended to use the dry-run option `-d` to test-run your script.**

=== Summary ===
Cleanup whitespace in text files:

  * Unify indentation by replacing leading tabs with spaces (or vice versa)
  * Strip trailing whitespace
  * Make sure the file ends with exactly one line break
  * Unify line delimiters to Unix, Windows, or Mac style
  * Optionally change indentation depth

=== Usage ===
*Preconditions:* [http://www.python.org/download/ Python] is required, 
[http://pypi.python.org/pypi/setuptools#using-setuptools-and-easyinstall EasyInstall]
recommended. 

Install like this:

```
$sudo easy_install -U tabfix
```

or on Windows:
```
>easy_install -U tabfix
```

*Syntax*:
```
$ tabfix --help
Usage: tabfix [options] [PATH]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s N, --tab-size=N    set target tab size (default: 4)
  --input-tab-size=N    assume tab size of input file to be N (default: target
                        tab size)
  -t, --tabbify         uses tabs for indentation (default: use spaces
  --line-separator=MODE
                        line separator used for output file. Possible values:
                        Unix, Windows, Mac, LF, CRLF, CR (default: keep mode
                        from input file)
  -d, --dry-run         dry run: just print status messages; don't change
                        anything
  -i IGNORELIST, --ignore=IGNORELIST
                        skip this file name patterns (separate by ',' or
                        repeat this option)
  -m MATCHLIST, --match=MATCHLIST
                        match this file name pattern (separate by ',' or
                        repeat this option)
  -r, --recursive       visit sub directories
  -o FILENAME, --target=FILENAME
                        name of output file
  -b, --backup          create backup files (*.bak)
  -q, --quiet           decrease verbosity to 2 (use -qq for 1, ...)
  -v, --verbose         increment verbosity to 4 (use -vv for 5, ...)
  --zip-backup          add backups of modified files to a zip-file
  --ignore-errors       ignore errors during processing

See also https://github.com/mar10/tabfix
$ 
```

*Example*

Fix whitespace in all !JavaScript and HTML files in the current directory and all sub directories.  
Convert space-indents to tabs, using one tab for 4 spaces.  
Source files will be replaced, a backup file is created with `*.bak` extension.
```
> tabfix -t -b -r -m*.js,*.html
```

Run the script in dry-run mode, so only status messages are printed, but no files are changed.  
Don't make backups:
```
> tabfix -t -r -m*.js,*.html -d
```

*Example*

Fix whitespace (using 4 spaces for indentation) in two source files:
```
> tabfix foo.js bar.html
```

*Example*

Cleanup test.html and write output to test2.html.
Convert tabs to 4 spaces, assuming original tab size was 2.<br>
`-vv` prints all modified lines.<br>
Since we pass `-d`, no files are really changed.
```
>tabfix --input-tab-size=2 test.html -otest2.html -vv -d
```
