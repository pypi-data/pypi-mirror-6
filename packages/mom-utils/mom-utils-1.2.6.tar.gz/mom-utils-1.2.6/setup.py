# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import os
import sys
from distutils import log

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


long_desc = ''' '''
requires = ['coards', 'numpy', 'PyYAML', 'NetCDF4', 'DateUtils']

setup(
    name='mom-utils',
    version='1.2.6',
    url='https://github.com/castelao/mom-utils',
    #download_url='https://bitbucket.org/castelao/mom4-utils',
    license='PSF',
    author='Guilherme Castelao, Luiz Irber',
    author_email='guilherme@castelao.net, luiz.irber@gmail.com',
    description='Python utilities for the GFDL\'s numerical model MOM',
    long_description=README + '\n\n' + NEWS,
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms='any',
    scripts=["bin/mom_namelist"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
