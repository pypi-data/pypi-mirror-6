.. _attic_delete:

attic delete
------------
::


    usage: attic delete [-h] [-v] [-s] ARCHIVE
    
    Delete an existing archive
    
    positional arguments:
      ARCHIVE        archive to delete
    
    optional arguments:
      -h, --help     show this help message and exit
      -v, --verbose  verbose output
      -s, --stats    print statistics for the deleted archive

Description
~~~~~~~~~~~


This command deletes an archive from the repository. Any disk space not
shared with any other existing archive is also reclaimed.

