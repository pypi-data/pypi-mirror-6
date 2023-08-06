#!/usr/bin/env python
from distutils.core import setup

version='1.0'

setup(
    name='django-chart-tools',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['chart_tools', 'chart_tools.templatetags'],
    package_data = {'chart_tools': ['templates/chart_tools/*.html']},

    url='https://bitbucket.org/kmike/django-chart-tools/',
    license = 'MIT license',
    description = """A thin wrapper around Google Chart API that tries not to invent a new language for describing charts.""",

    long_description = open('README.rst').read(),

    classifiers=[
        'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
