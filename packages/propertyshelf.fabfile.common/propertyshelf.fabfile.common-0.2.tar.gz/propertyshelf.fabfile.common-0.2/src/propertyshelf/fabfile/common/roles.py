# -*- coding: utf-8 -*-
"""Manage chef roles."""

from chef import autoconfigure, Role, Search
from fabric import api
from fabric.colors import green, red
from propertyshelf.fabfile.common.exceptions import missing_env


def check(role, roles=None):
    """Check if a given role is available on the chef server."""
    if not roles:
        chef_api = autoconfigure()
        roles = Role.list(api=chef_api)
    return role in roles


def get_required():
    """Get a list of required roles."""
    result = {}

    role_base = api.env.get('role_base')
    if role_base:
        result['role_base'] = role_base

    role_database = api.env.get('role_database')
    role_database = role_database or missing_env('role_database')
    result['role_database'] = role_database

    role_frontend = api.env.get('role_frontend')
    role_frontend = role_frontend or missing_env('role_frontend')
    result['role_frontend'] = role_frontend

    role_staging = api.env.get('role_staging')
    if role_staging:
        result['role_staging'] = role_staging

    role_worker = api.env.get('role_worker')
    role_worker = role_worker or missing_env('role_worker')
    result['role_worker'] = role_worker

    return result


def check_required():
    """Check if the required roles are available."""
    chef_api = autoconfigure()
    chef_roles = Role.list(api=chef_api)

    for role in get_required().values():
        if check(role, chef_roles):
            print(green('Role %s available.') % role)
        else:
            print(red('Role %s NOT available.') % role)


def list_nodes(role_list=None):
    """List all available nodes with given roles."""
    if not role_list:
        role_list = get_required().values()
    else:
        role_list = role_list.split(';')

    chef_api = autoconfigure()
    for role in role_list:
        print('Role: %s' % role)
        query = 'role:%s' % role
        for row in Search('node', query, api=chef_api):
            print('- %s: %s' % (row['name'], row.object['ipaddress']))
        print
