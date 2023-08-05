#!/usr/bin/env python


from distutils.core import setup

import wyrm


setup(
    name='Wyrm',
    version=wyrm.__version__,
    description='Toolbox for Brain Computer Interfacing Experiments.',
    long_description='A Python toolbox of on-line BCI experiments and off-line BCI data analysis.',
    author='Bastian Venthur',
    author_email='bastian.venthur@tu-berlin.de',
    url='http://github.com/venthur/wyrm/',
    download_url='http://github.com/venthur/wyrm/',
    license='GPL2',
    platforms='any',
    packages=['wyrm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Libraries',
        ]
)
