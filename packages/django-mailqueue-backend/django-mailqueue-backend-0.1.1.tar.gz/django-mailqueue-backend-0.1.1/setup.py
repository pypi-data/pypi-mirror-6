from os import path as os_path
from setuptools import setup, find_packages

import mailqueue_backend

description = long_description = "Simple Mail Queuing Backend for Django"
if os_path.exists('README.rst'):
    long_description = open('README.rst').read()

version = mailqueue_backend.VERSION

def read(fname):
    return open(os_path.join(os_path.dirname(__file__), fname)).read()

#mailq | tail -n +2 | grep -v '^ *(' | awk  'BEGIN { RS = "" } { if ($7 == "from@example.com" || $8 == "from@example.com") print $1 } ' | tr -d '*!'| postsuper -d -

setup(name='django-mailqueue-backend',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Communications :: Email",
        "Topic :: Utilities",
        "Framework :: Django",
    ],
    keywords='django mail queue smtp backend',
    maintainer='Dwaiter.com',
    maintainer_email='dev@dwaiter.com',
    url='https://bitbucket.org/dwaiter/django-mailqueue-backend',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django>=1.2', 'queue-front>=0.7.2']
)