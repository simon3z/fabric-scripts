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
from fabric.context_managers import shell_env


def install_packages(packages, proxy=''):
    with shell_env(http_proxy=proxy, ftp_proxy=proxy):
        sudo('yum -y install {0}'.format(' '.join(packages)), pty=False)


def enable_services(services):
    for x in services:
        sudo('sudo systemctl enable {0}'.format(x))
        sudo('sudo systemctl start {0}'.format(x))

def enable_tcp_ports(ports):
    for x in ports:
        sudo('firewall-cmd --add-port={0}/tcp'.format(x))
        sudo('firewall-cmd --permanent --add-port={0}/tcp'.format(x))
