#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = '01388863189'
#
# Done by Gabriel Abdalla Cavalcante Silva at Receita Federal do Brasil,
#
# Licensed under the Apache License, Version 2.0, that can be viewed at:
#   http://www.apache.org/licenses/LICENSE-2.0
""" This module contain all functions neeeded to configure the environment
    to evaluate the Tests with success.
"""
import ConfigParser
import argparse


def create_vmtest_cfg(**kwargs):
    """ Create a new configuration file;if it exists, it will be overwritten."""
    config = ConfigParser.ConfigParser()
    config.add_section('Vcenter')
    config.set('Vcenter', 'user', kwargs['vuser'])
    config.set('Vcenter', 'pass', kwargs['vpass'])
    config.set('Vcenter', 'server', kwargs['vserver'])

    config.add_section('Host')
    config.set('Host', 'user', kwargs['huser'])
    config.set('Host', 'pass', kwargs['hpass'])
    config.set('Host', 'cluster', kwargs['hcluster'])

    with open(kwargs['cfg'], 'wb') as configfile:
        config.write(configfile)

    if kwargs.get('debug', None):
        return config


def read_vmtest_cfg(**kwargs):
    """ Read the configuration file previously created."""
    config = ConfigParser.ConfigParser()
    config.read(kwargs['cfg'])

    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-vuser', required=True)
    parser.add_argument('-vpass', required=True)
    parser.add_argument('-vserver', required=True)
    parser.add_argument('-huser', required=True)
    parser.add_argument('-hpass', required=True)
    parser.add_argument('-hlist', required=True)

    args = parser.parse_args()

    create_vmtest_cfg(vuser=args.vuser,
                      vpass=args.vpass,
                      vserver=args.vserver,
                      huser=args.huser,
                      hpass=args.hpass,
                      hcluster=args.hlist,
                      cfg='vmware.cfg'
    )
