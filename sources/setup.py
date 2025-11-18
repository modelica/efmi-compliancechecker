# Copyright (c) 2021-2025, Modelica Association and contributors
# 
# Licensed under the 3-Clause BSD license (the "License");
# you may not use this software except in compliance with
# the "License".
# 
# This software is not fully developed or tested.
# 
# THE SOFTWARE IS PROVIDED "as is", WITHOUT ANY WARRANTY
# of any kind, either express or implied, and the use is 
# completely at your own risk.
# 
# The software can be redistributed and/or modified under
# the terms of the "License".
# 
# See the "License" for the specific language governing
# permissions and limitations under the "License".

from setuptools import setup

setup(
    name='eFMIComplianceChecker',
    version='1.0.1',
    description='Tool for checking eFMUs for conformance with the eFMI® Standard.',
    author='Modelica Association and contributors',
    author_email='[efmi-info@googlegroups.com]',
    url="https://www.efmi-standard.org",
    license='BSD-3-Clause',
    packages=['eFMIComplianceChecker'],
    python_requires='>=3.13.9',
    install_requires=[
        'colorama>=0.4.6',
        'lxml>=6.0.2',
        'lark==0.12.0'
    ],
)
