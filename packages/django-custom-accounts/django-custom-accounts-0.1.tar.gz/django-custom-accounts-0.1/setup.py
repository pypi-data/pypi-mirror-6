#!/usr/bin/env python

import accounts
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='django-custom-accounts',
    version=accounts.__version__,
    description='A custom accounts application for Django',
    author='Alvaro Lizama',
    author_email='nekrox@gmail.com',
    url='https://github.com/nekrox/django-custom-accounts',
    download_url='https://github.com/nekrox/django-custom-accounts/archive/master.tgz',
    packages=[
        'accounts',
    ],
    include_package_data=True,
    install_requires=[
        "Django >= 1.5",
    ],
    license='MIT License',
    keywords='django custom user auth model email without username',
    classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
    )
