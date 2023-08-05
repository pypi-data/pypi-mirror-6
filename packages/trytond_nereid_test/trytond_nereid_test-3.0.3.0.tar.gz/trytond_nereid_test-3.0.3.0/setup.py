#!/usr/bin/env python
#This file is part of Tryton and Nereid.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import re
import os
import ConfigParser
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = [
]


for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append('trytond_%s >= %s.%s, < %s.%s' % (
            dep, major_version, minor_version,
            major_version, minor_version + 1)
        )
requires.append('trytond >= %s.%s, < %s.%s' %
        (major_version, minor_version, major_version, minor_version + 1))

setup(
    name='trytond_nereid_test',
    version=info.get('version'),
    url='http://nereid.openlabs.co.in/docs/',
    license='GPLv3',
    author='Openlabs Technologies & Consulting (P) Limited',
    author_email='info@openlabs.co.in',
    description='Tryton - Web Framework Test Supplement',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=requires,
    packages=[
        'trytond.modules.nereid_test',
    ],
    package_dir={
        'trytond.modules.nereid_test': '.',
    },
    package_data={
        'trytond.modules.nereid_test': info.get('xml', [])
                + ['tryton.cfg', 'locale/*.po', 'tests/*.rst']
                + ['templates/*.*', 'templates/tests/*.*'],
    },
    zip_safe=False,
    platforms='any',
    entry_points="""
    [trytond.modules]
    nereid_test = trytond.modules.nereid_test
    """,
)
