# -*- coding: utf-8 -*-
"""Fabric exception wrapper."""

from fabric import api


def err(msg):
    return api.abort(msg)


def missing_env(param):
    return err('The definition for the param "%s" is missing!' % param)
