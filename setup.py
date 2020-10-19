#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pandas', 'jupyter_commons']

setup_requirements = ['pytest-runner', 'nox']

test_requirements = ['pytest', 'pytest-asyncio', 'pytest-datadir', 'nox']

setup(
    author="Stefan Braun",
    author_email='sb@stbraun.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    description="Functions helping with analysis of log files.",
    install_requires=requirements,
    requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='loganalysis',
    name='loganalysis',
    packages=find_packages(include=['loganalysis']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/stbraun/loganalysis',
    version='0.1.2',
    zip_safe=False,
)
