#
# Copyright 2012 Red Hat, Inc.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

"""
Python's implementation of Popen forks back to python before execing.
Forking a python proc is a very complex and volatile process.

This is a simpler method of execing that doesn't go back to python after
forking. This allows for faster safer exec.
"""

import os
import sys
from subprocess import Popen, PIPE

from cpopen import createProcess


class CPopen(Popen):
    def __init__(self, args, close_fds=False, cwd=None, env=None,
                 deathSignal=0, childUmask=None):
        if not isinstance(args, list):
            args = list(args)

        if env is not None and not isinstance(env, list):
            env = list(("=".join(item) for item in env.iteritems()))

        self._childUmask = childUmask
        self._deathSignal = int(deathSignal)
        Popen.__init__(self, args,
                       close_fds=close_fds, cwd=cwd, env=env,
                       stdin=PIPE, stdout=PIPE,
                       stderr=PIPE)

    def _execute_child_v276(self, args, executable, preexec_fn, close_fds,
                       cwd, env, universal_newlines,
                       startupinfo, creationflags, shell, to_close,
                       p2cread, p2cwrite,
                       c2pread, c2pwrite,
                       errread, errwrite):

        return self._execute_child_v275(args, executable, preexec_fn,
            close_fds, cwd, env, universal_newlines,
            startupinfo, creationflags, shell,
            p2cread, p2cwrite,
            c2pread, c2pwrite,
            errread, errwrite)

    def _execute_child_v275(self, args, executable, preexec_fn, close_fds,
                       cwd, env, universal_newlines,
                       startupinfo, creationflags, shell,
                       p2cread, p2cwrite,
                       c2pread, c2pwrite,
                       errread, errwrite):

        try:
            pid, stdin, stdout, stderr = createProcess(args, close_fds,
                                                       p2cread, p2cwrite,
                                                       c2pread, c2pwrite,
                                                       errread, errwrite,
                                                       cwd, env,
                                                       self._deathSignal,
                                                       self._childUmask)

            self.pid = pid
            self._closed = False
            self._returncode = None
        except:
            os.close(p2cwrite)
            os.close(errread)
            os.close(c2pread)
            raise
        finally:
            os.close(p2cread)
            os.close(errwrite)
            os.close(c2pwrite)

    if sys.version_info[0:3] >= (2, 7, 6):
        _execute_child = _execute_child_v276
    else:
        _execute_child = _execute_child_v275
