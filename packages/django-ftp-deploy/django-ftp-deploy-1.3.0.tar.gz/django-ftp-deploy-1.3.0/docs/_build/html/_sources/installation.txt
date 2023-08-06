.. _installation:

Installation
============

Installation and requirements for django-ftp-deploy module


Requirements
------------   

Required third party libraries are **installed automatically** if you use pip to install django-ftp-deploy.

1.  Django >= 1.5
2. `pycurl <https://pypi.python.org/pypi/pycurl>`_
3. `certifi <https://pypi.python.org/pypi/certifi>`_
4. `django_braces <https://pypi.python.org/pypi/django-braces>`_
5. `django_crispy_forms <https://pypi.python.org/pypi/django-crispy-forms>`_
6. `Celery <http://www.celeryproject.org/>`_




Installation
------------

.. note:: FTP Deploy Server is optional and doesn't need to be installed for basic usage. It is however, highly recommended that you install FTP Deploy Server to gain full functionality of the system.



#. `Download <https://pypi.python.org/pypi/django-ftp-deploy/>`_  and install ``django-ftp-deploy`` with `requirements`_ manually,
    
   or Install ``django-ftp-deploy`` using pip::

        pip install django-ftp-deploy


#. Add ``ftp_deploy`` and ``ftp_deploy.server`` to your ``INSTALLED_APPS`` list in your settings
   
   .. code-block:: python

    INSTALLED_APPS = (
      ...
      'ftp_deploy',
      'ftp_deploy.server',
      ...
    )    

#. Add ``django-ftp-deploy`` to your ``urlpatterns`` list in your urls

   .. code-block:: python

        urlpatterns = patterns('',
            ...
            url(r'^ftpdeploy/', include('ftp_deploy.urls')),
            url(r'^ftpdeploy/', include('ftp_deploy.server.urls')),
            ...
          )

#. Synchronize your database. It is highly recommended you use `south <https://pypi.python.org/pypi/South/>`_ migration tool for future development purposes
   
   .. code-block:: python

        python manage.py migrate ftp_deploy
   
      

#. Copy static files into your ``STATIC_ROOT`` folder
   
   .. code-block:: python
   
       python manage.py collectstatic


Configuration
-------------

* Add ``DEPLOY_BITBUCKET_SETTINGS`` configuration to your settings::

    DEPLOY_BITBUCKET_SETTINGS = {
    'username'      : '',
    'password'      : '',
    }


  ``DEPLOY_BITBUCKET_SETTINGS``
        | *username*: bitbucket username
        | *password*: bitbucket password



* The FTP Deploy Dashboard **requires** the *bootstrap3* template pack for `django_crispy_forms <https://pypi.python.org/pypi/django-crispy-forms>`_

  .. code-block:: python
  
      CRISPY_TEMPLATE_PACK = 'bootstrap3'

  All required template files are included.
  
  
Celery
******

.. note:: Configuration presented below use django as a broker and result backend, however this is not recommended for production enviroment. Read more in Celery `documentation <https://celery.readthedocs.org/en/latest/>`_.

In order to use django as broker and backend, project need to have  `django-celery <https://pypi.python.org/pypi/django-celery>`_ project installed:

* Install django-celery using pip::
    
    pip install django-celery

* Add *djcelery* to your ``INSTALLED_APPS``
  
  .. code-block:: python

   INSTALLED_APPS = (
     ...
     'kombu.transport.django',
     'djcelery',
     ...
   )

Add celery configuration to your settings
  
  .. code-block:: python
  
      BROKER_URL = 'django://'
      CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'

Synchronize your database using `south <https://pypi.python.org/pypi/South/>`_::
    
  python manage.py migrate djcelery
  python manage.py migrate kombu.transport.django



Go to root folder of your project and run celery worker as follow::

  celery -A ftp_deploy worker --concurrency 1

.. note:: Used worker example apply only for development enviroment as well. Celery worker in production should be run as a deamon. Read more in Celery `documentation <http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html>`_.

.. warning:: Remember to include '*--concurrency 1*' option when running the worker. That avoid to perform more then one task at the same time.


