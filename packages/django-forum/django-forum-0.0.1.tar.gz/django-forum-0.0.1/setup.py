#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-forum',
    version='0.0.1',

    author='Dmitry Voronin',
    author_email='dimka665@gmail.com',

    url='https://github.com/dimka665/django-forum',
    description='Django forum app',
    long_description=open('README.rst').read(),

    packages=find_packages(),
    # install_requires='requests',

    license='MIT license',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django forum reusable app',
)
