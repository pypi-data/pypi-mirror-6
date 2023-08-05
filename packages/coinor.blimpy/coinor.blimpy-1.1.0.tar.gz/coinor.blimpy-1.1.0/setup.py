#!/usr/bin/env python

from setuptools import setup
import setuptools

setup(name='coinor.blimpy',
      version='1.1.0',
      description='Basic List Implementation in Python',
      long_description='BLiMPy (Basic List Implementation in Python) is a basic implementation of a linked list data structure that is a drop-in replacement for the Python list. It supports all basic list methods. The data structure is not as efficient as the Python list for many operations and in most cases, should not be used except in a teaching setting. It was developed to illustrate basic principles and to be used with GiMPy, a graph implementation in Python. BLImPy includes a stack data structure, a queue data structure, and a priority queue data structure.',
      author='Aykut Bulut, Ted Ralphs',
      author_email='{aykut,ted}@lehigh.edu',
      license='Eclipse Public License',
      url='http://projects.coin-or.org/CoinBazaar/wiki/Projects/GIMPy',
      namespace_packages=['coinor'],
      packages=['coinor.blimpy','coinor'],
      package_dir = {'coinor': 'src'},
     )
