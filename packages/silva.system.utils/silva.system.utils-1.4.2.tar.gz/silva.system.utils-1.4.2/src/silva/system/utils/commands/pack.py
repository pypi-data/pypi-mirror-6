# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.system.utils.script import NEED_ZOPE_RUNNING, fail
import time
import logging

logger = logging.getLogger('silva.system')


class PackCommand(object):
    flags = NEED_ZOPE_RUNNING

    def get_options(self, factory):
        parser = factory(
            'pack',
            help="pack a root database")
        parser.add_argument(
            '--name', default="main",
            help="database name to pack")
        parser.add_argument(
            "--days", type=int, default=3,
            help="number of days to keep")
        parser.set_defaults(plugin=self)

    def run(self, db, options):
        if options.days < 0:
            fail(u'Cannot pack in the future.')
        db = db.databases.get(options.name)
        if db is None:
            fail(u'Unknown database "%s", cannot pack it.', options.name)
        logger.info(
            u'Packing "%s" database, keeping %d days ...',
            options.name, options.days)
        db.pack(time.time()-options.days*86400)


