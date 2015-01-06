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

from fabric.api import sudo
from fabric.api import task

from common import enable_services
from common import install_packages


@task
def deploy(proxy=''):
    install_packages(['kubernetes'], proxy=proxy)
    enable_services(['docker.socket',
                     'etcd.service',
                     'kube-apiserver.service',
                     'kube-controller-manager.service',
                     'kube-proxy.service',
                     'kube-scheduler.service',
                     'kubelet.service'])
