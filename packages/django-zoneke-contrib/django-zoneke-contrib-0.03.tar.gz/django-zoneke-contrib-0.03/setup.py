#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

from setuptools import setup, find_packages
import os
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
REQUIREMENTS = open(os.path.join(os.path.dirname(__file__), 'requirements/common.txt')).read().split('\n'),

__version__ = 0.03

METADATA = dict(
    name='django-zoneke-contrib',
    version=__version__,
    author='chen chiyuan',
    author_email='chenchiyuan03@gmail.com',
    description='Django Contrib',
    long_description=README,
    url='http://github.com/chenchiyuan/contrib',
    keywords='python django contrib util weixin',
    install_requires=REQUIREMENTS,
    include_package_data=True,
    license='BSD License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
    packages=find_packages(),
)

if __name__ == '__main__':
    setup(**METADATA)
