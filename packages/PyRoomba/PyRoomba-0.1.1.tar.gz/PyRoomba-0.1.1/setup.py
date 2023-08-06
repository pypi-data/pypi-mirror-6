#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='PyRoomba',
    version='0.1.1',
    author='Marcell Vazquez-Chanlatte',
    packages=find_packages(),
    url='',
    license='LICENSE',
    description='',
    requires = ['amqp', 'pyserial'],
)
