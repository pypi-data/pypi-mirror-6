import os
import sys

from setuptools import setup

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

README = open('{0}/README.md'.format(CURRENT_DIR)).read()
LICENSE = open('{0}/LICENSE'.format(CURRENT_DIR)).read()


def find_requirements(filename):
    requirements = []
    with open('{0}/{1}'.format(CURRENT_DIR, filename), 'r') as reqs:
        requirements = reqs.readlines()
    return requirements

requirements = find_requirements('requirements.txt')


setup(
    name='auth-signals-connector',
    version='0.1.0',
    description='Simple abstraction layer for django.contrib.auth.signals',
    long_description=(README),
    license=LICENSE,
    author='Ivan Kolodyazhny',
    author_email='e0ne@e0ne.info',
    url='https://github.com/e0ne/auth-signals-connector',
    install_requires=requirements,
    packages=['auth_signals_connector'],
    include_package_data=True,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
    keywords='django, auth, signals, login, logout',
)
