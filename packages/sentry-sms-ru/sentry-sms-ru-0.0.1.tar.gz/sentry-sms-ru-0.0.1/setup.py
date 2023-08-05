#!/usr/bin/env python
'''
Sentry-Pushover
=============
A [Sentry](https://www.getsentry.com/) plugin that sends notofications to a [Pushover](https://pushover.net).

License
-------
Copyright 2012 Janez Troha

This file is part of Sentry-Pushover.

Sentry-Pushover is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Sentry-Pushover is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Sentry-Pushover.  If not, see <http://www.gnu.org/licenses/>.
'''
from setuptools import setup, find_packages

setup(
    name='sentry-sms-ru',
    version='0.0.1',
    author='Yevgeniy Shchemelev',
    author_email='shchemelevev@gmail.com',
    url='https://bitbucket.org/silver_sky/sentry_sms_ru',
    description='A Sentry plugin that integrates with sms.ru',
    long_description=__doc__,
    license='GPL',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests',
    ],
    entry_points={
        'sentry.plugins': [
            'pushover = sentry_sms_ru.plugin:SMSNotifications'
        ]
    },
    include_package_data=True,
)
