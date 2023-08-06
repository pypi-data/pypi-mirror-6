# coding=utf-8
"""
Package it
"""
from setuptools import setup

setup(
    name='voyeur',
    version='0.1.0',
    packages=['tests', 'voyeur'],
    url='https://github.com/gilles/voyeur',
    license='MIT',
    author='Gilles Devaux',
    author_email='gilles.devaux@gmail.com',
    description='Dead simple library for object serialization',
    tests_require=['nose', 'coverage'],
    test_suite='nose.collector'
)
