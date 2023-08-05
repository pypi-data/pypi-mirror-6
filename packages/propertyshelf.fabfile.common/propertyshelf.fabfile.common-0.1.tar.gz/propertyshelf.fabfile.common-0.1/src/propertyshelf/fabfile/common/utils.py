# -*- coding: utf-8 -*-
"""Various utility functions."""

from datetime import datetime
from fabric import api
from fabric.contrib.files import exists
from propertyshelf.fabfile.common.exceptions import err


def backup_dev_packages(folder=None, user=None, config=None):
    """Backup the development packages."""
    config = config or err('Need application config.')
    folder = folder or config.get('app', {}).get('dir')
    folder = folder or err('Folder must be set!')
    user = user or config.get('user') or err('Required user must be set!')
    with api.settings(sudo_user=user):
        # Backup buildout src packages.
        with api.cd(folder):
            if exists('src', use_sudo=True):
                now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                backup_folder = 'src_backups/%s' % now
                api.sudo('mkdir -p %s' % backup_folder)
                api.sudo('mv ./src/* %s' % backup_folder, warn_only=True)


def update_dev_packes(folder=None, user=None, config=None):
    """Update the development packages."""
    config = config or err('Need application config.')
    folder = folder or config.get('app', {}).get('dir')
    folder = folder or err('Folder must be set!')
    user = user or config.get('user') or err('Required user must be set!')
    with api.settings(sudo_user=user):
        # Update buildout src packages.
        with api.cd(folder):
            if exists('./bin/develop', use_sudo=True):
                api.sudo('./bin/develop up -f')


def run_buildout(folder=None, user=None, config=None):
    """Run the buildout."""
    config = config or err('Need application config.')
    folder = folder or config.get('app', {}).get('dir')
    folder = folder or err('Folder must be set!')
    user = user or config.get('user') or err('Required user must be set!')
    with api.settings(sudo_user=user):
        # Run buildout.
        with api.cd(folder):
            api.sudo('./bin/buildout')


def supervisorctl(command=None, service=None):
    """Control supervisor services."""
    api.sudo('supervisorctl %s %s' % (command, service), warn_only=True)
