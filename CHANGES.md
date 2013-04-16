tabfix changes
==============


Cleanup whitespace in text files.

## 2.0.0
Cloned on GitHub from the Google Code version 

**Note**: the command line options have changed!  
**Be careful with existing shell scripts after updating from v.0.x!** 

### Done
  - `-i`, `--ignore` option was added to allow exclusion patterns.

### Planned
  - Support for Python 2.6+ and 3.2+
  - `-x`, `--execute` option was removed. It is now on by default.
    Use `--dry-run` to force simulation mode.
  - `--no-backup` option was removed. It is now on by default.
    Use `-b` to enable backups.
  - `-m` option now accepts a comma separated list of extensions.
  - Multiple target folders may be passed
  - Verbositiy was changed. By default only changed files will be printed.
  - PEP 8
  
## 0.1.7 and before
Hosted on Google Code: https://code.google.com/p/tabfix/

(It may or may not replace the original code some time later.)