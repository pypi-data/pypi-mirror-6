from __future__ import absolute_import
from __future__ import print_function

import os
import filecmp


def files_recursive(files_and_dirs, path_to='', path=''):
    files = []
    next_cur = []
    for f in files_and_dirs:
        if os.path.isfile(path_to+path+f):
            files.append(path+f)
        else:
            next_cur.append(f)
    for d in next_cur:
        files += files_recursive(os.listdir(path_to+path+d), path_to, path+d+'/')
    return files


def _dircmp_files(d, path=''):
    left = [path+f for f in d.left_only]
    changes = [path+f for f in d.diff_files]
    right = [path+f for f in d.right_only]
    for sd in d.subdirs:
        l, c, r = _dircmp_files(d.subdirs[sd], path+sd+'/')
        left += l
        changes += c
        right += r
    return left, changes, right


class VersionDiff(object):
    def __init__(self, repo, v1='', v2=''):
        self.repo = repo
        if v1 == '' or v2 == '':
            v2 = v1 or v2
            v2 = '.' if v2 == '' else (repo + '/versions/' + v2)
            v1 = repo + '/versions/original'
        else:
            v1, v2 = repo + '/versions/' + v1, repo + '/versions/' + v2
        self.v1, self.v2 = v1+'/', v2+'/'
        d = filecmp.dircmp(v1, v2, ignore=[repo])
        self.removed, self.changed, self.added = _dircmp_files(d)

    def added_files_recursive(self):
        try:
            self._added_files
        except:
            self._added_files = files_recursive(self.added, self.v2)
        return self._added_files

    def removed_files_recursive(self):
        try:
            self._removed_files
        except:
            self._removed_files = files_recursive(self.removed, self.v1)
        return self._removed_files
