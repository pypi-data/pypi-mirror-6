#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from distutils.core import setup

setup(name='pyicp7k',
    version='0.1',
    description='Python interface for communicating ICP DAS 7k series devices',
    author='Matwey V. Kornilov',
    author_email='matwey.kornilov@gmail.com',
    url='https://bitbucket.org/matwey/pyicp7k',
    packages=['icp7k'],
    scripts=['icp7kctl.py'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Hardware',]
    )

