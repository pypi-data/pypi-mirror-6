__author__ = 'travis'

"""
Parse command-line args to generate config
object.
"""

# Copyright (C) 2014, Travis Bear
# All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import sys
import pwd
import os
try:
    import argparse
except ImportError:
    print ("FATAL: unsupported version of python.  Need 2.7 or higher")
    sys.exit()

COL_USERNAME = 0
COL_HOME_DIR = 5
DEFAULT_PUBLIC_KEY_FILE = "%s%s.ssh%sid_rsa.pub" %(pwd.getpwuid(os.geteuid())[COL_HOME_DIR], os.sep, os.sep)
DEFAULT_REMOTE_AUTHORIZED_KEYS_FILE = "authorized_keys"
DEFAULT_REMOTE_SSH_DIR = "~/.ssh"
DEFAULT_SSH_PORT = 22
DEFAULT_TIMEOUT_SECONDS=3
DEFAULT_THREADCOUNT = 100
DEFAULT_USERNAME = pwd.getpwuid(os.geteuid())[COL_USERNAME]


parser = argparse.ArgumentParser(description='Distribute an ssh key to remote hosts.')
parser.add_argument('-a', '--authorized_keys',
                    default = DEFAULT_REMOTE_AUTHORIZED_KEYS_FILE,
                    help='Name of the remote authorized keys file.  (Changing \
                          this setting is uncommon.)')
parser.add_argument('-d', '--append',
                    action='store_true',
                    default = False,
                    help='Add the ssh key to the end of the remote authorized \
                          keys file instead of overwriting it.  If the ssh key \
                          already exists in the remote authorized keys file, \
                          no action is taken.')
parser.add_argument('-k', '--key_file',
                    default = DEFAULT_PUBLIC_KEY_FILE,
                    help='Path to the local public ssh key file.  Default is \
                          %s' % DEFAULT_PUBLIC_KEY_FILE)
parser.add_argument('-m', '--timeout_seconds',
                    default=DEFAULT_TIMEOUT_SECONDS,
                    type=int,
                    help='Timeout value (in seconds) for connecting to each \
                          remote host.  Default is %s' % DEFAULT_TIMEOUT_SECONDS)
parser.add_argument('-o', '--port',
                    default=22,
                    type=int,
                    help='The ssh port to connect to the remote hosts on. \
                          Default is %s' % DEFAULT_SSH_PORT)
parser.add_argument('-p', '--password',
                    default=None,
                    help='Password to use on remote hosts.  If not specified \
                    here, you will be prompted for this interactively.')
parser.add_argument('-s', '--ssh_dir',
                    default=DEFAULT_REMOTE_SSH_DIR,
                    help='Directory to copy the key into on the remote \
                          host.  Default is %s.  (Changing this setting is\
                          uncommon.)' % DEFAULT_REMOTE_SSH_DIR)
parser.add_argument('-t', '--threads',
                    default = DEFAULT_THREADCOUNT,
                    type=int,
                    help='Number of threads to use for simultaneous key \
                          distribution.  Default is %d.' % DEFAULT_THREADCOUNT)
parser.add_argument('-u', '--username',
                    default=DEFAULT_USERNAME,
                    help="Username to use on remote hosts.  Default is \
                          %s" % DEFAULT_USERNAME)
parser.add_argument('hosts',
                    nargs='*',
                    help='Zero or more remote hosts to receive the ssh key.  If\
                          this value is unspecified, remote hosts will be read\
                          from standard in.  Hosts may be specified in either a\
                          simple form (myhost.example.com) or with a username\
                          (myuser@myhost.example.com')

config = parser.parse_args()
