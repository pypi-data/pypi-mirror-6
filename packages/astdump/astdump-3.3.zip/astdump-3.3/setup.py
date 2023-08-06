#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'astdump',
    version = '3.3',
    author = 'anatoly techtonik',
    author_email = 'techtonik@gmail.com',
    description = 'Extract information from Python modules without importing',
    license = 'Public Domain',
    url = 'https://bitbucket.org/techtonik/astdump',
    long_description = open('README.rst', 'rb').read(),
    classifiers=[
        u'Development Status :: 5 - Production/Stable',
        u'Intended Audience :: Developers',
        u'License :: Public Domain',
        u'Programming Language :: Python',
        u'Programming Language :: Python :: 2',
        u'Programming Language :: Python :: 3',
        u'Topic :: Software Development',
        u'Topic :: Software Development :: Disassemblers'],
    py_modules=['astdump']
)
