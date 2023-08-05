# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

import floppymodelforms

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = floppymodelforms.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()

setup(
    name='django-floppymodelforms',
    version=version,
    description="A hack to force Django's ModelForm to use floppyforms' fields.",
    long_description=readme,
    author='Henrique Bastos',
    author_email='henrique@bastos.net',
    url='https://github.com/henriquebastos/django-floppymodelforms',
    packages=[
        'floppymodelforms',
    ],
    include_package_data=True,
    install_requires=[
        'django',
        'django-floppyforms'
    ],
    license="BSD",
    zip_safe=False,
    keywords='floppymodelforms floppy forms django',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
