# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import atexit
import logging
import argparse
import os.path
import sys
import pdb
from pkg_resources import iter_entry_points

from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_parent
from OFS.interfaces import IObjectManager
from Testing.makerequest import makerequest
from infrae.wsgi.paster import boot_zope
from silva.core.interfaces import IRoot
from zope.location.interfaces import ISite
from zope.security.management import newInteraction
from zope.site.hooks import setSite, setHooks
import AccessControl.User
import Zope2


def setup_logging(options):
    """Setup logger to log messages on the output.
    """
    logger = logging.getLogger()
    level = logging.INFO
    if options.debug:
        level = logging.DEBUG
    logger.setLevel(level)
    formatter = logging.Formatter(fmt='%(levelname)s: %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if options.log:
        handler = logging.FileHandler(options.log)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def fail(message, *args):
    """Fail.
    """
    if args:
        message = message % args
    sys.stderr.write('ERROR: ' + message + '\n')
    sys.exit(1)

NEED_ZOPE_RUNNING = 1
NEED_ZOPE_SESSION = NEED_ZOPE_RUNNING | 2
NEED_SILVA_SESSION = NEED_ZOPE_SESSION | 4


def default_arg_generator(options):
    setup_logging(options)
    yield options

def zope_boot_arg_generator(parent):
    options = parent.next()

    if options.config is None or not os.path.isfile(options.config):
        fail("use --config to specify zope configuration")

    boot_zope(options.config, debug_mode=options.debug)

    def close():
        Zope2.DB.close()

    atexit.register(close)

    yield Zope2.DB, options

    try:
        parent.next()
    except StopIteration:
        pass
    else:
        fail(u"internal error")

def zope_session_arg_generator(parent):
    db, options = parent.next()

    newSecurityManager(None, AccessControl.User.system)
    Zope2.zpublisher_transactions_manager.begin()
    root = makerequest(Zope2.bobo_application())
    newInteraction()

    yield root, options

    Zope2.zpublisher_transactions_manager.commit()

    try:
        parent.next()
    except StopIteration:
        pass
    else:
        fail(u"internal error")


def zope_find_user(container, username):
    while IObjectManager.providedBy(container):
        if container._getOb('acl_users', None) is not None:
            user = container.acl_users.getUser(username)
            if user is not None and user.getUserName() is not None:
                return user.__of__(container.acl_users)
        container = aq_parent(container)
    fail("%s is not a valid user." % username)


def silva_session_arg_generator(parent):
    root, options = parent.next()

    if not hasattr(options, 'paths') or not len(options.paths):
        fail(u"specifiy at least one Silva root path")

    for path in options.paths:
        try:
            silva = root.unrestrictedTraverse(path)
        except KeyError:
            fail("%s is not a valid Zope path" % path)
        if not IRoot.providedBy(silva):
            fail("%s is not a valid Silva root" % path)
        if ISite.providedBy(silva):
            setSite(silva)
        else:
            setSite(None)
        setHooks()

        if hasattr(options, 'username') and options.username:
            user = zope_find_user(silva, options.username)
            newSecurityManager(None, user)

        yield silva, options

    try:
        parent.next()
    except StopIteration:
        pass
    else:
        fail(u"internal error")


ARGS_GENERATORS = [(NEED_ZOPE_RUNNING, zope_boot_arg_generator),
                   (NEED_ZOPE_SESSION, zope_session_arg_generator),
                   (NEED_SILVA_SESSION, silva_session_arg_generator)]


def get_plugins():
    plugins = []
    for entry_point in iter_entry_points('silva.system.utils'):
        command_class = entry_point.load()
        plugins.append(command_class())
    return plugins


def get_options():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-c", "--config",
        default='parts/instance/etc/zope.conf',
        help="Zope configuration file path")
    parser.add_argument(
        "--debug", action="store_true",
        help="run in debug mode")
    parser.add_argument(
        "--log", action="store",
        help="store logs in a file")
    subparser = parser.add_subparsers(
        title="commands")

    def add_options(*args, **kwargs):
        kwargs['formatter_class'] = argparse.ArgumentDefaultsHelpFormatter
        return subparser.add_parser(*args, **kwargs)

    for plugin in get_plugins():
        plugin.get_options(add_options)

    return parser.parse_args()


def script():
    """Silva Upgrade script.
    """
    options = get_options()
    args_generator = default_arg_generator(options)

    for flag, new_args_generator in ARGS_GENERATORS:
        if (options.plugin.flags & flag) == flag:
            args_generator = new_args_generator(args_generator)

    for args in args_generator:
        try:
            options.plugin.run(*args)
        except Exception, error:
            if options.debug:
                print (u"%s:" % sys.exc_info()[0]).encode('utf-8')
                print (u"%s" % sys.exc_info()[1]).encode('utf-8')
                pdb.post_mortem(sys.exc_info()[2])
            raise error

    sys.exit(0)
