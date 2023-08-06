#!/usr/bin/env python

from distutils.core import setup

setup(name='django-dbgettext',
      version='0.1.1',
      description='Translate Django models by extracting data for gettext',
      author='Simon Meers',
      author_email='simon@simonmeers.com',
      url='http://bitbucket.org/drmeers/django-dbgettext/wiki',
      packages=['dbgettext', 'dbgettext.management', 'dbgettext.templatetags',
                'dbgettext.management.commands', 'dbgettext.lexicons'],
     )
