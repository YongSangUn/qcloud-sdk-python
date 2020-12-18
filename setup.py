#!/usr/bin/env python

import os
from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)

setup(
    name='qcloud_sdk',
    version='1.2',
    description='Simplified some functions of Tencent Cloud. ',
    author='rylan.long',
    author_email='sangun.yong@gmail.com',
    url='http://github.com/YongSangUn/qcloud-sdk-python',
    packages=find_packages(exclude=["tests*"]),
    scripts=[],
)
