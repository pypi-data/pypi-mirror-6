# -*- coding: utf-8 -*-
import os
import re
import subprocess

from .exceptions import TracError

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
SHELL_SCRIPT = os.path.join(MODULE_DIR, 'scripts', 'tracremote.sh')


def parse_process_error(output):
    errors = []
    messages = output.split(u'\n')
    # TODO: compare locally speed of this version vs:
    # for m in filter(lambda x: x.starts_with(...),...)
    # and than o.split('error=')[1]
    for m in messages:
        e = re.match(r'^error=(?P<error>.+)', m)
        if e:
            errors.append(e.group('error'))
    return errors


class TracRemote(object):
    def __init__(self, ssh_host, ssh_user, tracs_dir, htpasswd_path, chgrp):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.tracs_dir = tracs_dir
        self.htpasswd_path = htpasswd_path
        self.chgrp = chgrp
        self.__base_args = [
            'bash', SHELL_SCRIPT, self.ssh_host, self.ssh_user, self.tracs_dir,
            self.htpasswd_path, self.chgrp
        ]

    @property
    def base_args(self):
        """
        Base arguments to run SHELL_SCRIPT.

        Note: Using property to ensure that these args can't be modified

        """
        return list(self.__base_args)

    def call_command(self, *args):
        full_args = self.base_args
        full_args.extend(args)
        proc = subprocess.Popen(
            full_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        code = proc.poll()
        if code != 0:
            errors = parse_process_error(output)
            raise TracError(code, errors, output)
        return output

    def copy_trac(self, pattern_name, trac_name):
        """
        Create new trac by copying ``pattern_name`` trac directory.

        Retrun ``trac_name`` on success

        """
        self.call_command('copy', pattern_name, trac_name)
        return trac_name

    def add_user_to_trac(self, trac_name, username):
        """
        Add existing user to selected trac with scripts/trac.sh
        Return True on success,
        raise TracError with error code in TracError.code otherwise

        """
        # TODO: check if this command is  still used and does something good
        self.call_command('tracadduser', trac_name, username)
        return True

    def add_trac_user(self, trac_name, username, password=None):
        """
        Add user to ``self.htpasswd_path`` file

        """
        if password:
            output = self.call_command('adduser', trac_name, username, password)
        else:
            output = self.call_command('adduser', trac_name, username)
            password = re.match(r'.*password=(?P<password>\w+) .*', output)
        if not password:
            raise TracError(10, ['Password not created!'])
        return password.group('password')

    def get_trac_users(self):
        """
        Returns usernames list of users registered at ``self.htpasswd_path`` file.
        Users list started from '>>>' and ended by '<<<'

        """
        output = self.call_command('userslist')
        output = output.split()
        users_list = []
        for o in output:
            if o == '>>>':
                users_list = []
                continue
            if o == '<<<':
                break
            users_list.append(o)
        else:
            raise TracError(20)
        return users_list
