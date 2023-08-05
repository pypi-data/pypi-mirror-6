# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '1.4.2'

setup(name='silva.system.utils',
      version=version,
      description="Command line utils to manage Silva sites",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='system utils silva',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.system.utils',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.system'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Zope2',
        'Products.Silva >= 3.0c1',
        'argparse',
        'infrae.wsgi',
        'setuptools',
        'silva.core.xml',
        'silva.core.interfaces',
        'silva.core.services',
        'zope.component',
        'zope.location',
        'zope.security',
        'zope.publisher',
        'zope.site',
        ],
      entry_points = """
      [console_scripts]
      silva = silva.system.utils.script:script
      [silva.system.utils]
      manage = silva.system.utils.commands.manage:ManageCommand
      pack = silva.system.utils.commands.pack:PackCommand
      files = silva.system.utils.commands.files:FilesCommand
      versions = silva.system.utils.commands.version:CleanupVersionCommand
      zexp_export = silva.system.utils.commands.zexp:ExportZEXPCommand
      zexp_import = silva.system.utils.commands.zexp:ImportZEXPCommand
      xml_import = silva.system.utils.commands.xml:XmlImportCommand
      """
      )
