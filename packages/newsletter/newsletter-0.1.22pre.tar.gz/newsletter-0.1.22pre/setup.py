#!/usr/bin/env python
##    newsletter - Python newsletter library
##    Copyright (C) 2011 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com


# This is the distutils setup script for newsletter.
#
# To configure, compile, install, just run this script.

try:
    DESCRIPTION = open('readme.rst').read()
    CHANGES = open('CHANGES.txt').read()
    INSTALL = open('install.rst').read()
    TODO = open('TODO.txt').read()
except:
    DESCRIPTION = "newsletter is for making newsletters with python"
    CHANGES = ""
    INSTALL = ""
    TODO = ""

EXTRAS = {}

long_description = DESCRIPTION + INSTALL + CHANGES + TODO
#import sys
#if "checkdocs" in sys.argv:
#    print long_description

METADATA = {
    'name':             'newsletter',
    'version':          '0.1.22pre',
    'license':          'LGPL',
    'url':              'https://bitbucket.org/illume/newsletter',
    'author':           'Rene Dudfield',
    'author_email':     'renesd@gmail.com',
    'description':      'alpha newsletter software for #python. newsletterapp more extensible.',
    'long_description': long_description,
    'classifiers':      [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Internet :: WWW/HTTP :: WSGI',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: Python Modules ',
    ],
}

import sys

if "bdist_msi" in sys.argv:
    # hack the version name to a format msi doesn't have trouble with
    METADATA["version"] = METADATA["version"].replace("pre", "a0")
    METADATA["version"] = METADATA["version"].replace("rc", "b0")
    METADATA["version"] = METADATA["version"].replace("release", "")


cmdclass = {}
PACKAGEDATA = {
    'cmdclass':    cmdclass,

    'package_dir': {'newsletter': 'newsletter',
                    #'newsletter.tests': 'test',
                   },
    'packages': ['newsletter',
                 'newsletter.tests', 
                 'newsletter.base', 
                 'newsletter.newsletterapp', 
                ],
    'scripts': ['scripts/newsletterapp'],
}





from distutils.core import setup, Command

# allow optionally using setuptools for bdist_egg.
using_setuptools = False


# it appears that setuptools is required to install all the files in newsletter/newsletterapp/
if 1 or "-setuptools" in sys.argv:
    using_setuptools = True

    from setuptools import setup, Command
    if "-setuptools" in sys.argv:
        sys.argv.remove ("-setuptools")

    EXTRAS.update({'include_package_data': True,
                   'install_requires': ["cherrypy", "pywebsite", "feedparser"],
                   'zip_safe': False,
                   'test_suite' : 'newsletter.tests',
                   }
    )


# test command.  For doing 'python setup.py test'
class TestCommand(Command):
    user_options = [ ]
    def initialize_options(self):
        self._dir = os.getcwd()
    def finalize_options(self): pass
    def run(self):
        import newsletter.tests
        newsletter.tests.main()

# we use our test command.
if not using_setuptools:
    import os
    cmdclass['test'] = TestCommand


PACKAGEDATA.update(METADATA)
PACKAGEDATA.update(EXTRAS)
setup(**PACKAGEDATA)

