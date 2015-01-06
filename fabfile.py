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

import os

import virtdeploy

from fabric.api import cd
from fabric.api import env
from fabric.api import run
from fabric.api import settings
from fabric.api import task
from fabric.contrib.files import append

from projects import kube
from projects import manageiq
from projects import openshift
from projects import ovirt


@task(name='vm-hosts')
def vm_hosts(*hosts):
    """
    specify the instance names instead of hosts
    """
    driver = virtdeploy.get_driver('libvirt')
    env.hosts.extend((driver.instance_address(x)[0] for x in hosts))


def _read_key_file(key_file='~/.ssh/id_rsa.pub'):
    with open(os.path.expanduser(key_file)) as f:
        return f.read()


@task(name='init-host')
def host_init():
    """
    configure the access to the host
    """
    user = env.user

    with settings(user='root', no_keys=True):
        run('getent passwd {0} > /dev/null || useradd {0}'.format(user))

        with cd('~{0}'.format(user)):
            run('mkdir -p -m 700 .ssh')
            append('.ssh/authorized_keys', _read_key_file())
            run('chown -R {0}:{0} .ssh'.format(user))

        append('/etc/sudoers', '{0} ALL=(ALL) NOPASSWD: ALL'.format(user))
        append('/etc/sudoers', 'Defaults:{0} !requiretty'.format(user))
