django-fretboard
================

Django-Fretboard is a fork of the forums used on gretschpages.com/forum/

It is built for Django 1.5, and is not compatible with previous versions of Django, mostly due to the new 1.5 user objects.


### Settings
There are a few settings you may wish to override in your project's settings.py:

* PAGINATE_BY: defaults to 25 
* FORUM_BASE_NAME: defaults to site name
* COMMENT_PLACEHOLDER: placeholder text for post box. Defaults to "be nice"
