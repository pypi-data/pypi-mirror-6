================
django-testimony
================

A Django app that creates django-cms testimony content display plugin on a CMS page.  There is an option for static display of a specified number of testimonials or animated scrollers as well.

Dependencies
============

- django
- django-cms

Getting Started
===============

The easiest way is to use `pip` to install the app in your python environment like so:: 

  pip install django-testimonial
  
Then add the plugin to your Django-CMS project at the bottom of the `settings.py` file. Something like so:: 

  INSTALLED_APPS += ( 'testimony', )

Perform the usual `syncdb` and `migrate` to update your database::

  python manage.py syncdb
  python manage.py migrate

And you are done.  

Usage
=====

Add the plugin to a page and then go to your admin area to add some testimonials.  Mark the ones you want to see as published.  Thats it!

Advanced Usage
==============

You can add or change the templates available in the admin by creating a setting like the following in your `settings.py` file:: 

    if 'testimony' in INSTALLED_APPS:
        TESTIMONY_TEMPLATES = (
            ('testimony/list_default.html', gettext('Default list (stationary)')),
            ('testimony/rotator.html', gettext('Continuous scroll (animated)')),
            ('testimony/vticker.html', gettext('Scroll and pause (animated)')),
            )
    
Whats next?
===========
Adding the testimonial collection form as a plugin, with optional captcha support.    