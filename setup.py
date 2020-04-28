#!/usr/bin/env python

import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('athenacli/__init__.py') as f:
    version = ast.literal_eval(
        _version_re.search(f.read()).group(1)
    )

description = 'CLI for Athena Database. With auto-completion and syntax highlighting.'

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requirements = [
    'click>=7.0',
    'Pygments>=1.6',
    'prompt_toolkit>=2.0.6,<3.0.0',
    'sqlparse>=0.3.0,<0.4.0',
    'configobj>=5.0.5',
    'cli_helpers[styles]>=1.1.0',
    'botocore>=1.5.52',
    'boto3>=1.4.4',
    'PyAthena>=1.2.2',
]

setup(
    name='athenacli',
    author='athenacli Core Team',
    author_email="athenacli@googlegroups.com",
    version=version,
    packages=find_packages(),
    package_data={
        'athenacli': [
            'athenaclirc',
            'packages/literals/literals.json'
        ]
    },
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dbcli/athenacli",
    install_requires=install_requirements,
    entry_points={
        'console_scripts': ['athenacli = athenacli.main:cli'],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
