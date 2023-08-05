#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='gae-pesapal',
    version='0.0.1',
    description='Pesapal NDB Model',
    author='Mitchel Kelonye',
    author_email='kelonyemitchel@gmail.com',
    url='https://github.com/kelonye/gae-pesapal',
    packages=['gae_pesapal',],
    package_dir = {'gae_pesapal': 'lib'},
    license='MIT',
    zip_safe=True
)