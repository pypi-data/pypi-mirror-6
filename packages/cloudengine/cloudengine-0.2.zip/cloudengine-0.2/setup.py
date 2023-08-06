# -*- coding: utf-8 -*-
from distutils.core import setup


setup(
    name='cloudengine',
    version='0.2',
    author=u'Swapnil Talekar',
    author_email='swapnil@getcloudengine.net',
    packages= ['cloudengine', 'cloudengine.classes', 'cloudengine.core',
               'cloudengine.files', 'cloudengine.push', 'cloudengine.users'
                ],
    package_data={ 'cloudengine.classes' : ['fixtures/*.json'],
                   'cloudengine.core' : ['fixtures/*.json'],
                   'cloudengine.files' : ['fixtures/*.json'],
                   'cloudengine.push' : ['fixtures/*.json'],
                   'cloudengine.users' : ['fixtures/*.json'],
                   },
      
    include_package_data = True,
    url='http://github.com/cloudengine/CloudEngine',
    license='MIT license, see LICENCE.txt',
    description='An Open source backend for mobile apps',
    install_requires = ['MySQL-python',
                        'anyjson',
                        'argparse',
                        'azure',
                        'boto',
                        'django-filter',
                        'django-storages',
                        'djangorestframework',
                        'gevent',
                        'gevent-websocket',
                        'greenlet',
                        'gunicorn',
                        'mimeparse',
                        'mock',
                        'pymongo',
                        'python-dateutil',
                        'pytz',
                        'six',
                        'wsgiref',
                        ],
      zip_safe=False,
)

