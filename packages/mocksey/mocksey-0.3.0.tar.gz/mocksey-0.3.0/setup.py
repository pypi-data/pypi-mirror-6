#!/usr/bin/env python

import mocksey

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'mocksey',
]

requires = []

setup(
    name='mocksey',
    version=mocksey.__version__,
    description=mocksey.__description__,
    long_description=open('README.rst').read(),
    author='Chris McGraw',
    author_email='mitgr81+mocksey@mitgr81.com',
    url='https://github.com/mitgr81/mocksey',
    test_suite='mocksey.tests',
    packages=packages,
    package_dir={'mocksey': 'mocksey'},
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    license="MIT",
    zip_safe=False,
    classifiers=(
        b'Intended Audience :: Developers',
        b'Natural Language :: English',
        b'License :: OSI Approved :: MIT License',
        b'Operating System :: OS Independent',
        b'Development Status :: 4 - Beta',
        b'Topic :: Software Development :: Testing',
        b'Programming Language :: Python',
        b'Programming Language :: Python :: 2.6',
        b'Programming Language :: Python :: 2.7',
        b'Programming Language :: Python :: 3',
        b'Programming Language :: Python :: 3.1',
        b'Programming Language :: Python :: 3.2',
        b'Programming Language :: Python :: 3.3',
    ),
)
