===================================
os-diskconfig-python-novaclient-ext
===================================


Disk Config extension for python-novaclient.


Install
=======

::

  pip install os_diskconfig_python_novaclient_ext


Usage
=====

This extension will automatically be detected by novaclient and will provide
the --disk-config option for `boot`, `zone-boot`, `rebuild`, and `resize`
commands.


Note
====

This is the *client* extension, for disk-config to work, the Nova service must
also be using the *server-side* extension as well.
