#!/usr/bin/env python

from setuptools import setup

setup(name='PRAF',
      version='1.2',
      description='Python framework for REST API',
      author='Yohann Gabory',
      author_email='yohann@gabory.fr',
      url='https://github.com/boblefrag/python-rest-api-framework',
      packages=['rest_api_framework', 'rest_api_framework.datastore',
                'rest_api_framework.models'],
      install_requires=["werkzeug", "python-dateutil"]
      )
