#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='GauminIpuin',
    version='0.2',
    description='Interactive book library',
    author='Ales Zabala Alava (Shagi)',
    author_email='shagi@gisa-elkartea.org',
    url='http://lagunak.gisa-elkartea.org/projects/gauminipuin/',
    packages=find_packages(),
    license="GPLv3+",
    package_data={
        '': ['*.kv', 'imgs/*'],
    },
)
