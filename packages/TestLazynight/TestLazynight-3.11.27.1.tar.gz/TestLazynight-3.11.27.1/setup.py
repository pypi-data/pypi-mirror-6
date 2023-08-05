# coding: utf-8
#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open('README').read()

setup(
    name='TestLazynight',
    version='3.11.27.1',
    description=readme.partition('\n')[0],
    long_description=readme,
    author='flowerowl',
    author_email='lazynight@gmail.com',
    url='http://read.sohu.com',
    packages=find_packages(exclude=['*.pyc']),
    include_package_data=True,
    package_data={
    },
    install_requires=[
        "web.py",
    ],
    entry_points={
        'console_scripts': [
            'test = test.main:main',
        ]
    },
)
