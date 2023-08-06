#!/usr/bin/python
"""Pack ZODB storages without running Zope or ZEO"""

usage="usage: %prog [options] PATH..."

import sys, os, logging, time, optparse

import zope.dottedname.resolve
import ZODB.FileStorage, ZODB.serialize

parser = optparse.OptionParser(usage=usage, description=__doc__)
days = optparse.make_option(
    '-d', '--days', type="int", default=0,
    help=("remove revisions more than DAYS old "
          "[default: %default]"))
parser.add_option(days)

def storage_callback(option, opt_str, value, parser, *args, **kwargs):
         setattr(parser.values, option.dest,
                 zope.dottedname.resolve.resolve(value))
storage = optparse.make_option(
    '-s', '--storage', metavar='DOTTED', type="string",
    default=ZODB.FileStorage.FileStorage,
    action='callback', callback=storage_callback,
    help=("use the storage constructor at DOTTED "
          "[default: ZODB.FileStorage.FileStorage]"))
parser.add_option(storage)

logger = logging.getLogger('fspack')

def pack_paths(paths, days=days.default, storage=storage.default):
    delta = days*86400
    for path in paths:
        pack(path, delta, constructor=storage)

def pack(path, delta=days.default*86400, constructor=storage.default):
    storage = constructor(path)
    start = time.time()
    storage.pack(start-delta, ZODB.serialize.referencesf)
    storage.close()
    logger.info('%s has been packed in %.3f seconds'
                % (path, time.time()-start))

def main(parser=parser):
    logging.basicConfig(level=logging.INFO)

    options, args = parser.parse_args()
    if not args:
        parser.error("at least one PATH is required")

    pack_paths(paths=args, **options.__dict__)

    logging.shutdown()

if __name__ == '__main__':
    main()
