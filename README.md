django-fretboard
================

[![Build Status](https://travis-ci.org/tBaxter/django-fretboard.svg?branch=master)](https://travis-ci.org/tBaxter/django-fretboard)

Django-Fretboard is a fork of the forums used on gretschpages.com/forum/

It is currently built for Django 2.0+, and is not compatible with older versions of Django. It has also been updated to use Python 3, because seriously, why wouldn't you at this point?

### Settings
There are a few settings you may wish to override in your project settings.py

* PAGINATE_BY: defaults to 25 
* FORUM_BASE_NAME: defaults to site name
* COMMENT_PLACEHOLDER: placeholder text for post box.


### Requirements:

[Tango Shared Core](https://github.com/tBaxter/tango-shared-core) is used for standardizing images and allows for voting.
