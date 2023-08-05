# -*- coding: utf-8 -*-
"""Manage MLS application client components."""

from fabric import api
from mls.fabfile.utils import mls_config
from propertyshelf.fabfile.common import rackspace
from propertyshelf.fabfile.common import utils
from propertyshelf.fabfile.common.exceptions import missing_env


@api.task
def remove():
    """Remove an existing MLS application client."""
    role = api.env.get('role_worker')
    role = role or missing_env('role_worker')
    opts = dict(
        environment='production',
        role=role,
    )
    rackspace.remove(**opts)


@api.task
@api.roles('worker')
def update():
    """Update the client packages."""
    utils.supervisorctl(command='stop', service='application')
    utils.backup_dev_packages(config=mls_config())
    utils.run_buildout(config=mls_config())
    utils.supervisorctl(command='start', service='application')


@api.task
@api.roles('worker')
def restart():
    """Restart the application client component."""
    utils.supervisorctl(command='restart', service='application')


@api.task
@api.roles('worker')
def rebuild():
    """Rebuild the application using buildout."""
    utils.run_buildout(config=mls_config())
    utils.supervisorctl(command='restart', service='application')
