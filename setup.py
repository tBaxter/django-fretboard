# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

with open('docs/requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='django-fretboard',
    version='1.17.2',
    author=u'Tim Baxter',
    author_email='mail.baxter@gmail.com',
    url='http://github.com/tBaxter/django-fretboard',
    license='MIT',
    description='Responsive, powerful, simple Django forums.',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=required,
    zip_safe=False,
    include_package_data=True,
)
