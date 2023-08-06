__author__ = 'travis'

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

from colorama import Fore

# TODO: put in some knowledge of which types of errors we should
#       retry on.

AUTH_FAILURE = "AUTHENTICATION FAILURE"
APPENDED = "APPENDED"
CONNECTION_FAILURE = "CONNECTION FAILURE"
GENERAL_FAILURE = "GENERAL FAILURE"
IO_FAILURE = "LOCAL IO FAILURE"
NO_ACTION = "NO ACTION"
SCRIPT_FAILURE = "SCRIPT FAILURE"
SSH_FAILURE = "SSH FAILURE"
SUCCESS = "SUCCESS"
UNKNOWN_ERROR = "UNKNOWN ERROR"

colors = {
    APPENDED: Fore.GREEN,
    AUTH_FAILURE: Fore.RED,
    CONNECTION_FAILURE: Fore.RED,
    GENERAL_FAILURE: Fore.RED,
    IO_FAILURE: Fore.RED,
    NO_ACTION: Fore.YELLOW,
    SCRIPT_FAILURE: Fore.RED,
    SSH_FAILURE: Fore.RED,
    SUCCESS: Fore.GREEN,
    UNKNOWN_ERROR: Fore.RED
}
