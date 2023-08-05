# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django_sql_dashboards',
    version='0.0.1',
    author=u'Guillaume Thomas',
    description='',
    long_description=open('README.txt').read(),
    zip_safe=False,
    install_requires=[
       "Django",
       "django-bootstrap3>=2.3.0",
       "MySQL-python"
    ],
    include_package_data=True,
    packages=find_packages(),
)
