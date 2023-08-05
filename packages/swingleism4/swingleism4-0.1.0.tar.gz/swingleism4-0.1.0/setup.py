#!/usr/bin/env python

import re
from setuptools import setup

def get_long_description():
    with open('README.rst') as readme:
        return readme.read().strip().split('.. comment: readme-split', 1)[1]

setup(
    name='swingleism4',
    version='0.1.0',
    description='swingleism, yo',
    long_description=get_long_description(),
    author='John Swingle',
    author_email='johnswingle44@gmail.com',
    url='http://github.com/johnswingle44/swingleism/',
    license='MIT',
    include_package_data=True,
    py_modules=['swingleism'],
    install_requires = ['docopt'],
    entry_points={
        'console_scripts': ['swingleism = swingleism:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ]
)
