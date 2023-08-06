Django AWS Manager
==================

Django AWS Manager is a django app that allows you to view and manage Amazon EC2 instances.  It can be useful as a way to access your server quickly from the admin screen and remote desktop.  The servers can be shut off during off hours (e.g., outside of market hours for a trading server) to save costs.

Install
-----------

> pip install django-aws-manager

or for the latest from github:

> pip install -e  git+git://github.com/jromich/django-aws-manager.git#egg=django-aws-manager


Quick start
-----------

1. Add "aws-manager" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'aws-manager',
    )

2. Include the aws_manager URLconf in your project urls.py like this::

    url(r'^aws-manager/', include('aws_manager.urls')),

3. Run `python manage.py migrate` to create the aws-manager models (or add it using south)

4. register the app with your admin in admin.py

5. add a new server record through the admin screen

Usage
------

- You can start/stop the server using the admin actions on the aws server list page.

- The server status is visible from the server detail view

- An RDP for remote desktop access file can be downloaded from the detail view if the EC2 server is windows based and is running.

- A management command can be used to start and stop the servers from the command line e.g.::

    python manage.py aws-server *servername* start

    (Available management commands: start, stop, state, start-wkdays-only, stop-wkdays-only)

- Starting and stopping of the servers can be scheduled using chron or heroku scheduler with the management commands

