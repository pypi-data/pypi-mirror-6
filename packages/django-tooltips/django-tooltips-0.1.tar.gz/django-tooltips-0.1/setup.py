#!/usr/bin/env python
from setuptools import setup, find_packages

# try:
import pypandoc
description = pypandoc.convert('README.md', 'rst')
# except (IOError, ImportError):
#    description = ''

setup(
    name = 'django-tooltips',
    version = '0.1',
    description='Django manageable Bootstrap Tooltips',
    long_description=description,
    author = 'Sander van de Graaf',
    author_email = 'mail@svdgraaf.nl',
    url = 'http://github.com/svdgraaf/django-tooltips/',
    packages = find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
    ],
)