#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

packages = [
    'django_env_server',
    'django_env_server.management',
    'django_env_server.management.commands',
]

setup(
    name='django_env_server',
    version='0.0.1',
    packages=packages,
    license='MIT',
    description='Load environment variables into the Django development server',
    long_description=readme,
    author='Matt Foster',
    author_email='matt@mcfstr.com',
    url='https://github.com/mcfstr/django-env-server',
    install_requires=['django >= 1.4'],
)
