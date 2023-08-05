.. include:: global.rst.inc

Welcome to Attic
================
|project_name| is a deduplicating backup program written in Python.
The main goal of |project_name| is to provide an efficient and secure way
to backup data. The data deduplication technique used makes |project_name|
suitable for daily backups since only actual changes are stored.


Easy to use
-----------
Initialize a new backup :ref:`repository <repository_def>` and create your
first backup :ref:`archive <archive_def>` in two lines::

    $ attic init /usbdrive/my-backup.attic
    $ attic create -v /usbdrive/my-backup.attic::documents ~/Documents

See the :ref:`quickstart` chapter for a more detailed example.

Easy installation
-----------------
You can use pip to install |project_name| quickly and easily::

    $ pip install attic

Need more help with installing? See :ref:`installation`.

User's Guide
============

.. toctree::
   :maxdepth: 2

   foreword
   installation
   quickstart
   usage
   faq

Getting help
============

If you've found a bug or have a concrete feature request you can add your bug
report or feature request directly to the project `issue tracker`_. For more
general questions or discussions a post to the mailing list is preferred.

Mailing list
------------

There is a mailing list for Attic on librelist_ you can use for feature
requests and general discussions about Attic. A mailing list archive is
available `here <http://librelist.com/browser/attic/>`_.

To subscribe to the list send an email to attic@librelist.com and reply
to the confirmation mail. Likevise To unsubscribe send an email to 
attic-unsubscribe@librelist.com and reply to the confirmation mail.
