===============
django-yutils
===============

YUTILS == Yet/Why Another Utility Belt

This is a collection of misc. utilities for Django.


Installation
============

1. Download dependencies:
    - Python 2.6+
    - Django 1.5+
    
2. ``pip install django-yutils`` or ``easy_install django-yutils``



Configuration
=============

settings.py
-----------

1. Add "yutils" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        # all other installed apps
        'yutils',
    )
      
2. Add logger handler::

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            # all other handlers
            'log_file_yutils': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(os.path.join(os.path.dirname( __file__ ), '..'), 'logs/yutils.log'),
                'maxBytes': '16777216', # 16megabytes
             },
        },
        'loggers': {
            # all other loggers
            'yutils': {
                'handlers': ['log_file_yutils'],
                'propagate': True,
                'level': 'DEBUG',
            }
        }
    }
   
3. Configure YUTILS's settings::

    YUTILS = {
    	'mandrill_api_key': '{{ API_KEY }}'
    }
    
Logs
----

Create a 'logs' folder in your project's root folder (if you don't have one already).
Your project folder should look something like this::

    myproject/
        __init__.py
        settings.py
        urls.py
        wsgi.py
    logs/
    manage.py
