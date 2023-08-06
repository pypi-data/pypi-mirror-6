# coding: utf-8
import os
from setuptools import setup, find_packages

AUTHOR = 'Cooper.luan'
AUTHOR_EMAIL = 'gc.suprs@gmail.com'
PACKAGE = 'sasoup'
VERSION = __import__('sasoup').__version__

setup(
    name='sasoup',
    version=VERSION,
    description='html parser base on rules',
    keywords='sasoup',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url='https://github.com/lannikcooper/sasoup',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyyaml',
        'lxml',
    ]
)
