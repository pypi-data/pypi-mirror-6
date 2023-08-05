==================
silva.system.utils
==================

Introduction
============

This extension provides a script to help you manage `Silva`_ sites in
the Zope instance from the command line. This will add script into the
``bin`` directory of your installation called ``silva``.

For most of the operations, the script requires you to provide the
Zope 2 configuration file with the option ``-c``.

By default you can , view the Silva site in the root of your database,
create and delete Silva sites, and users to them, pack your database,
and remove old versions of versioned content.

The script is however pluggable. An another default command provided
by ``silva.core.upgrade`` extension let you to upgrade a Silva site.

Default commands
================

``manage``
   Manage Silva sites:

   - List existing Silva sites,

   - Add a new Silva site,

   - Delete an existing Silva site,

   - Install documentation into an existing Silva site,

   - Add a user into an existing Silva site.

   Multiple actions can done at the same time: you can create a new
   Silva, install the documentation and add a user to it.

``pack``
   Pack a database. The database ``name`` and the number of ``days``
   to pack can be provided on the command line.

``files``
   Convert Silva file storage accordingly to the service files
   settings.

``versions``
   Delete old closed versions from versioned content. The number of
   version to keep is configurable.

``zexp_export``
   Export content into a ZEXP file.

``zexp_import``
   Import a ZEXP file.

``xml_import``
   Import an Silva XML file.

Code repository
===============

The code source for this extension can be found in Git at:
https://github.com/silvacms/silva.system.utils

.. _Silva: http://silvacms.org/
