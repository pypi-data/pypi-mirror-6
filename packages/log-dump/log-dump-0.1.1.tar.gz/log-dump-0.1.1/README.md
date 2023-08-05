log-dump
--------

The Windows security log dumper.

Introduction
------------

Log-Dump is a Python script to dump and generate all Windows Logon Errors, primary the 4625 and 4771 events on Windows 2008 / 2012 Servers and 529 on Windows 2003 Servers.
With this tool, system admins can generate a CSV list with all information contained in the Windows Security Log about the erros, wich became easily to treat.

Installation
------------

1. Install Log-dump.

You can install the log-dump through pip:

`pip install log-dump`

As well, the sdist package can be downloaded at:

https://pypi.python.org/pypi/log-dump/

How to Use
----------

Once Instaled, you just need run it with Elevated Privileges and provide a range of date, as noted in the following example(Considering that the scripts dir of the python instalation is part of the PATH):

`C:\>log_dump.py -sd "30/01/13 20:00" -ed "31/01/13 20:00"`

A file named 'logon_failure.log' will be created at the current dir with all logon errors in the CSV format.

License
-------

Licensed under the Apache License, Version 2.0, that can be viewed at:
  http://www.apache.org/licenses/LICENSE-2.0

Credits
-------
* [Gabriel Abdalla Cavalcante](https://github.com/gcavalcante8808)
