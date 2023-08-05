# -*- coding: utf-8 -*-
import sys
from setuptools import setup

setup(
    name='longtask',
    version='0.1.1',
    description='Long task runner.',
    author='Konrad Hałas',
    author_email='halas.konrad@gmail.com',
    url='https://github.com/konradhalas/longtask',
    packages=['longtask'],
    test_suite='longtask.tests',
    install_requires=['progressbar'],
    tests_require=['mock'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License'
    ]
)

