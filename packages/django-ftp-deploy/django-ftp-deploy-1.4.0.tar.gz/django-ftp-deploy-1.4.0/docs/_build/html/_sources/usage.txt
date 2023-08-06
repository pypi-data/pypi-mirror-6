Usage
=====

Using the django-ftp-deploy module

.. note:: For full functionality you need to have *FTP Deploy Server* installed in your project, otherwise you can manage your deploys in admin page. For further informations visit :ref:`installation <installation>` section. 

.. important:: It's important to always use **non fast forward** git merge to your deploy branch! Otherwise POST Hook has no information about commits included in merge.
    
  .. code-block:: python
  
      git merge --no-ff


Login
*****

Login screen for FTP Deploy Server application. Page is available at::

  /ftpdeploy/


Dashboard
*********

The Main **Dashboard** page is available at::

	/ftpdeploy/dashboard/

| The dashboard allows you to manage all of your services from one page. All failing services are placed on the top of the list, to make it easy to find all services containing issues.
| A screenshot is available in the :ref:`Other <other>` section.

| If service is currently deploying, status icon is change to animated cog.


Service
*******

Service is one repository-to-ftp configuration.



Add Service
-----------

To add new service click ``Add Service`` button on the *Service* dashboard page or visit::

	/ftpdeploy/service/add

The ``Add Service`` form includes sections with fields listed below. Please read the following instructions in order to fill out the form correctly:

``FTP Settings``
   
   | *Host:* FTP server host
   | *Username:* FTP server username
   | *Password:* FTP server password
   | *Path*: path to the root directory of your project

``Repository``

   | *Source:* Source of repository (Bitbucket or Github)
   | *Respository Name:* Name of the repository to deploy. After you choose source, the list is populated dynamically from your repository account
   | *Respository Slug:* Slug of your Repository Name. This field is populated *dynamically* by using 'slugify' on the repository name
   | *Branch*: Branch name for deploy service
	
``Notification``

   | *Notification*: Notification set using by service. 

``Secutiry``

   | *Security Key*: 30 character alpha-numeric, unique, random generated string. Security Key is used to create repository hook. 


During saving process, all values are validated. The following checks are performed.

* FTP hostname
* FTP login credentials
* FTP path
* Repository login credentials
* Repository slug name (if exists on repository list)
* Repository branch
* Repository hook


All services will fail their first validation, as no POST hook will exist yet. You will be prompted to add the service hook by the error message. All issues are listed under status section in ``Manage Service`` page.

.. note:: Repository POST hook is **required**. It provides information about pushed git commits, along with branch name, which is used in the deploy process. You can manage this manually on the repository page if you need to. The validation process respects all changes you have made directly on the repository site as well.




Manage Service
--------------

To manage a service click the ``Manage`` button next to the service name or visit::
	
	/ftpdeploy/service/{service_id}/manage


The manage page contains sections such as:

* Statistics of service 
  
  | - POST Hook status (if not set up, ``Add Hook`` link is provided)
  | - number of success deploys
  | - number of fail deploys if exists
  | - number of skiped deploys if exists
  | - last deploy user
  | - last deploy date

* Notification 
   
  Represent current notification settings. You can change notification by clicking ``Cog icon``


*  Status 
   
   Icon representing current status. If validation passes, it displays date of the latest status check, otherwise list of issues. In order to refresh the status you need to click *status icon* (the same applies for services list on dashboard page) or edit and save service.

   .. note:: Status is not refreshed automatically because of expense of validation process. Usually takes up to 15 seconds to go through all validation points.

   
* Restore Deploys (if any of deploys has failed)
  
  List of failing deploys for service in chronological order. The list provides the following details: 

  | - Deploy date
  | - Deploy user
  | - Deploy commits (commit message, commit user, commit raw node)
  | - Restorable flag
  | - Status

  If the list contain deploys that you don't want to restore you can skip them by clicking the ``Skip`` button assigned to the failed deployment.

  .. warning:: **Skipping deploys may cause inconsistent data between your repository and FTP files or may fail to restore deploys**. 
   
   *Example*: if you skip a deploy with commit that creates a new file, and next deployment include commit that attempts to remove this file, the entire restore process would fail because of trying remove a file that actually doesn't exist. 



  The entire process of restore failed deploys is described in the `Restore Failed Deploys`_ section.



* Recent Deploys
  
  List of recent deploys. List mirror `Logs`_ filtered by current service.


* If service is deploying or has deploy in the queue, progress bar is presented to display current status. Restore deploy is locket at this time as well.


Edit Service
------------  

To edit service click ``Edit`` button next to the service name or visit::
  
  /ftpdeploy/service/{service_id}/edit

Edit page provides the same functionality as the `Add Service`_ page. If you need to load list of your repositories again, you need to reset *Source* drop down list, and choose option again.

After you press submit, service data goes through the validation process again, and redirect you to the `Manage Service`_ page



Restore Failed Deploys
----------------------

If any deploy fails, the service has an opportunity to restore them. It's possible by capturing payload data from POST Hook and storing the data before a deployment is performed.
The restoring process works as follows:

``Restoring process``

 | - Find first failed and not skipped deploy
 | - Built the restore tree, since first fail deploy up to the most recent deploy (omit skip deploys)
 | - Build new payload data based on restore tree
 | - Build commits information and files diff from new payload
 | - After click restore send new payload to deploy (as it would be a normal POST Hook), remove deploys included in restore, and store new payload.


In order to restore deploys you need to click ``Restore Deploys`` on `Manage Service`_ page. That will bring the popup window with information about the restore such as :

 | - Number of commits included in restore along with details (commit message, commit user, raw node)
 | - File diff (New Files, Modified Files, Removed Files)  

To run restore process you need to press ``Restore`` button.

.. note:: If your restore keep failing you can manage this manually. As you never lose deploys and commits information you can rely on *File diff*  even after fail restore. You can just transfer and remove all relevant files included in *File diff* and skip all failed deploys. That help you to keep your data consistent if restore fails.



Notifications
*************

Configurable sets of notifications.

Add/Edit Notification
---------------------

To add new notification click ``Add Notification`` button on the *Notification* dashboard page or visit::

  /ftpdeploy/notification/add


You can add emails as many as you like and choose what kind of notification they going to receive. In addition there are two extra options as follow:

  | *deploy_user*: user who make an deploy
  | *commit_user*: email list of users who made a commit(s) included in deploy


In order to edit notification you can click ``Edit`` button next to notification name or visit::
  
  /ftpdeploy/{notification_id}/edit


*Edit Notification* screen provide same functionality as *Add Notification* page.



Email Templates
---------------

The email notification system provides html and text templates that can be overriden if you wish. In order to do that you need to create your own templates for success and fail notification separately::


  /ftp_deploy/email/email_success.html
  /ftp_deploy/email/email_success.txt

  /ftp_deploy/email/email_fail.html
  /ftp_deploy/email/email_fail.txt


All templates are rendered with the following context information:

``Success Template``
  | - *{{service}}* object
  | - *{{host}}* of the current website (where the email came from)
  | - *{{commits_info}}* in format [['commit message','commit user','raw node'],[...]]
  | - *{{files_added}}* , *{{files_modified}}*, *{{files_removed}}* in format ['file_name_1', 'file_name_2', ...]


``Fail Template``
  | - *{{service}}* object
  | - *{{host}}* of the current website (where the email came from)
  | - *{{error}}* message of the exception


Logs
****

In order to see logs page you need to click ``Log`` button on the top of the page or visit::

  /ftpdeploy/log

Logs provide information about all activity in the FTP Deploy application. 

In addition log list contain information about number of commits included in deploy. If you need to see more details about included commits, you can click the ``commits number`` (commit message, commit user, raw node).


