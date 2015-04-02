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
        'gcc',
        'gcc-c++',
        'git',
        'graphviz-devel'
        'libxml2-devel',
        'libxslt',
        'libxslt-devel',
        'memcached',
        'postgresql-devel',
        'postgresql-server',
        'ruby-devel',
        'vim',
    ])


@task
def deploy():
    install_deps()

    sudo('test -e /var/lib/pgsql/data/pg_hba.conf || postgresql-setup initdb')
    enable_services(['memcached', 'postgresql'])

    with settings(warn_only=True, sudo_user='postgres'):
        sudo('createuser {0}'.format(env.user))
        sudo('createdb --owner={0} vmdb_development'.format(env.user))

    run('type bundle 2>/dev/null || gem install bundler -v "~>1.3"')
    run('test -d manageiq || git clone https://github.com/ManageIQ/manageiq')

    with cd('manageiq/vmdb'):
        run('bundle install --without qpid')

    with cd('manageiq'):
        run('vmdb/bin/rake build:shared_objects')

    with cd('manageiq/vmdb'):
        run('bundle install --without qpid')
        run('cp config/database.pg.yml config/database.yml')
        sed('config/database.yml',
            'username: root', 'username: {0}'.format(env.user))
        run('bin/rake db:migrate')

    enable_tcp_ports([3000])


@task
def start_rails():
    with cd('manageiq/vmdb'):
        run('bin/rails server')


@task
def start():
    with cd('manageiq/vmdb'):
        run('bundle exec rake evm:start')


@task
def stop():
    with cd('manageiq/vmdb'):
        run('bundle exec rake evm:kill')
