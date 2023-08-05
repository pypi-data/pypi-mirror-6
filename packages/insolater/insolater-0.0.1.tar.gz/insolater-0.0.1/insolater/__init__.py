# Copyright (c) 2013 David Karesh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__all__ = [
    'Insolater',
    'cli',
    'init',
    'current_version',
    'all_versions',
    'save_version',
    'delete_version',
    'change_version',
    'pull_version',
    'push_version',
    'exit',
    'version_tools',
    'version_tools_git',
    'version_tools_compressed',
    'versioncmp',
    ]

# Export the global Insolater object methods.
from insolater import Insolater
from run import cli

_INSOLATER = Insolater()

init = _INSOLATER.init
current_version = _INSOLATER.current_version
all_versions = _INSOLATER.all_versions
save_version = _INSOLATER.save_version
delete_version = _INSOLATER.delete_version
change_version = _INSOLATER.change_version
pull_version = _INSOLATER.pull_version
push_version = _INSOLATER.push_version
exit = _INSOLATER.exit
