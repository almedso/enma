#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


try:
    from _version import __version__
except ImportError:
    __version__ = "0.1.a1"

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='enma',
    version=__version__,
    description='Entitlement Management WebApp',
    long_description=readme + '\n\n' + history,
    author='Volker Kempert',
    author_email='volker.kempert@pixmeter.com',
    url='https://github.com/volker_kempert/enma',
    packages=[
        'enma',
    ],
    package_dir={'enma':
                 'enma'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='entitlement management webapp',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
