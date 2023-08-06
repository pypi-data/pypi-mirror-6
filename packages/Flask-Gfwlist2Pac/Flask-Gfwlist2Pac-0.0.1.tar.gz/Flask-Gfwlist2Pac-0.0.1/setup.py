#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask-Gfwlist2Pac
----------

A flask application to generate PAC file based on gfwlist

"""

from setuptools import setup, find_packages
from pip.req import parse_requirements

setup(
    name='Flask-Gfwlist2Pac',
    version='0.0.1',
    url='https://github.com/leoleozhu/flask_gfwlist2pac/',
    license='MIT',
    author='leoleozhu',
    author_email='leiping.zhu@gmail.com',
    description='Flask application to generate PAC file based on gfwlist',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        str(x.req) for x in parse_requirements('requirements.txt')],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
