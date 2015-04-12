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

from manageiq import create_provider

from fabric.api import cd
from fabric.api import put
from fabric.api import run
from fabric.api import settings
from fabric.api import sudo
from fabric.api import task
from fabric.api import env
from fabric.contrib.files import sed

from common import install_packages
from common import enable_services
from common import enable_tcp_ports


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
def start():
    with cd('origin'):
        run('make')
        sudo('nohup ./_output/local/go/bin/openshift start &')

        # add OpenShift as a provider in ManageIQ
        create_provider('openshift01', env.host)
