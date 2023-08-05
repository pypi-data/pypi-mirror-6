# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys
sys.path.insert(0, '.')
version = __import__('rmb').__version__

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    print('WARNING: Could not locate pandoc, using Markdown long_description.')
    long_description = open('README.md').read()

description = long_description.splitlines()[0].strip()


setup(
    name='rmb',
    url='http://github.com/likang/python-rmb',
    download_url='http://pypi.python.org/pypi/rmb',
    version=version,
    description=description,
    long_description=long_description,
    license='MIT',
    platforms=['any'],
    py_modules=['rmb'],
    author='Kang Li',
    author_email='eastern.fence@gmail.com',
    install_requires=[
        'setuptools >= 0.6b1',
    ],
)
