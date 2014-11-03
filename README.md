django-fretboard
================

[![Build Status](https://travis-ci.org/tBaxter/django-fretboard.svg?branch=master)](https://travis-ci.org/tBaxter/django-fretboard)

Django-Fretboard is a fork of the forums used on gretschpages.com/forum/

It is built for Django 1.5+, and is not compatible with older versions of Django.

It has been tested in Python 2.7 and 3.4 and up to Django 1.7.1


### Settings
There are a few settings you may wish to override:

* PAGINATE_BY: defaults to 25 
* FORUM_BASE_NAME: defaults to site name
* COMMENT_PLACEHOLDER: placeholder text for post box.


### Requirements:

[Tango Shared Core](https://github.com/tBaxter/tango-shared-core) is used for standardizing images and allows for voting.
