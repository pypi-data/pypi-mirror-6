# -*- coding: utf-8 -*-
"""Manage frontend components like web server, load balancer and cache."""

from fabric import api


def restart_nginx():
    """Restart the NginX web server component."""
    api.sudo('/etc/init.d/nginx restart')


def restart_varnish():
    """Restart the Varnish caching proxy component."""
    api.sudo('/etc/init.d/varnish restart')


def restart_haproxy():
    """Restart the HA-Proxy load balancer component."""
    api.sudo('/etc/init.d/haproxy restart')
