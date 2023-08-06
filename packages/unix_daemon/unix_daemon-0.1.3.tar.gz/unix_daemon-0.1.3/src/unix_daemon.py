# -*- coding: utf-8 -*-
'''
daemon module emulating BSD Daemon(3)

Copyright 2013 Yoshida Shin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
import sys
import errno


__all__ = ['daemon']


def daemon(nochdir=False, noclose=False):
    r''' Fork twice and become a daemon.

         If argument `nochdir' is False, this process changes the calling
         process's current working directory to the root directory ("/");
         otherwise, the current working directory is left unchanged.
         The Default of nochdir is False.

         If  argument `noclose' is False,
         this function redirects stdin, stdout and stderr to /dev/null;
         otherwise, leaves them.
         The defult value of noclose is False.

         daemon returns the pid of new process.
    '''

    ## 1st fork
    pid = os.fork()
    if pid != 0:
        os.waitpid(pid, os.P_WAIT)
        os._exit(0)

    ## 2nd fork
    os.setsid()
    if os.fork() != 0:
        os._exit(0)

    ## daemon process
    # ch '/'
    if not nochdir:
        os.chdir('/')

    if not noclose:
        # Close stdin, stdout and stderr
        for f in (sys.stdin, sys.stdout, sys.stderr):
            if f.closed:
                # Skip if the file is already closed.
                continue

            fd = f.fileno()
            f.close()
            try:
                # Make sure to close the file descriptor.
                os.close(fd)
            except OSError as e:
                if e.errno == errno.EBADF:
                    # Do nothing if the descriptor has already closed.
                    pass
                else:
                    raise

        # Redirect stdin to /dev/null
        stdin = os.open(os.devnull, os.O_RDONLY)
        sys.stdin = os.fdopen(stdin, 'r')

        # Redirect stdout to /dev/null
        stdout = os.open(os.devnull, os.O_WRONLY|os.O_APPEND)
        sys.stdout = os.fdopen(stdout, 'a')

        # Redirect stderr to /dev/null
        stderr = os.dup(sys.stdout.fileno())
        sys.stderr = os.fdopen(stderr, 'a')

    return os.getpid()
