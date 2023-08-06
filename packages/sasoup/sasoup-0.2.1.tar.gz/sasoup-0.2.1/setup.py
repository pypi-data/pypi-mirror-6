# coding: utf-8
import os
from setuptools import setup, find_packages

AUTHOR = 'Cooper.luan'
AUTHOR_EMAIL = 'gc.suprs@gmail.com'
PACKAGE = 'sasoup'


def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'sasoup/version.py')) as f:
        locals = {}
        exec(f.read(), locals)
        return locals['VERSION']
    raise RuntimeError('No version info found.')

setup(
    name='sasoup',
    version=get_version(),
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
