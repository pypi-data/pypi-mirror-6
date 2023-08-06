#!/usr/bin/env python
from setuptools import setup, find_packages

packages = find_packages()
version_str = '5.2.1rc1'

setup(
    name = 'ConceptNet',
    version = version_str,
    description = 'A semantic network of general knowledge',
    author = "Rob Speer, Commonsense Computing Group",
    author_email = 'conceptnet@media.mit.edu',
    packages=packages,
    package_data={'conceptnet5': ['support_data/*']},
    install_requires=['metanl', 'assoc-space', 'xmltodict', 'pyyaml', 'flask'],
    license = 'GPLv3'
)

