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

from fabric.api import put
from fabric.api import sudo
from fabric.api import task

from common import install_packages


OVIRT_RELEASE = 'http://resources.ovirt.org/pub/yum-repo/ovirt-release35.rpm'


@task(name='deploy-engine')
def deploy_engine(proxy=''):
    install_packages([OVIRT_RELEASE], proxy=proxy)
    install_packages(['ovirt-engine'], proxy=proxy)

    put('resources/engine-setup.answers',
        '/tmp/engine-setup.answers', mode=0600)

    sudo('engine-setup '
         '--jboss-home=/usr/share/ovirt-engine-jboss-as '
         '--config=/tmp/engine-setup.answers')


@task(name='deploy-node')
def deploy_node(proxy=''):
    install_packages([OVIRT_RELEASE], proxy=proxy)
    # final deployment is orchestrated by ovirt-engine
