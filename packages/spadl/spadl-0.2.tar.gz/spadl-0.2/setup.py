#!/usr/bin/env python

from setuptools import setup

VERSION = (0, 2)
VERSION_STR = ".".join(map(str, VERSION))


url='https://github.com/mila/spadl'

try:
    long_description = open('README.rst').read().decode('utf-8')
except IOError:
    long_description = "See %s" % url


setup(
    name='spadl',
    version=VERSION_STR,
    description='This package provides a standard logging handler which writes log records to DbgLog.',
    long_description=long_description,
    author='Miloslav Pojman',
    author_email='miloslav.pojman@gmail.com',
    url=url,
    py_modules=['spadl'],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Logging'
    ],
    zip_safe=False,
)
