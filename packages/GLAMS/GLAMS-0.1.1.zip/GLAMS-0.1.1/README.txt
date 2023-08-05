﻿GLAMS
=====

:Title:    
    GLAMS (Gandhi Lab Animal Management System)

:Author:       
    Kyle Ellefsen

:Date:
    2013.9.7

:Description:  
    This program creates a MySQL database containing mouse colony information. It also contains a web server which, when launched, allows users to retrieve and update information on the database. 


INSTALLATION FOR WINDOWS
========================

#. Install MySQL (for `windows <http://dev.mysql.com/downloads/windows/installer/>`_.)

   - Choose ``Sever Machine`` when prompted for 'server configuration type'.
   - Choose ``Enable TCP/IP Networking`` if you would like to access GLAMS from other computers.
   - Leave the port number as the default ``3306``. 
   - Keep ``Open firewall port for network access`` checked.
   - Use your lab password as the ``MySQL Root Password``.
   - Add a user.  
   - Set 'host' to be ``<All Hosts (%)>``. 
   - Set 'Role' as ``DB Admin``.  
   - Leave authentication as ``MySQL``.  This user account will be in GLAMS to communicate with MySQL, and it will be saved as plaintext, so make sure it is a password you don't use for anything else. Remember it for a later step.
   - Run Windows Service as a Standard System Account. This automatically starts MySQL on Windows startup.
   - After the install, create a new database (aka schema) called ``glams``. (instructions at http://stackoverflow.com/questions/5515745/create-a-new-database-with-mysql-workbench)

#. Install the latest version of Python 2 (`2.7.6 <http://www.python.org/getit/releases/2.7.6/>`_. as of 2013.12.17) 
#. Install pip (instructions at `pip-installer.org <http://www.pip-installer.org/en/latest/installing.html>`_.)
#. Install `lxml <http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml>`_.

   - Download lxml-3.2.4.win32-py2.7.exe and install.

#. Install GLAMS. In a command line, change directory to where pip.py is installed.  In Windows this is usually 'C:/Python27/Scripts/'. Then type::

    pip install glams


#. In a command line, change directory to where glams is installed (in windows: ``C:\Python27\Lib\site-packages\glams\``). Run the script::

    setup_glams.py 


   (you can also double click on the icon) and answer the questions when prompted.  This script will create a config.txt file which will save your password as plaintext, so don't use the lab password.  The script will also reset the database.

#. Launch the GLAMS server by running::

    main.py


   in the glams directory.  Open a browser, and navigate to ``localhost``.  GLAMS has been installed.

TODO
=====

- Save the column order when a user moves a column.
- Add column for filtering 'projected age at date'.
- Be able to select cage in 'history'.
- Do sorting in the backend, not in javascript.


BUGS
====
- If viewing on the chrome web browser which has the google docs app installed, you can't view mouse or cage information.  This might be a chrome bug.
- When switching to cage view if no columns are selected there is an error.