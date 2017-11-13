# -*- coding: utf-8 -*-
from fabric.api import *

env.hosts = ['112.74.188.127']
env.user = 'root'
env.password = 'Aa123456'


def pack():
    tar_files = ['requirements.txt', '*.py', 'backtradercn/*']
    local('rm -f backtradercn.tar.gz')
    local('tar -czvf backtradercn.tar.gz --exclude=\'*.tar.gz\' --exclude=\'fabfile.py\' %s' % ' '.join(tar_files))


def deploy():
    remote_tmp_tar = '/root/data/backtradercn.tar.gz'

    with cd('/root/data/'):
        run('rm -fr *')
        put('backtradercn.tar.gz', remote_tmp_tar)
        run('tar -xzvf %s' % remote_tmp_tar)
        run('grep -Ev \'^#\' requirements.txt | awk -F\'# \' \'{print $1}\' | xargs -n 1 -L 1 pip install')



