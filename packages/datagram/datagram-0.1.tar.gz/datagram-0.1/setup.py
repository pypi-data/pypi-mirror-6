#!/usr/bin/env python

from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(	name='datagram',
		version='0.1',
		description='Useful Data Containers',
		author='Jose Maria Miotto',
		author_email='josemiotto+datagram@gmail.com',
		packages=['datagram'],
		license='GPL3',
		long_description=long_description,
		url='https://pypi.python.org/pypi/datagram'
		)