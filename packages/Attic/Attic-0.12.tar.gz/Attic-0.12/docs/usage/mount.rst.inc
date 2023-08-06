.. _attic_mount:

attic mount
-----------
::


    usage: attic mount [-h] [-v] [-f] [-o OPTIONS]
                       REPOSITORY_OR_ARCHIVE MOUNTPOINT
    
    Mount archive or an entire repository as a FUSE fileystem
    
    positional arguments:
      REPOSITORY_OR_ARCHIVE
                            repository/archive to mount
      MOUNTPOINT            where to mount filesystem
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose output
      -f, --foreground      stay in foreground, do not daemonize
      -o OPTIONS            Extra mount options

Description
~~~~~~~~~~~


This command mounts an archive as a FUSE filesystem. This can be useful for
browsing an archive or restoring individual files. Unless the ``--foreground``
option is given the command will run in the background until the filesystem
is ``umounted``.

