#!/usr/bin/env python

from __future__ import print_function, division
import re

import yaml


def load_configuration(yaml_string, kw=None, missing_fmt=None):
    environ = yaml.safe_load(yaml_string)
    environ = _expand_config_vars(environ, updates=kw, missing_fmt=missing_fmt)

    return environ


def _rec_replace(env, value, missing_fmt=None):
    if missing_fmt is None:
        fmt = str
    else:
        fmt = missing_fmt

    finder_subkeys = re.compile('\[\{(\w*)\}\]')
    finder_vars = re.compile('\{(\w*)\}')
    newvalue = value

    for k in finder_subkeys.findall(value):
        newvalue = _rec_replace(env,
                                newvalue.replace("{%s}" % k, env[k]),
                                missing_fmt=missing_fmt)

    newvalue = fmt.format(newvalue, **env)

    keys = finder_vars.findall(newvalue)
    while keys:
        for k in keys:
            newvalue = _rec_replace(env,
                                    #newvalue.replace("{%s}" % k, env[k]),
                                    fmt.format(newvalue, **env),
                                    missing_fmt=missing_fmt)
        keys = finder_vars.findall(newvalue)

    return newvalue


def _env_replace(old_env, ref=None, missing_fmt=None):
    new_env = {}
    for k in old_env:
        try:
            # tests if value is a string
            old_env[k].split(' ')
        except AttributeError:
            # if it's not a string, let's test if it is a dict
            try:
                old_env[k].keys()
            except AttributeError:
                # if it's not, just set new_env with it
                new_env[k] = old_env[k]
            else:
                # Yup, a dict. Need to replace recursively too.
                new_env[k] = _env_replace(old_env[k],
                                          ref if ref else old_env,
                                          missing_fmt=missing_fmt)
        else:
                # else start replacing vars
                new_env[k] = _rec_replace(ref if ref else old_env,
                                          old_env[k],
                                          missing_fmt=missing_fmt)

    return new_env


def _expand_config_vars(d, updates=None, missing_fmt=None):
    if updates:
        d.update(updates)
    new_d = _env_replace(d, missing_fmt=missing_fmt)

    return new_d
