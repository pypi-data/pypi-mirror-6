# -*- coding: utf-8 -*-
"""Manage chef roles."""

from chef import autoconfigure, Role
from fabric import api
from fabric.colors import green
from propertyshelf.fabfile.common import roles


@api.task
def check():
    """Check if the required roles are available."""
    roles.check_required()


@api.task
def create_missing():
    """Create missing roles on the chef server."""
    chef_api = autoconfigure()
    required = roles.get_required()
    domain = api.env.get('domain', 'example.com')

    # Create the role_database.
    if not roles.check(required.get('role_database')):
        name = required.get('role_database')
        description = 'ZEO Server for %s.' % domain
        run_list = (
            "role[mls_zeoserver]",
        )
        default_attributes = {
            'domain': domain,
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)

    # Create the role_frontend.
    if not roles.check(required.get('role_frontend')):
        name = required.get('role_frontend')
        description = 'Frontend Server for %s.' % domain
        run_list = (
            "role[mls_loadbalancer]",
        )
        default_attributes = {
            'domain': domain,
            'haproxy': {
                'app_server_role': required.get('role_worker'),
            },
            'mls': {
                'domain': '.'.join(['mls', domain]),
            },
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)

    # Create the role_worker.
    if not roles.check(required.get('role_worker')):
        name = required.get('role_worker')
        description = 'Application Worker for %s.' % domain
        run_list = (
            "role[mls_application]",
        )
        policy_on = api.env.get('mls_policy_enabled') and 'true' or 'false'
        default_attributes = {
            'domain': domain,
            'mls': {
                'customizations': api.env.get('mls_customizations', []),
                'policy': {
                    'enabled': policy_on,
                    'package': api.env.get('mls_policy_package', ''),
                    'package_url': api.env.get('mls_policy_package_url', ''),
                },
                'zeo_role': required.get('role_database'),
            },
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)

    # Create the role_staging.
    if not roles.check(required.get('role_staging')):
        name = required.get('role_staging')
        description = 'Staging system for %s.' % domain
        run_list = (
            "role[%s]" % required.get('role_database'),
            "role[%s]" % required.get('role_worker'),
            "role[%s]" % required.get('role_frontend'),
        )
        default_attributes = {
            'domain': domain,
            'haproxy': {
                'app_server_role': name,
            },
            'mls': {
                'domain': '.'.join(['staging', domain]),
                'zeo_role': name,
            },
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)


@api.task
def list_nodes(role_list=None):
    """List all available nodes with given roles."""
    roles.list_nodes()
