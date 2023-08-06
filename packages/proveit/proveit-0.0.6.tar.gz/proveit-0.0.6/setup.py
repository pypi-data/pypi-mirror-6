#!/usr/bin/env python
from setuptools import setup

setup(
    author='Nick Williamson',
    author_email='nick@nickw.info',
    url = 'https://github.com/ConceptPending/proveit',
    description="Implementation of gmaxwell's suggestion of proving account balances",
    name='proveit',
    packages=[''],
    install_requires=['bitcoin-python', 'simplejson'],
    version='0.0.6'
)
