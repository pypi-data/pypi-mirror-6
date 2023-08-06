;-*- Doctest -*-
==================
Pack ZODBs Offline
==================

Pack a ZODB storage without running any part of the Zope application
server.  Only an appropriate version of ZODB3 for the ZODB storage is
required.  Apply only to copies of ZODB storages, not ZODB storages
currently in use.

Start with a FileStorage that has versions that would be removed on
pack.

    >>> import ZODB, ZODB.FileStorage, transaction
    >>> db = ZODB.DB(ZODB.FileStorage.FileStorage(data_fs))
    >>> conn = db.open()
    >>> conn.root()['foo'] = 'foo'
    >>> transaction.commit()
    >>> conn.root()['foo'] = 'bar'
    >>> transaction.commit()
    >>> conn.close()
    >>> db.close()

The size after packing will be smaller than the size after packing.

    >>> import os
    >>> initial_size = os.path.getsize(data_fs)

    >>> import z3c.offlinepack
    >>> z3c.offlinepack.pack_paths([data_fs])

    >>> os.path.getsize(data_fs) < initial_size
    True
