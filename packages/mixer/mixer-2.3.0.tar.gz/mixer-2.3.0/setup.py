#!/usr/bin/env python

""" mixer -- Generate tests data.

mixer -- Description

"""
import sys
from os import path as op

from setuptools import setup

from mixer import __version__, __project__, __license__


def read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''

install_requires = [l for l in read('requirements.txt').split('\n')
                    if l and not l.startswith('#')]

tests_require = [l for l in read('requirements-tests.txt').split('\n')
                 if l and not l.startswith('#')]

if sys.version_info < (2, 7):
    install_requires.append('importlib')
    install_requires.append('ordereddict')


setup(
    name=__project__,
    version=__version__,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),
    keywords = "django flask sqlalchemy testing mock stub mongoengine data".split(), # noqa

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url='http://github.com/klen/mixer',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],

    packages=['mixer', 'mixer.backend'],
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
)

# lint_ignore=F0401
