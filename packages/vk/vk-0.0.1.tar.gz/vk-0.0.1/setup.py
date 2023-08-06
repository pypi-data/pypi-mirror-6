#!/usr/bin/env python
from distutils.core import setup

version='0.0.1'

setup(
    name='vk',
    version=version,
    author='Dmitry Voronin',
    author_email='dimka665@gmail.com',

    packages=['vk'],

    url='https://github.com/dimka665/vk/',
    license = 'MIT license',
    description = "vk.com API wrapper",

#    long_description = open('README.rst').read() + open('CHANGES.rst').read(),
    long_description = '',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
