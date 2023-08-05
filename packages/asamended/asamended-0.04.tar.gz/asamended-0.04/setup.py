#!/usr/bin/env python

from setuptools import find_packages, setup

long_description = """This package is a Client library for the asamended.com API.
"""

appname = "asamended"
version = "0.04"

setup(**{
    "name": appname,
    "version": version,
    "packages": [
        'asamended',
        ],
    "install_requires": ["tater", "networkx", "requests"],
    "author": "Thom Neale",
    "author_email": "twneale@gmail.com",
    "packages": find_packages(exclude=['tests*']),
    "package_data": {
        'asamended.uscode': ['*.py'],
    },
    "long_description": long_description,
    "description": 'Client library for the asamended.com API.',
    "license": "MIT",
    "url": "http://asamended.github.com/python-asamended/",
    "platforms": ['any'],
    "scripts": [
    ]
})
