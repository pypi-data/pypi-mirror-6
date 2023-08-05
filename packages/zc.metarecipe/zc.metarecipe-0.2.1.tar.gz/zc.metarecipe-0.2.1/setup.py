##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
name, version = 'zc.metarecipe', '0.2.1'

install_requires = ['setuptools']
extras_require = dict(test=['zope.testing', 'manuel'])

entry_points = """
"""

from setuptools import setup

# copy README to root.
import os
here = os.path.dirname(__file__)
with open(
    os.path.join(here, *(['src'] + name.split('.') + ['README.txt']))
    ) as inp:
    with open(os.path.join(here, 'README.txt'), 'w') as outp:
        outp.write(inp.read())

setup(
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    license = 'ZPL 2.1',

    name = name, version = version,
    long_description=open('README.txt').read(),
    description = open('README.txt').read().strip().split('\n')[0],
    packages = [name.split('.')[0], name],
    namespace_packages = [name.split('.')[0]],
    package_dir = {'': 'src'},
    install_requires = install_requires,
    zip_safe = False,
    entry_points=entry_points,
    package_data = {name: ['*.txt', '*.test', '*.html']},
    extras_require = extras_require,
    tests_require = extras_require['test'],
    test_suite = name+'.tests.test_suite',
    )

os.remove(os.path.join(here, 'README.txt'))
