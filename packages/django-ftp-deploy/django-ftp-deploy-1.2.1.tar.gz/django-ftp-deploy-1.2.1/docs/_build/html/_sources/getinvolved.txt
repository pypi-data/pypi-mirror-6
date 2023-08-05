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
4. Install all requirements for developing module. Go to root directory of unziped files and use pip::
   
     pip install -r requirements/dev.txt

5. Add ``FTP_TEST_SETTINGS`` configuration to your settings
   
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

Application use `Nose <https://nose.readthedocs.org/en/latest/>`_ as test runner and  `Fabric <http://docs.fabfile.org/en/1.8/>`_ library to automate testing process. 

In order to run tests go into *ftp_deploy/tests* directory and then:


* *all* tests::
  
   fab test

* *all* tests with *coverage*::
  
   fab testc

* *Unit Tests* only::

   fab testu

* *Integration Tests* only::

   fab testi


*Unit Tests* and *Integration Tests* accepts **module** attibute to specify module to test::

   fab testu:module_name
