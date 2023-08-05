.. _getinvolved:

Introduction
============

1. Download the newest version `django-ftp-deploy <https://pypi.python.org/pypi/django-ftp-deploy>`_ module 
2. Unzip the file and put **ftp_deploy** folder into your root project directory::
      
    -media/
    -static/
    -projectname/
      -ftp_deploy/
         ...
      -projectname/
         -settings.py
         -urls.py
         ...
      -manage.py


3. Install application as described in :ref:`installation <installation>` section.
4. Install all requirements for developing module. In order to do this, go to root directory of unziped file, and run::
   
     pip install -r requirements/dev.txt

5. Add ``FTP_TEST_SETTINGS`` configuration to your settings (testing purposes only)
   
   .. code-block:: python

       FTP_TEST_SETTINGS =  {
        'host'      : '',
        'username'  : '',
        'password'  : '',
        'path'      : '',
       }


6. Replace ``projectname`` in test configuration file::
   
    # ftp_deploy/tests/conf/conf.py

    from projectname.settings import *

7. Install `PhantomJS <http://phantomjs.org/>`_ for intergration tests
8. **Start Developing!**
   

   
Testing
=======

Application use `Nose <https://nose.readthedocs.org/en/latest/>`_ and  `Fabric <http://docs.fabfile.org/en/1.8/>`_ libraries to automate testing process. 
For tests coverage statistics use `Coverage <https://pypi.python.org/pypi/coverage>`_ library.

In order to run tests go into *ftp_deploy/tests* directory and then run:


* *all* tests::
  
   fab test

* *all* tests with *coverage*::
  
   fab testc

* *Unit Tests* only::

   fab testu

* *Integration Tests* only::

   fab testi

* *Extarnal Tests* only (FTP, Repository etc.)::

   fab teste