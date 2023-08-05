#/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

setup(
    name="geocodio",
    version="1.0.1",
    description="Simple wrapper for geocod.io address service",
    author="David Stanley",
    author_email="davidstanley01@gmail.com",
    url="https://github.com/davidstanley01/geocodio.py",
    license='BSD License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
    install_requires=[
      'Requests>=2.2.0'

    ],
)
