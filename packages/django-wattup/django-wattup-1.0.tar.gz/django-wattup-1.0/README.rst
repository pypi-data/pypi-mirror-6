=====

django-wattup v1.0

=====

A very simple contact form application for django.

Quick Start
-----------

Add "wattup" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'wattup',
      )

Include the wattup URLconf in your projects urls.py like so:

      url(r'', include('wattup.urls'))

Add this to your projects settings.py: 

      EMAIL_USE_TLS = foo
      
      EMAIL_HOST = 'foo'
      
      EMAIL_PORT = foo
      
      EMAIL_HOST_USER = 'foo'
      
      EMAIL_HOST_PASSWORD = 'foo'
      
      DEFAULT_TO_EMAIL = 'foo'
      
      DEFAULT_FROM_EMAIL = 'foo'
      
      ORG_NAME = 'foo'

*NOTE*

      Make sure that these settings are correct!

      "DEFAULT_TO_EMAIL" is the email address you want the messages to go to.

      "DEFAULT_FROM_EMAIL" is the email address you want the message to say it is from.

Run 'python manage.py syncdb'

Start the development server and visit http://127.0.0.1:8000/contact


From here, you should be able to send a message using the form you are given. If it does not work, check your settings.py
