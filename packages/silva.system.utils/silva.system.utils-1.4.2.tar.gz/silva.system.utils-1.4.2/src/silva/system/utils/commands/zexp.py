# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

from cStringIO import StringIO
from cPickle import Pickler, Unpickler

from silva.system.utils.script import NEED_ZOPE_SESSION, NEED_SILVA_SESSION
from silva.core.interfaces import IContainer
from ZODB.broken import find_global, Broken
from ZODB.POSException import ExportError
from ZODB.ExportImport import export_end_marker, blob_begin_marker, persistent_id
from ZODB.ExportImport import Ghost, ExportImport
from ZODB.utils import u64, cp, mktemp
import types
import logging
import sys

logger = logging.getLogger('silva.system')
known_broken_modules = {}

def file_opener(gzip=False):
    file_open = open
    if gzip:
        import gzip
        file_open = gzip.open
    return file_open


def is_broken(symb):
    """Return true if the given symbol is broken.
    """
    return isinstance(symb, types.TypeType) and Broken in symb.__mro__


def create_broken_module_for(symb):
    """If your pickle refer a broken class (not an instance of it, a
       reference to the class symbol itself) you have no choice than
       having this module available in the same symbol and with the
       same name, otherwise repickling doesn't work (as both pickle
       and cPikle __import__ the module, and verify the class symbol
       is the same than the one provided).
    """
    parts = symb.__module__.split('.')
    previous = None
    for fullname, name in reversed(
        [('.'.join(parts[0:p+1]), parts[p]) for p in range(1, len(parts))]):
        if fullname not in sys.modules:
            if fullname not in known_broken_modules:
                module = types.ModuleType(fullname)
                module.__name__ = name
                module.__file__ = '<broken module to pickle class reference>'
                module.__path__ = []
                known_broken_modules[fullname] = module
            else:
                if previous:
                    module = known_broken_modules[fullname]
                    setattr(module, *previous)
                break
            if previous:
                setattr(module, *previous)
            previous = (name, module)
        else:
            if previous:
                setattr(sys.modules[fullname], *previous)
                break
    if symb.__module__ in known_broken_modules:
        setattr(known_broken_modules[symb.__module__], symb.__name__, symb)
    elif symb.__module__ in sys.modules:
        setattr(sys.modules[symb.__module__], symb.__name__, symb)


class BrokenModuleFinder(object):
    """This broken module finder works with create_broken_module_for.
    """

    def load_module(self, fullname):
        module = known_broken_modules[fullname]
        if fullname not in sys.modules:
            sys.modules[fullname] = module
        module.__loader__ = self
        return module

    def find_module(self, fullname, path=None):
        if fullname in known_broken_modules:
            return self
        return None


def find_broken_global(*symb):
    result = find_global(*symb)
    if is_broken(result):
        logger.warning('Broken ZODB object for %s.', u' '.join(symb))
        create_broken_module_for(result)
    return result


def import_during_commit(self, transaction, f, return_oid_list):
    """Import data during two-phase commit.

    Invoked by the transaction manager mid commit.
    Appends one item, the OID of the first object created,
    to return_oid_list.
    """
    oids = {}

    # IMPORTANT: This code should be consistent with the code in
    # serialize.py. It is currently out of date and doesn't handle
    # weak references.

    def persistent_load(ooid):
        """Remap a persistent id to a new ID and create a ghost for it."""

        klass = None
        if isinstance(ooid, tuple):
            ooid, klass = ooid

        if ooid in oids:
            oid = oids[ooid]
        else:
            if klass is None:
                oid = self._storage.new_oid()
            else:
                oid = self._storage.new_oid(), klass
            oids[ooid] = oid

        return Ghost(oid)

    while 1:
        header = f.read(16)
        if header == export_end_marker:
            break
        if len(header) != 16:
            raise ExportError("Truncated export file")

        # Extract header information
        ooid = header[:8]
        length = u64(header[8:16])
        data = f.read(length)

        if len(data) != length:
            raise ExportError("Truncated export file")

        if oids:
            oid = oids[ooid]
            if isinstance(oid, tuple):
                oid = oid[0]
        else:
            oids[ooid] = oid = self._storage.new_oid()
            return_oid_list.append(oid)

        # Blob support
        blob_begin = f.read(len(blob_begin_marker))
        if blob_begin == blob_begin_marker:
            # Copy the blob data to a temporary file
            # and remember the name
            blob_len = u64(f.read(8))
            blob_filename = mktemp()
            blob_file = open(blob_filename, "wb")
            cp(f, blob_file, blob_len)
            blob_file.close()
        else:
            f.seek(-len(blob_begin_marker),1)
            blob_filename = None

        pfile = StringIO(data)
        unpickler = Unpickler(pfile)
        unpickler.persistent_load = persistent_load
        unpickler.find_global = find_broken_global

        newp = StringIO()
        pickler = Pickler(newp, 1)
        pickler.inst_persistent_id = persistent_id

        pickler.dump(unpickler.load())
        pickler.dump(unpickler.load())
        data = newp.getvalue()

        if blob_filename is not None:
            self._storage.storeBlob(oid, None, data, blob_filename,
                                    '', transaction)
        else:
            self._storage.store(oid, None, data, '', transaction)


class ExportZEXPCommand(object):

    flags = NEED_ZOPE_SESSION

    def get_options(self, factory):
        parser = factory(
            'zexp_export',
            help='export a content into a ZEXP')
        # parser.add_argument('--gzip', action='store_true',
        #     help='Use gzip compression.')
        parser.add_argument('path', help='path to export')
        parser.add_argument('outfile', help='path to the ouput zip file')
        parser.set_defaults(plugin=self)

    def run(self, root, options):
        path = options.path
        try:
            content = root.restrictedTraverse(path)
            connection = content._p_jar
            with open(options.outfile, 'wb') as f:
                connection.exportFile(content._p_oid, f)
        except KeyError:
            logger.error('Invalid path')
            exit(1)


class ImportZEXPCommand(object):
    flags = NEED_SILVA_SESSION

    def get_options(self, factory):
        parser = factory(
            'zexp_import',
            help='import a ZEXP file')
        # parser.add_argument('--gzip', action='store_true',
        #     help='Input is a gzip file')
        parser.add_argument('--broken', action='store_true',
            help='Handle broken content')
        parser.add_argument(
            'file', help='ZEXP file to import')
        parser.add_argument(
            'paths', nargs=1,
            help='path to Silva sites to work on')
        parser.add_argument(
            'target',
            help='path in Silva where to import the ZEXP',
            default='/')
        parser.set_defaults(plugin=self)

    def run(self, root, options):
        path = options.target
        if not path.startswith('/'):
            path = '/' + path
        container_path, content_id = path.rsplit('/', 1)
        try:
            import_root = root.restrictedTraverse(container_path)
        except KeyError:
            logger.error('Invalid path')
            exit(1)

        if not IContainer.providedBy(import_root):
            logger.error('Import root is not a container')
            exit(2)

        if options.broken:
            ExportImport._importDuringCommit = import_during_commit
            sys.meta_path.append(BrokenModuleFinder())

        with open(options.file, 'rb') as f:
            logger.info('Importing...')
            content = import_root._p_jar.importFile(f)
            logger.info('Inserting content at %s...',
                        "/".join(import_root.getPhysicalPath()) + path)
            import_root._setObject(content_id, content)
            content.id = content_id
