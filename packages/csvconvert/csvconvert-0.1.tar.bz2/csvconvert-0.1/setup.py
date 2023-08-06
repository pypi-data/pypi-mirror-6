# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from setuptools import setup

setup(
    name='csvconvert',
    version='0.1',
    description='A tool to convert between various csv variants',
    autor='Szymon Pyżalski',
    author_email='szymon@pythonista.net',
    py_modules=['csvconvert'],
    entry_points="""[console_scripts]
    csvconvert = csvconvert:convert"""
)
