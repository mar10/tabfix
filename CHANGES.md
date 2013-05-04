tabfix changes
==============


Cleanup whitespace in text files.

## 0.2.2
  - --ignore also works for folder names

## 0.2.1
  - Added --ignore

## 0.2.0
Cloned on GitHub from the Google Code version 

**Note**: the command line options have changed!  
**Be careful with existing shell scripts after updating from v.0.x!** 

  - Support for Python 2.6+ and 3.2+
  - `-x`, `--execute` option was removed. It is now on by default.
    Use `--dry-run` to force simulation mode.
  - `--no-backup` option was removed. It is now on by default.
    Use `-b` to enable backups.
  - `-i`, `--ignore` option was added to allow exclusion patterns.
  - Verbositiy was changed. By default only changed files will be printed.
  - PEP 8
  - Multiple target folders may be passed
  - `-m` option now accepts a comma separated list of patterns.

## 0.1.7 and before
Hosted on Google Code: https://code.google.com/p/tabfix/

(It may or may not replace the original code some time later.)