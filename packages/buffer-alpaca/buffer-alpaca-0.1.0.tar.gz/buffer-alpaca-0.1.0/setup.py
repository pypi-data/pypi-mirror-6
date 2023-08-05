import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
	name='buffer-alpaca',
	version='0.1.0',
	description='Buffer API library client for python',
	author='Pavan Kumar Sunkara',
	author_email='pavan.sss1991@gmail.com',
	url='https://bufferapp.com',
	license='MIT',
	install_requires=[
		'requests >= 2.1.0'
	],
	packages=[
		'buffer'
	],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Topic :: Software Development :: Libraries :: Python Modules',
	]
)
