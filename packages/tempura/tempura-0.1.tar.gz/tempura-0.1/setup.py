import os
from setuptools import setup

setup(
    name = "tempura",
    version = "0.1",
    url = "https://github.com/tengu/py-tempura",
    description = "not-a-template",
    py_modules = ['tempura'],
    entry_points={"console_scripts": [ 'tempura=tempura:main' ]},
    # install_requires=['baker'],
    zip_safe=False,
)
