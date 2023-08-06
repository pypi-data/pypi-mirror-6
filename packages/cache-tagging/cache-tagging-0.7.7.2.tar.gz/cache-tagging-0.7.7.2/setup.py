#!/usr/bin/env python
#
# Copyright (c) 2011-2013 Ivan Zakrevsky
# Licensed under the terms of the BSD License (see LICENSE.txt)
import os.path
from setuptools import setup, find_packages

app_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

setup(
    name = app_name,
    version = '0.7.7.2',

    packages = find_packages(),
    include_package_data=True,

    author = "Ivan Zakrevsky",
    author_email = "ivzak@yandex.ru",
    description = "Cache-tagging allows you easily invalidate all cache records tagged with a given tag(s). Django support.",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license = "BSD License",
    keywords = "django cache tagging",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url = "https://bitbucket.org/emacsway/{0}".format(app_name),
)
