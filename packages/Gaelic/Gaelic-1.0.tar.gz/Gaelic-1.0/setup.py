#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='Gaelic',
    version='1.0',
    description='Google App Engine package installer (pip bridge)',
    author='Jon Wayne Parrott',
    author_email='jjramone13@gmail.com',
    url='http://bitbucket.org/jonparrott/gaelic',
    py_modules=['gaelic'],
    install_requires=['distribute'],
    entry_points={
        'console_scripts': [
            'gaelic = gaelic:main'
        ]
    }
)
