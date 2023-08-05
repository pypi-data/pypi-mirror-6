# -*- coding: utf-8 -*-
import sys
import os

from setuptools import setup, find_packages
from importlib import import_module


def name():
    return 'setupbuilder'


def version():
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(setup_dir, 'src')

    sys.path.insert(0, src_dir)
    try:
        module = import_module(name())
    except ImportError:
        return '0.0.0'
    else:
        return getattr(module, '__version__', '0.0.0')


setup(
    version=version(),
    name=name(),
    description='Command to generate setup for python packages.',
    long_description='',
    license='GPLv3',
    platforms=['linux', 'linux2', 'osx', 'win32', 'win64'],
    author='Rodrigo Pinheiro Matias',
    author_email='rodrigopmatias@gmail.com',
    url='http://pypi.python.org/setupbuilder',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'setupbuilder = setupbuilder:main',
            'setupcompress = setupbuilder:data_compress',
        ]
    }
)
