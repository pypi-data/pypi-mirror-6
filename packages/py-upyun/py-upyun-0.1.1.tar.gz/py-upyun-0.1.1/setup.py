#!/usr/bin/env python
import os
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

sdict = {
    'name' : 'py-upyun',
    'version' : '0.1.1',
    'description' : 'Youpai Usage API',
    'author' : 'zixuan zhang',
    'author_email' : 'zixuan.zhang.victor@gmail.com',
    'keywords' : ['youpai', 'upyun', 'cloud'],
    'packages' : ['youpai'],
    'install_requires': ['urllib3>=1.7'],
    'classifiers' : [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

setup(**sdict)

