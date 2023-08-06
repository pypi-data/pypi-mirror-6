#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup, find_packages


# Test if hardlinks work. This is a workaround until
# http://bugs.python.org/issue8876 is solved
if hasattr(os, 'link'):
    tempfile = __file__ + '.tmp'
    try:
        os.link(__file__, tempfile)
    except OSError as e:
        if e.errno == 1:  # Operation not permitted
            del os.link
        else:
            raise
    finally:
        if os.path.exists(tempfile):
            os.remove(tempfile)


dateutil = 'python-dateutil'
if sys.version_info < (3, 0):
    dateutil = 'python-dateutil==1.5'

setup(
    name='django-schedule-frinat',
    version='0.6',
    description='A calendaring app for Django (frinat edition).',
    author='Anthony Robert Hauber',
    author_email='thauber@gmail.com',
    url='http://github.com/thauber/django-schedule/tree/master',
    packages=[
        'schedule',
        'schedule.conf',
        'schedule.feeds',
        'schedule.management',
        'schedule.management.commands',
        'schedule.models',
        'schedule.templatetags',
        'schedule.tests',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    install_requires=['setuptools', 'vobject', dateutil],
    license='BSD',
    test_suite = "schedule.tests",
)
