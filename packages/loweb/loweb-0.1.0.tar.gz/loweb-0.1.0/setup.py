# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='loweb',
    version='0.1.0',
    description='Tools to generate static web sites from yaml data and mustache templates',
    author='Gregory Vincic',
    author_email='g@7de.se',
    url='https://github.com/gregoryv/loweb',
    license='GPLv3',
    packages=['loweb'],
    include_package_data=True,
    install_requires=['pystache', 'PyYAML']
    )
