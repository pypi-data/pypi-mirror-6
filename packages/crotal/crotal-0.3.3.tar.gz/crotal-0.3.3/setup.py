#coding:utf-8
import os
import sys

from setuptools import setup, find_packages


setup(
    name = "crotal",
    version = "0.3.3",
    packages = find_packages(),

    include_package_data = True,

    entry_points = {
        'console_scripts' : [
            'crotal = crotal.main:main'
        ],
    },
    package_data = {
        'crotal' : [ '*.data' ]
    },
    install_requires = ['Jinja2==2.7.1','markdown==2.3.1','PyYAML==3.10','Pygments==1.6'],
    author = "Dinever",
    author_email = 'dingpeixuan911@gmail.com',
    url = "http://github.com/dinever/crotal",
    description = 'A static site generator written in python.',
)
