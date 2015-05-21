#
# Copyright 2015 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

import sys
import time

from fabric.api import cd
from fabric.api import env
from fabric.api import run
from fabric.api import settings
from fabric.api import sudo
from fabric.api import task

from common import enable_services
from common import enable_tcp_ports
from common import install_packages
from manageiq import create_provider
from manageiq import refresh_provider


DEFAULT_ATTEMPTS = 10
OPENSHIFT = './_output/local/go/bin/openshift'
MASTER_YAML_FILE = 'openshift.local.config/master-config.yaml'
ADMIN_KUBECONFIG_FILE = 'openshift.local.config/admin.kubeconfig'
PROVIDER_NAME = 'openshift01'

@task(name='install-deps')
def install_deps():
    install_packages([
        'docker',
        'docker-registry',
        'git',
        'golang',
        'screen',
        'vim',
    ])
    # required on CentOS7
    sudo('yum -y update device-mapper')


@task
def deploy():
    install_deps()

    enable_services(['docker.service'])
    enable_tcp_ports([8443, 8444])

    sudo('usermod -aG root {0}'.format(env.user))

    run('test -d origin || git clone https://github.com/openshift/origin.git')


@task
def build():
    with cd('origin'):
        run('make clean build')


@task
def start():
    build()

    with cd('origin'):
        run('test -e {0} || {1} start master '
            '--write-config=openshift.local.config'.
            format(MASTER_YAML_FILE, OPENSHIFT))

        run('mkdir -p ~/.config/openshift/')
        run('cp {0} ~/.config/openshift/config'.format(ADMIN_KUBECONFIG_FILE))

        # used the sleep workaround due to fabric issue #395
        sudo('nohup {0} start master --config={1} & sleep 5; exit 0'.
             format(OPENSHIFT, MASTER_YAML_FILE))

        with settings(warn_only=True):
            attempts = 0
            while attempts < DEFAULT_ATTEMPTS:
                if run('{0} cli get nodes'.format(OPENSHIFT)):
                    break
                else:
                    attempts += 1
                    time.sleep(5)

        if attempts == DEFAULT_ATTEMPTS:
            sys.exit('failed to start OpenShift after {0} attempts'.format(
                attempts))

    with cd('origin'):
        # workaround for ManageIQ authentication
        run('{0} admin policy add-role-to-group cluster-admin '
            'system:authenticated system:unauthenticated '
            '--namespace=master'.format(OPENSHIFT))


@task(name='create-example-app')
def create_example_app():
    """creates an example app: "hello-openshift"""
    with cd('origin'):
        run('{0} cli create -f '
            'examples/hello-openshift/hello-pod.json'.format(OPENSHIFT))


@task(name='create-provider')
def create_openshit_provider():
    """add OpenShift as a provider in ManageIQ"""
    provider_id = create_provider(PROVIDER_NAME, env.host)
    refresh_provider(provider_id, env.host)
