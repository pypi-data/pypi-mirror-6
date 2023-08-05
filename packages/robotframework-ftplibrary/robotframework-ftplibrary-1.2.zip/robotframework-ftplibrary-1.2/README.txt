Robot Framework FTP Library

-----------------------------license--------------------------------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

----------------------------------------------------------------------

This library provides functionality of FTP client.

Version 1.2 released on 24th of November 2013.

What's new in release 1.2:
- updated naming for puprpose of pypi.

FTP communication provided by ftplib.py. While developing, following versions were used:
- robotframework-2.8.1
- robotframework-ride-1.2.1
- python-2.7.5

Tested on:
- Windows 7
- Debian 6
- ProFTPD

Author: Marcin Kowalczyk

Website: http://sourceforge.net/projects/rf-ftp-py/

Installation:
- run command: pip install robotframework-ftplibrary
or
- download, unzip and run command: python setup.py install
or
- download, unzip and copy FtpLibrary.py file to a directory pointed by PYTHONPATH (for example ...\Python27\lib\site-packages).

The simplest example (connect, change working dir, print working dir, close):
 | ftp connect | 192.168.1.10 | mylogin | mypassword |
 | cwd | /home/myname/tmp/testdir |
 | pwd |
 | ftp close |