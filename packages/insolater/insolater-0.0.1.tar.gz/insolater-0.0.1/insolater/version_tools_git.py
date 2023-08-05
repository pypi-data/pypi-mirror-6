from __future__ import absolute_import
from __future__ import print_function

import os
import subprocess


def init(repo):
    _run_git(repo, "--work-tree=. init")
    with open(repo+'/info/exclude', 'a') as f:
        f.write('\n'+repo)
    _run_git(repo, "add -A .")
    _run_git(repo, "commit -am 'Original files'")
    _run_git(repo, "branch original")
    _run_git(repo, "checkout -b _current_version")
    _run_git(repo, "branch -D master")
    with open(repo+'/current_version', 'w') as f:
        f.write('original')


def is_version(repo, version):
    return os.path.isfile(repo+'/refs/heads/'+version)


def all_versions(repo):
    return filter(lambda x: x[0] != '_', os.listdir(repo+'/refs/heads/'))


def current_version(repo):
    with open(repo+'/current_version', 'r') as f:
        return f.readline().strip()


def open_version(repo, version):
    if not is_version(repo, version):
        return
    _run_git(repo, "add -A .")
    _run_git(repo, "commit -am 'clear staging'")
    _run_git(repo, "branch "+version)
    _run_git(repo, "checkout "+version)
    _run_git(repo, "reset --hard")
    _run_git(repo, "branch -D _current_version")
    _run_git(repo, "checkout -b _current_version")
    with open(repo+'/current_version', 'w') as f:
        f.write(version)


def save_version(repo, version=''):
    if version == '':
        version = current_version(repo)
    if version == 'original':
        return
    _run_git(repo, "add -A .")
    _run_git(repo, "commit -am 'update'")
    _run_git(repo, "branch -D "+version)
    _run_git(repo, "branch -m _current_version "+version)
    _run_git(repo, "checkout -b _current_version")


def delete_version(repo, version):
    if ((not is_version(repo, version)) or
            version == 'original' or
            current_version(repo) == version):
        return
    _run_git(repo, "branch -D "+version)


def diff_version(repo, v1, v2):
    changes = _run_git(repo, "diff --name-only {0} {1}".format(v1, v2))[1]
    changes = changes.strip().split('\n')
    return changes


def _run(command):
    """Replace instances of {repo} with repo and run the command."""
    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    exit_code = proc.poll()
    return exit_code, out, err


def _run_git(repo, command):
    """Runs git --git-dir={repo} command."""
    return _run("git --git-dir=" + repo + " " + command)


def _run_git_add(repo, filepatterns=[]):
    """Runs git --git-dir={repo} add -A for each filepattern."""
    sh = ""
    for fp in filepatterns:
        sh += "git --git-dir={repo} add -A " + fp + ";".format(fp)
    return _run(sh)
