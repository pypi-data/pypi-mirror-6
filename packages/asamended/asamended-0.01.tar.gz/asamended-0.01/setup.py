#!/usr/bin/env python

from setuptools import setup

long_description = """Client library for the asamended.com API.
"""

appname = "asamended"
version = "0.01"

setup(**{
    "name": appname,
    "version": version,
    "packages": [
        'asamended',
        ],
    "author": "Thom Neale",
    "author_email": "twneale@gmail.com",
    "long_description": long_description,
    "description": 'Client library for the asamended.com API.',
    "license": "MIT",
    "url": "http://asamended.github.com/python-asamended/",
    "platforms": ['any'],
    "scripts": [
    ]
})
