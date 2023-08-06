#! /usr/bin/env python

import os
import string

import pytest


from rec_env import load_configuration


class MissingFormatter(string.Formatter):
    env_vars = {
      'USER': 'user',
      'HOME': 'home',
      'ARCHIVE_OCEAN': 'ocean'
    }

    def get_value(self, key, args, kwargs):
        try:
            if hasattr(key, "mod"):
                return args[key]
            else:
                return kwargs[key]
        except:
            return self.env_vars[key]


with open(os.path.join(os.path.dirname(__file__), 'namelist.yaml')) as f:
    TEST_YAML = f.read()


def test_recursive_replace():
    env = load_configuration(TEST_YAML, missing_fmt=MissingFormatter())
    assert env['workdir'] == "/scratchout/grupos/ocean/home/user/expbase/coupled.pgi"


def test_recursive_replace_nested_complex():
    env = load_configuration(TEST_YAML, missing_fmt=MissingFormatter())
    assert env['regrid_2d_namelist']['vars']['regrid_2d_nml']['dest_grid'] == (
        "/scratchout/grupos/ocean/home/user/expbase/coupled.pgi/gengrid/grid_spec_UNION.nc")
