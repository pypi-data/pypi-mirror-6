# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-emailsys',
    version='0.0.14',
    author=u'Ron Sneh',
    author_email='me@ronsneh.com',
    packages=find_packages(),
    url='https://bitbucket.org/rsneh/django-emailsys',
    description='Provide the ability to send emails using WebServices',
    long_description=open('README').read(),
    include_package_data=True,
    zip_safe=False,
)
