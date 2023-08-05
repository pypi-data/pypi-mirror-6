from __future__ import absolute_import
from __future__ import print_function

import os
import shutil
from insolater.versioncmp import VersionDiff


def init(repo):
    if not os.path.isdir(repo):
        os.mkdir(repo)
        os.mkdir(repo+'/removed')
        os.mkdir(repo+'/versions')
        with open(repo+'/current_version', 'w') as f:
            f.write('original')
        shutil.copytree('.', repo + '/versions/original', ignore=shutil.ignore_patterns(repo))
        with open(repo+'/removed/original', 'w') as f:
            f.write('')


def is_version(repo, version):
    return os.path.isdir(repo+'/versions/'+version)


def all_versions(repo):
    return filter(lambda x: x[0] != '_', os.listdir(repo+'/versions/'))


def current_version(repo):
    with open(repo+'/current_version', 'r') as f:
        return f.readline().strip()


def open_version(repo, version):
    if not is_version(repo, version):
        return
    vp = repo + '/versions/' + version + '/'
    vd = VersionDiff(repo)
    for fp in vd.changed+vd.removed:
        _copy(repo+'/versions/original/'+fp, fp)
    for fp in vd.added_files_recursive():
        os.remove(fp)
    vd = VersionDiff(repo, version)
    for fp in vd.changed:
        _copy(vp+fp, fp)
    for fp in vd.added_files_recursive():
        _copy(vp+fp, fp)
    with open(repo+'/removed/'+version, 'r') as f:
        removed = f.read().split()
    for fp in removed:
        os.remove(fp)
    with open(repo+'/current_version', 'w') as f:
        f.write(version)


def save_version(repo, version=''):
    #TODO: merging changes
    if version == '':
        version = current_version(repo)
    if version == 'original':
        return
    version_path = repo + '/versions/' + version
    if os.path.isdir(version_path):
        shutil.rmtree(version_path)
    os.mkdir(version_path)
    vd = VersionDiff(repo)
    for fp in vd.changed+vd.added_files_recursive():
        _copy(fp, version_path+'/'+fp)
    with open(repo+'/removed/'+version, 'w') as f:
        f.write(reduce(lambda a, b: a+'\n'+b, vd.removed_files_recursive(), '').strip())


def delete_version(repo, version):
    if ((not is_version(repo, version)) or
            version == 'original' or
            current_version(repo) == version):
        return
    shutil.rmtree(repo+'/versions/'+version)
    os.remove(repo+'/removed/'+version)


def _copy(src, dst):
    dst = os.path.normpath(dst)
    src = os.path.normpath(src)
    if dst == '.':
        return
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    p, f = os.path.split(dst)
    p = os.path.normpath(p)
    if not os.path.isdir(p):
        os.makedirs(p)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
