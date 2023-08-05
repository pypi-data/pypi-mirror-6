============
pytracremote
============

Python wrapper over shell script that manages trac copying and .htpasswd
management on remote server that serves mu;tiple trac instances in different
folders.

This module may not have practical use for anyone except 42coffeecups.com but
it may be used as demonstration of shell-script wrapping in python


Requirements
============

1. Software on local host: ssh, apg
2. Software on host with trac: htpasswd

Example usage
=============

.. code-block:: python

	>>> import pytracremote
	>>> t_r = pytracremote.TracRemote(ssh_host="trac.example.com", ssh_user="tracmanager", tracs_dir='/var/lib/trac/projects', htpasswd_path='/var/lib/trac/projects/.htpasswd', chgrp='apache2')
	>>> t_r.get_trac_users()
	['user1', 'user2']
	>>> t_r.copy_trac('42-trac11-template', '42-test-deletemedelete')
	'42-test-deletemedelete'
	>>> # on remote directory '42-trac11-template' will be copied to '42-test-deletemedelete'
	>>> t_r.add_trac_user('42-test-deletemedelete', 'deletemedelete')
    'ays5Quatda'


