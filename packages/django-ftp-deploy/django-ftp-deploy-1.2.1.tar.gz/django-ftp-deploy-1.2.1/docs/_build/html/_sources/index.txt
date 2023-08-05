.. Django FTP Deploy documentation master file, created by
   sphinx-quickstart on Mon Oct  7 18:49:46 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django FTP Deploy Documentation
============================================

django-ftp-deploy allows you to automatically deploy GIT repositories to FTP servers. You don't need to install git on the server!


**Features:**

* Login Screen
* Services Dashboard (a service is one repository-to-ftp configuration)
* Manage Multiple Services
* Verification Services Configurations
* Repository Hook Management
* Dynamic Loading of Repository list
* Restore Failed Deploys
* Email Notifications per service
* Statistics of Deployments
* Deployment Logs


Supported GIT repositories:

* Bitbucket
* Github (planned)
  


Current tests coverage status:

.. image:: ../ftp_deploy/tests/coverage/coverage_status.png


User Guide
----------


.. toctree::
   :maxdepth: 3

   installation 
   usage
   other
   changelog


Get Involved!
-------------

Get involved and help make this application better!

.. toctree::
   :maxdepth: 3  
    
   getinvolved



Roadmap
-------  

*v2.0*

* Github support
* Queuing deploys (along with deploying progressbar)
* Cron validation
* FTP password encryption
* Advanced statistics

  

Knowing issues
--------------

Queuing deploys is not supported. If deploy is run before last deploy has been finished, it's captured with failed status. You need to go and manually restore deploy then, to make your repository and FTP data consisent. 

Issue will be fixed by queuing deploys using `Celery <http://docs.celeryproject.org/en/latest/index.html>`_ 



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

