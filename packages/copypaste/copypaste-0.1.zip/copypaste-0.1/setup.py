# -*- coding: utf-8 -*-

import os

from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='copypaste',
    version='0.1',
    description='Platform independent copy + paste library for Python',
    long_description=read('README.rst'),
    classifiers=(
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: IronPython',
    ),
    author='Nikita Grishko',
    author_email='grin.minsk@gmail.com',
    url='http://gr1n.github.io/copypaste/',
    license='MIT',
    packages=find_packages(),
    extras_require={
        'windows': (
            'pywin32',
        ),
        'test': (
            'tox',
            'pytest',
        ),
        'development': (
            'zest.releaser',
            'check-manifest',
        ),
    },
    include_package_data=True,
    zip_safe=False,
)
