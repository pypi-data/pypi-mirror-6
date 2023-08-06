==================
Pack ZODBs Offline
==================

Pack a ZODB storage without running any part of the Zope application
server.  Only an appropriate version of ZODB3 for the ZODB storage is
required.  Apply only to copies of ZODB storages, not ZODB storages
currently in use.

Install the distribution::

  $ python setup.py install

Then use the offlinepack script to pack a copy of your ZODB::

  $ offlinepack /path/to/Data-copy.fs

Use the --help option for more details::

  $ offlinepack --help
  usage: offlinepack [options] PATH...
  
  Pack ZODB storages without running Zope or ZEO
  
  options:
    -h, --help            show this help message and exit
    -d DAYS, --days=DAYS  remove revisions more than DAYS old [default: 0]
    -s DOTTED, --storage=DOTTED
                          use the storage constructor at DOTTED [default:
                          ZODB.FileStorage.FileStorage]

zc.buildout
-----------

A buildout.cfg is included that will install the offlinepack script
to the buildout.  The buildout makes it possible to quickly use the
offlinepack script without modifying the system python installation::

  $ git clone https://github.com/rpatterson/z3c.offlinepack.git
  $ cd z3c.offlinepack
  $ python bootstrap.py -v
  $ bin/buildout -v
  $ bin/offlinepack /path/to/Data-copy.fs

The buildout.cfg file can also be modified to use a specific version
of ZODB3.  This is uesful if you need to use offlinepack without
migrating the ZODB to a newer version of ZODB3.  Add the version
specifier to the offlinepack section of buildout.cfg.  For example, to
use offlinepack with Zope 2.9, use the following offlinepack section::

  [offlinepack]
  recipe = zc.recipe.egg:scripts
  eggs = z3c.offlinepack
      ZODB3<3.7-dev
