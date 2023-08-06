CloudEngine
===========

**Open source backend stack for mobile.**


Overview
=========

CloudEngine is an open source backend stack for building awesome mobile apps.
The aim of the project is to help mobile app developers get their apps off the ground
as quickly as possible. For this, CloudEngine needs to provide all the basic services
required for building rich mobile apps out-of-the-box. Currently there are bare minimum
services included. The aim is also to create fully customizable and extensible framework for
building backend mobile services. The core services could be tightly coupled.


Requirements
=============
CloudEngine runs only on gunicorn server and hence currently runs only
on UNIX environments.

* Python (2.7.5+)
* Django (1.5.4+)
* MongoDB (2.4.6+)
* MySQL (5.5+)

All the python library dependencies are listed in `requirements.txt`

Installation
===============

You can install using pip. On Windows, CloudEngine will be installed without support for gevent-socketio 
and gunicorn (i.e. you can't test push notifications and related features).

	pip install cloudengine	


Configure database and other necessary 
settings in `cloudengine.settings.py`. Create database tables.

	python manage.py syncdb
	
Run the gunicorn server with gevent-socketio worker class. Add the project directory 
to python path

	gunicorn -w 1 --pythonpath .  \
	--worker-class socketio.sgunicorn.GeventSocketIOWorker  \
	cloudengine.wsgi:application
	
On development environments, you can simply run the django development server

	python manage.py runserver
	

Technical Overview
====================

CloudEngine is a pure Python django stack. Each backend service is plugged in as django
app. Each service should be independently pluggable and usable except the core services. 
Currently some of the services are tightly coupled. CloudEngine currently runs on gunicorn
server and hence runs only on UNIX environments. CloudEngine uses the excellent
[gevent-socketio][gevent-socketio] library for implementing real time communication
channels, which are the basis of current push notifications system. 
gevent-socketio is the python port of the popular [socket.io][socket.io] library. 
For storage we use a combination of relational database (MySQL, PostgreSQL) and a
NoSQL db (Currently mongodb). Ideally, we'd like to move completely to a NoSQL db.
But we want to leverage a lot of django goodies and there is no elegant way to retain 
that while migrating to NoSQL. CloudEngine uses [django-rest-framework][django-rest] for providing
REST interfaces to services.


Client libraries
==================

The aim of the project is also to provide readily available client libraries for 
as many different platforms as possible to make it easier to consume CloudEngine
services on mobile devices.
Currently only Android SDK is available at -  [https://github.com/cloudengine/Android-SDK][android-sdk]
We plan to add SDKs for more platforms 


Documentation & Support
========================

Complete documentation is available at - ?

For discussions, questions and support use the [CloudEngine discussion group][group]

or [Github issue tracking][issue-tracker]

You may also want to [follow the authors on twitter] [twitter]. 



License
========
See the LICENSE file for more info.



[twitter]: https://twitter.com/thecloudengine
[group]: https://groups.google.com/forum/#!forum/cloudengine-dev
[gevent-socketio]: https://github.com/abourget/gevent-socketio
[socket.io]: http://socket.io
[issue-tracker]: https://github.com/cloudengine/CloudEngine/issues
[android-sdk]: https://github.com/cloudengine/Android-SDK
[django-rest]: https://github.com/tomchristie/django-rest-framework
