# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.ExtensionService import install_documentation

from silva.system.utils.script import NEED_ZOPE_SESSION, fail
from silva.core.interfaces import IRoot
from zope.publisher.browser import TestRequest

import logging
import transaction

logger = logging.getLogger('silva.system')


class ManageCommand(object):
    flags = NEED_ZOPE_SESSION

    def get_options(self, factory):
        parser = factory(
            'manage',
            help="manage Silva sites in the database")
        parser.add_argument(
            '--list', action="store_true",
            help="list available sites")
        parser.add_argument(
            '--add', action="store_true",
            help="add a new Silva root")
        parser.add_argument(
            '--delete', action="store_true",
            help="delete an existing Silva root")
        parser.add_argument(
            '--documentation', action="store_true",
            help="install documentation in the Silva root")
        parser.add_argument(
            '--user',
            help="add a new user in the Silva root: username:password:role")
        parser.set_defaults(plugin=self)
        parser.add_argument(
            'identifier', nargs='?',
            help="site identifier")

    def run(self, root, options):
        if options.list:
            logger.info('Listing silva sites')
            for content in root.objectValues():
                if IRoot.providedBy(content):
                    logger.info('%s (version %s)' % (
                            '/'.join(content.getPhysicalPath()),
                            content.get_silva_content_version()))
            return
        if not options.identifier:
            fail(u"Please provide a site identifier")
        identifier = options.identifier
        if ':' in identifier:
            identifier, title = identifier.split(':', 1)
        else:
            title = identifier
        if options.delete:
            if identifier not in root.objectIds():
                fail(
                    u'There is no such Silva root "%s" to delete.',
                    identifier)
            root.manage_delObjects([identifier])
            return
        if options.add:
            if identifier in root.objectIds():
                fail(
                    u'There is already a Zope object identifier by "%s"',
                    identifier)
            factory = root.manage_addProduct['Silva']
            factory.manage_addRoot(identifier, title)
            transaction.commit()
            logger.info(
                u'Silva root "%s" added.', identifier)
        root = root._getOb(identifier)
        if options.documentation:
            factory = root.manage_addProduct['SilvaFind']
            factory.manage_addSilvaFind('search', 'Search this site')
            install_documentation(root, TestRequest())
            transaction.commit()
            logger.info(
                u'Silva documentation installed inside Silva root "%s".',
                identifier)
        if options.user:
            parts = options.user.split(':')
            if len(parts) < 2 or len(parts) > 3:
                fail('Impossible to interpret user definition')
            username = parts[0]
            password = parts[1]
            role = parts[2] if len(parts) == 3 else 'Manager'
            acl_users = root._getOb('acl_users')
            users = acl_users._getOb('users')
            roles = acl_users._getOb('roles')
            if not role in roles.listRoleIds():
                fail(u'Role "%s" unknown.' % role)
            users.addUser(username, username, password)
            roles.assignRoleToPrincipal(role, username)
            transaction.commit()
            logger.info(
                u'User added to Silva root "%s".', identifier)

