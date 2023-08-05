from __future__ import absolute_import
from __future__ import print_function

import os
import shutil
import subprocess
import getpass
import pexpect
from insolater import version_tools as vt


class Insolater(object):
    _CMD = "inso"
    _NOT_INIT_MESSAGE = "No session found. See '{cmd} init <remote changes>'".format(cmd=_CMD)
    _ALREADY_INIT_MESSAGE = (
        "Already initialized. To end session use: {cmd} exit [<remote backup>]".format(cmd=_CMD))

    def __init__(self, repo=".insolater_repo", timeout=5, filepattern="."):
        self.repo = os.path.normpath(repo)
        self.timeout = timeout
        self.filepattern = filepattern.split()
        #TODO: _get_repo_path()
        #: make an .inso_include file
        #:: inso pattern [--add|set|clear|all]      none
        #: keep track of current version
        #:: don't allow edits to ORIG
        #::: either Update ORIG, Discard, Move to CHANGES, or Send to remote
        #TODO: apply (merge changes into ORIG)

    def init(self, remote_changes=None):
        """Create repo and store original files.  Optionally retrieve version remotely."""
        self._verify_repo_exists(False)
        vt.init(self.repo)
        if remote_changes:
            self.pull_version(remote_changes)
        return "Initialized repository with versions: original"

    def current_version(self):
        """Returns the current version."""
        self._verify_repo_exists(True)
        return vt.current_version(self.repo)

    def all_versions(self):
        self._verify_repo_exists(True)
        return vt.all_versions(self.repo)

    def change_version(self, version):
        """Save changes and switch to the specified version."""
        self._verify_repo_exists(True)
        #TODO: save changes? when in original
        if vt.current_version(self.repo) == 'original':
            vt.save_version(self.repo, '_original_edit')
        else:
            vt.save_version(self.repo)
        vt.open_version(self.repo, version)
        if vt.current_version(self.repo) == version:
            return "Switched to %s" % version
        else:
            return "Version not found: %s" % version

    def save_version(self, version='', overwrite=None):
        """Save/create and open a version with the specified name.
        Fails if version name starts with '_'.
        Prompts if version already exists unless overwrite is set."""
        self._verify_repo_exists(True)
        #TODO: better version name checking
        cv = vt.current_version(self.repo)
        version = version or cv
        if version[0] == '_':
            return "Invalid version name: %s" % version
        if not vt.is_version(self.repo, version):
            vt.save_version(self.repo, version)
            vt.open_version(self.repo, version)
            return "Version %s created and opened" % version
        if overwrite is None:
            discard = raw_input("Do you want to overwrite changes (y/[n]): ")
            overwrite = discard.lower() != 'y'
        if overwrite:
            vt.save_version(self.repo, version)
            vt.open_version(self.repo, version)
            return "Version %s saved and opened" % version
        return "Aborted to avoid overwriting."

    def delete_version(self, version):
        """Delete the specified version.
        Fail if the version does not exists, version is 'original' or it is the current version."""
        self._verify_repo_exists(True)
        if not vt.is_version(self.repo, version):
            return "Version not found: %s" % version
        if vt.current_version(self.repo) == version:
            return "Cannot delete current version: %s" % version
        if version == 'original':
            return "Cannot delete original version"
        vt.delete_version(self.repo, version)
        return "Version %s deleted" % version

    def pull_version(self, remote_changes, version=''):
        """Pull remote changes into specified version.
        If no version is specified pull into current version."""
        self._verify_repo_exists(True)
        cv = vt.current_version(self.repo)
        if version:
            self.save_version(version)
            self.change_version(version)
        for f in os.listdir('.'):
            if f != self.repo:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
        retv = self._run("rsync -Pravdtze ssh {0}/* .".format(os.path.normpath(remote_changes)))[0]
        if version != '' and version != cv:
            self.change_version(cv)
        if (retv != 0):
            raise Exception("Failed to sync changes")
        return "Pulled updates"

    def push_version(self, remote_location, version=''):
        """Push specified version to remote location.
        If no version is specified push the current version."""
        self._verify_repo_exists(True)
        cv = vt.current_version(self.repo)
        if version and version != cv:
            if not vt.is_version(self.repo, version):
                return "Version not found: %s" % version
            self.change_version(version)
        pswd = getpass.getpass(remote_location.split(':')[0] + "'s password:")
        transfer_str = ""
        for f in os.listdir('.'):
            if f == self.repo:
                continue
            rsync = "rsync -R -Pravdtze ssh " + f + " " + remote_location
            exitstatus = 0
            try:
                exitstatus = self._run_with_password(rsync, pswd, self.timeout)[0]
            except pexpect.TIMEOUT:
                raise Exception("Aborted (File transfer timeouted out)")
            finally:
                self.change_version(cv)
            if exitstatus != 0:
                transfer_str += f + " \t\tFailed to transfer\n"
                raise Exception(transfer_str + "Aborted (File transfer failed).")
            transfer_str += f + " \t\ttransfered\n"
        return transfer_str

    def exit(self, version='original', discard_changes=None):
        """Open original or specified version files, and delete all other versions
        (delete repo)."""
        self._verify_repo_exists(True)
        if not vt.is_version(self.repo, version):
            return "Version not found: %s" % version
        if discard_changes is None:
            discard = raw_input("Do you want to discard all changes (y/[n]): ")
            discard_changes = discard.lower() == 'y'
        if not discard_changes:
            return "Aborted to avoid discarding changes."
        vt.open_version(self.repo, version)
        shutil.rmtree(self.repo)
        return "Session Ended"

    def _verify_repo_exists(self, exists):
        """(may change pythons current directory).
        raise an exception if the repo does not have the specfied state of being."""
        if exists:
            if not os.path.exists(self.repo):
                if os.getcwd() == '/':
                    raise Exception(Insolater._NOT_INIT_MESSAGE)
                else:
                    os.chdir('..')
                    self._verify_repo_exists(exists)
        else:
            if os.path.exists(self.repo):
                raise Exception(Insolater._ALREADY_INIT_MESSAGE)

    def _run(self, command):
        """Replace instances of {repo} with self.repo and run the command."""
        command = command.format(repo=self.repo)
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        exit_code = proc.poll()
        return exit_code, out, err

    def _run_git(self, command):
        """Runs git --git-dir={repo} command."""
        return self._run("git --git-dir={repo} " + command)

    def _run_git_add(self):
        """Runs git --git-dir={repo} add -A for each filepattern."""
        sh = ""
        for fp in self.filepattern:
            sh += "git --git-dir={repo} add -A " + fp + ";".format(fp)
        return self._run(sh)

    def _run_with_password(self, command, pswd, timeout=5):
        """Replace instances of {repo} with self.repo and run the command using the password."""
        proc = pexpect.spawn(command.format(repo=self.repo))
        proc.expect('password:')
        proc.sendline(pswd)
        proc.expect(pexpect.EOF, timeout=timeout)
        return proc.isalive(), proc.read(), ''
