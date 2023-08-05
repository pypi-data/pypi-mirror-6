#!/usr/bin/env python

from setuptools import setup

setup(
    name         = 'nepho',
    version      = '1.0.0',
    url          = 'http://github.com/huit/nepho',
    description  = 'Simplified cloud orchestration tool for constructing virtual data centers',
    packages     = ['nepho', 'nepho.core', 'nepho.cli', 'nepho.providers'],
    author       = 'Harvard University Information Technology',
    author_email = 'ithelp@harvard.edu',
    license      = 'MIT',
    #scripts      = ['bin/nepho'],
    entry_points = {
        'console_scripts': [
            'nepho=nepho.cli.bootstrap:run',
        ]
    },
    dependency_links = [
        'git+git://github.com/cement/cement.git@2.1.4.dev20131029203905#egg=cement-2.1.4-dev'
    ],
    install_requires = [
        'argparse>=1.2',
        'boto>=2.0',
        'Jinja2',
        'PyYAML',
        'cement>=2.1,==2.1.4-dev',
        'termcolor',
        'colorama',
        'gitpython==0.3.2.RC1',
        'requests>=1.2.3',
        'python-vagrant==0.4.0'
    ],
    setup_requires = [
        'setuptools_git>=1.0',
        'flake8>=2.1.0',
        'nose>=1.3.0',
        'coverage>=3.7',
    ],
    test_suite = 'nose.collector',
)
