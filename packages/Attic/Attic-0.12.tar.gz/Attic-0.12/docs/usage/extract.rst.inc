.. _attic_extract:

attic extract
-------------
::


    usage: attic extract [-h] [-v] [-n] [-e PATTERN] [--exclude-from EXCLUDEFILE]
                         [--numeric-owner]
                         ARCHIVE [PATH [PATH ...]]
    
    Extract archive contents
    
    positional arguments:
      ARCHIVE               archive to extract
      PATH                  paths to extract
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose output
      -n, --dry-run         do not actually change any files
      -e PATTERN, --exclude PATTERN
                            exclude paths matching PATTERN
      --exclude-from EXCLUDEFILE
                            read exclude patterns from EXCLUDEFILE, one per line
      --numeric-owner       only obey numeric user and group identifiers

Description
~~~~~~~~~~~


This command extracts the contents of an archive. By default the entire
archive is extracted but a subset of files and directories can be selected
by passing a list of ``PATHs`` as arguments. The file selection can further
be restricted by using the ``--exclude`` option.

See "attic help patterns" for more help on exclude patterns.

