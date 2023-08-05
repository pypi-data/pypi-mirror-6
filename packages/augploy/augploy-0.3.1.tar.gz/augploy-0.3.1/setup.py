#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re

from os import path
from distutils.core import setup

# Parse version from augploy
augploy_content = open(path.join(path.dirname(__file__), 'augploy')).read()
version_matches = re.findall(r"^VERSION\s*=\s*'([\.\d]+)'$", augploy_content, re.MULTILINE)
version = version_matches[0]

setup(
    name='augploy',
    version=version,
    description='AUGmentum dePLOYment automation tool, powered by ansible',
    author='Augmentum ops team',
    install_requires=['ansible ==1.4.1'],
    scripts=['augploy']
)
