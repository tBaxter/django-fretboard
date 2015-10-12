## 1.14.0
* PEP-8 cleanup
* Switched to new Tango image sizing names.

## 1.13.0
* Refactored get_forum_list template tag
* Minor updates for Python3 compatibility

## 1.12.2
* Corrected urlparse import

## 1.12.1
* Fixed bad endwith in templates

## 1.12.0
* Make app settings play nice with 1.7 app loader
* added some middleware to test settings to keep Travis happy.

## 1.11.0
Closed CSRF hole in moderation commands

## 1.10.1
Tested build against Python 3

## 1.10.0
Added "first_post" cached property to Topic.

## 1.9.1
Removed select_related depth argument. Incompatible with Django 1.7

## 1.9.0
Updates for Django 1.7

## 1.8
Easier add topic form. No longer requires to be in a forum.

## 1.7
* Added convenience method to get topic via post.parent. Useful when using in conjunction with activity monitor

## 1.6
* Added get_image method to topics

## 1.5
* Added topic redirect url

## 1.4
* Updated to use newer Tango time tags

