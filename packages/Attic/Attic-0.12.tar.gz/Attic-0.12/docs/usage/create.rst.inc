.. _attic_create:

attic create
------------
::


    usage: attic create [-h] [-v] [-s] [-e PATTERN] [--exclude-from EXCLUDEFILE]
                        [-c SECONDS] [--do-not-cross-mountpoints]
                        [--numeric-owner]
                        ARCHIVE PATH [PATH ...]
    
    Create new archive
    
    positional arguments:
      ARCHIVE               archive to create
      PATH                  paths to archive
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose output
      -s, --stats           print statistics for the created archive
      -e PATTERN, --exclude PATTERN
                            exclude paths matching PATTERN
      --exclude-from EXCLUDEFILE
                            read exclude patterns from EXCLUDEFILE, one per line
      -c SECONDS, --checkpoint-interval SECONDS
                            write checkpoint every SECONDS seconds (Default: 300)
      --do-not-cross-mountpoints
                            do not cross mount points
      --numeric-owner       only store numeric user and group identifiers

Description
~~~~~~~~~~~


This command creates a backup archive containing all files found while recursively
traversing all paths specified. The archive will consume almost no disk space for
files or parts of files that have already been stored in other archives.

See "attic help patterns" for more help on exclude patterns.

