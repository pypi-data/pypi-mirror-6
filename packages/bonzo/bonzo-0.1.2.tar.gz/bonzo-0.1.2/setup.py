# -*- coding: utf-8 *-*
import os

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

from bonzo import __version__


with open('README.rst') as f:
    readme_content = f.read()

setup(
    name='bonzo',
    version=__version__,
    url='https://github.com/puentesarrin/bonzo',
    description='Bonzo is a minimalistic SMTP Proxy built on top of Tornado.',
    long_description=readme_content,
    author='Jorge Puente Sarrín',
    author_email='puentesarrin@gmail.com',
    packages=['bonzo'],
    keywords=['bonzo', 'tornado', 'smtp', 'proxy'],
    install_requires=['tornado >= 3.0'],
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: Proxy Servers'],
    test_suite='tests.runtests',
)
