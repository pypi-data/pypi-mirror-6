#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='requests-vzauth',
    version='0.1.0',
    packages=[ 'requests_vzauth' ],
    install_requires=[ 'requests>=1.0.0' ],
    provides=[ 'requests_vzauth' ],
    author='Glenn E. Bailey III',
    author_email='replicant@dallaslamers.org',
    description='Verizon Cloud authentication handler for requests.',
    license='LICENSE',
    url='https://github.com/replicant0wnz/requests-vzauth',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
