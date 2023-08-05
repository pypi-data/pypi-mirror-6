#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = '01388863189'
#
# Done by Gabriel Abdalla Cavalcante Silva at Receita Federal do Brasil,
#
# Licensed under the Apache License, Version 2.0, that can be viewed at:
#   http://www.apache.org/licenses/LICENSE-2.0
""" This module provides usefull functions to the project."""
import os
import pickle


def get_or_create_dir(directory='resource_lists'):
    """ Verify if the resource lists dir exists and create it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_resource_file(rfile, value):
    """ Take values and write them into a specified (r)file. """
    get_or_create_dir()
    with open('resource_lists/'+ rfile, 'wb') as resource_file:
        pickle.dump(value, resource_file)
