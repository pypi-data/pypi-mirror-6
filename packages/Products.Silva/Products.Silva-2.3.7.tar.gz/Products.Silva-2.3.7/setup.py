# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '2.3.7'

tests_require = [
    'silva.export.opendocument',
    'infrae.testing',
    'infrae.testbrowser',
    'infrae.wsgi [test]',
    'zope.testing',
    ]

def product_readme(filename):
    return open(os.path.join("Products", "Silva", filename)).read()


setup(name='Products.Silva',
      version=version,
      description="Silva Content Management System",
      long_description=product_readme("README.txt") + "\n" +
                       product_readme("HISTORY.txt"),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva cms zope',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/Products.Silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'PIL',
        'Products.FileSystemSite',
        'Products.Formulator',
        'Products.SilvaDocument',
        'Products.SilvaExternalSources',
        'Products.SilvaFind',
        'Products.SilvaKupu',
        'Products.SilvaMetadata',
        'Products.SilvaViews',
        'Sprout',
        'ZODB3 >= 3.9',
        'Zope2',
        'five.grok',
        'five.localsitemanager',
        'infrae.rest',
        'lxml >= 2.1.1',
        'setuptools',
        'silva.core.cache',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.messages',
        'silva.core.references',
        'silva.core.services',
        'silva.core.smi',
        'silva.core.upgrade',
        'silva.core.views',
        'silva.translations',
        'silvatheme.standardissue',
        'megrok.chameleon',
        'zeam.form.silva',
        'zope.annotation',
        'zope.component',
        'zope.contenttype',
        'zope.event',
        'zope.i18n',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.site',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
