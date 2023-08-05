===================
SSH Deploy Key
===================

Overview
========

SSH Deploy key is a high-performance tool to distribute
your ssh public key to one or more remote servers.  It 
accepts lists of remote hosts from redirected standard in, 
or the remote hosts can be entered interactively.

Documentation
=============
Documentation and example usage can be found at

http://ssh-copy-id.readthedocs.org/


Installation
============
SSH deploy key is installed from the command line.  

ssh-deploy-key is normally installed via pip.  However, on some systems,
there are source files that must be installed first.

Prerequisites
-------------

ssh-deploy-key depends on the excellent Paramiko ssh library, which
requires the Python sources.  You can install these
using the normal package managers for your OS.

**Debian/Ubuntu (apt-get)**

::

    sudo apt-get install python-dev


**Red Hat/Centos (yum)**

::

    sudo yum install python-devel

**OS X**


You will need a compiler installed -- either XCode or gcc.  Normally, you can
just run the command to install ssh-deploy-key (see below), and if no compiler
is available on your system, you will be prompted to install one:

.. image:: http://ssh-copy-id.readthedocs.org/en/latest/_images/install_gcc_mac.png

If this happens, click the 'install' button, then run the pip
command again.


Install ssh-deploy-key via Pip
------------------------------

Once the development libraries are in place, the best way to
install ssh-deploy-key is via pip.  To get pip, see
http://www.pip-installer.org/en/latest/installing.html

Then,
::

    sudo pip install ssh-deploy-key




Source
======
The SSH deploy key sources are hosted on bitbucket.

https://bitbucket.org/travis_bear/ssh_deploy_key
