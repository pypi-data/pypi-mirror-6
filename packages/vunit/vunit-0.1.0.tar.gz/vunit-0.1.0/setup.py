#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = '01388863189'
#
# Done by Gabriel Abdalla Cavalcante Silva at Receita Federal do Brasil,
#
# Licensed under the Apache License, Version 2.0, that can be viewed at:
#   http://www.apache.org/licenses/LICENSE-2.0
#
from distutils.core import setup
try:
    import py2exe
except ImportError:
    py2exe = None

setup(name='vunit',
      version='0.1.0',
      scripts=['vunit.py', 'vunit_cfg.py'],
      author='Gabriel Abdalla Cavalcante',
      data_files=['test_vunit_cfg.py', 'requirements.txt'],
      install_requires=['pysphere'],
      author_email='gabriel.cavalcante88@gmail.com',
      description = ("""Vunit is a python script that relies on pysphere library
      to test the Vmware Esxi and Vcenter environment with some usefull tests. 
      With this tool, system admins can verify impacts on environments before or 
      after a maintenance."""),
      url='https://github.com/gcavalcante8808',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: System :: Systems Administration',
      ]
)
