#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='guifi-nagios',
    version='0.1',
    description='Nagios helpers for guifi.net networks',
    long_description=open('README.txt').read(),
    author='Ales Zabala Alava (Shagi)',
    author_email='shagi@gisa-elkartea.org',
    url='http://lagunak.gisa-elkartea.org/projects/guifinagios/',
    packages=find_packages(),
    license='GPLv3+',
    zip_safe=False,
    install_requires=[
        'paramiko',
        'nagiosplugin',
    ],
    py_modules = ['ez_setup'],
    scripts=[
        'check_airos_version.py',
    ],
)
