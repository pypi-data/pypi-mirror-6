# -*- coding: utf-8 -*-
"""Bootstrap new servers."""

from fabric import api
from propertyshelf.fabfile.common import rackspace
from propertyshelf.fabfile.common.exceptions import missing_env


def database(nodename=None, image=None, flavor=None):
    """Bootstrap a new standalone database server."""
    nodename = nodename or api.env.get('nodename_database')
    nodename = nodename or missing_env('nodename_database')

    image = image or api.env.get('os_image')
    image = image or missing_env('os_image')

    flavor = flavor or api.env.get('flavor_database')
    flavor = flavor or missing_env('flavor_database')

    role = api.env.get('role_database')
    role = role or missing_env('role_database')

    runlist = ','.join([
        'role[%s]' % role,
        'recipe[propertyshelf::rackspace_backup]',
    ])

    opts = dict(
        environment='production',
        flavor=flavor,
        image=image,
        nodename=nodename,
        runlist=runlist,
        servername=nodename,
    )
    rackspace.create(**opts)


def frontend(nodename=None, image=None, flavor=None):
    """Bootstrap a new standalone frontend server."""
    nodename = nodename or api.env.get('nodename_frontend')
    nodename = nodename or missing_env('nodename_frontend')

    image = image or api.env.get('os_image')
    image = image or missing_env('os_image')

    flavor = flavor or api.env.get('flavor_database')
    flavor = flavor or missing_env('flavor_database')

    role = api.env.get('role_frontend')
    role = role or missing_env('role_frontend')

    runlist = ','.join([
        'role[%s]' % role,
    ])

    opts = dict(
        environment='production',
        flavor=flavor,
        image=image,
        nodename=nodename,
        runlist=runlist,
        servername=nodename,
    )
    rackspace.create(**opts)


def worker(nodename=None, image=None, flavor=None):
    """Bootstrap a new standalone application worker."""
    number = rackspace.next_client_number(
        environment='production',
        rolename=api.env.role_worker,
    )

    nodename = nodename or api.env.get('nodename_worker') + '-%02d' % number
    nodename = nodename or missing_env('nodename_worker')

    image = image or api.env.get('os_image')
    image = image or missing_env('os_image')

    flavor = flavor or api.env.get('flavor_worker')
    flavor = flavor or missing_env('flavor_worker')

    role = api.env.get('role_worker')
    role = role or missing_env('role_worker')

    runlist = ','.join([
        'role[%s]' % role,
    ])

    opts = dict(
        environment='production',
        flavor=flavor,
        image=image,
        nodename=nodename,
        runlist=runlist,
        servername=nodename,
    )
    rackspace.create(**opts)


def staging(nodename=None, image=None, flavor=None):
    """Bootstrap a staging system."""
    nodename = nodename or api.env.get('nodename_staging')
    nodename = nodename or missing_env('nodename_staging')

    image = image or api.env.get('os_image')
    image = image or missing_env('os_image')

    flavor = flavor or api.env.get('flavor_database')
    flavor = flavor or missing_env('flavor_database')

    role = api.env.get('role_staging')
    role = role or missing_env('role_staging')

    runlist = ','.join([
        'role[%s]' % role,
    ])

    opts = dict(
        environment='staging',
        flavor=flavor,
        image=image,
        nodename=nodename,
        runlist=runlist,
        servername=nodename,
    )
    rackspace.create(**opts)
