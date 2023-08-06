# -*- python -*-
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Jan Dittberner

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


long_description = ""
with open('README.rst', 'r') as README:
    long_description += README.read()
long_description += """

License
=======

"""
with open('LICENSE', 'r') as LICENSE:
    long_description += LICENSE.read()
long_description += """

Changes
=======

"""
with open('ChangeLog.rst') as CHANGES:
    long_description += CHANGES.read()


setup(
    name="smstrade",
    url="https://gitorious.org/python-smstrade",
    description=(
        "a Python library and command line tool to send SMS via the smstrade"
        " service."),
    long_description=long_description,
    requires=['requests', 'appdirs'],
    author="Jan Dittberner",
    author_email="jan@dittberner.info",
    packages=find_packages(exclude=['tests']),
    setup_requires=['vcversioner'],
    license="MIT",
    vcversioner={
        'version_module_paths': ['smstrade/_version.py'],
    },
    entry_points={
        'console_scripts': [
            'smstrade_send = smstrade:send_sms',
            'smstrade_balance = smstrade:account_balance',
        ],
    },
    tests_require=['pytest', 'httpretty'],
    cmdclass = {'test': PyTest},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
