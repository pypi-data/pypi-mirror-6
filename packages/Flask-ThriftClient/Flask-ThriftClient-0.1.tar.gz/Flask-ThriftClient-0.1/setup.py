#!/usr/bin/env python
"""
Flask-ThriftClient
-----------

Adds thrift client support to your Flask application

"""

from setuptools import setup

with open('README.md') as fd:
	long_description = fd.read()


setup(
	name='Flask-ThriftClient',
	version='0.1',
	url='https://bitbucket.org/chub/flask-thriftclient',
	license='BSD',
	author='Pierre Lamot',
	author_email='pierre.lamot@yahoo.fr',
	description='Adds thrift client support to your Flask application',
	long_description=long_description,
	packages=[
		'flask_thriftclient',
	],
	zip_safe=False,
	platforms='any',
	install_requires=[
		'Flask>=0.7',
		'thrift>=0.8'
	],
	test_suite='tests.thriftclient',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Framework :: Flask',
		'License :: OSI Approved :: BSD License',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development :: Libraries :: Python Modules'
	]
)
