# -*- coding: utf-8 -*-

import os

from setuptools import find_packages
from setuptools import setup

project = 'kotti_disqus'
version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name=project,
    version=version,
    description="Disqus commenting system add-on for Kotti",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Pylons",
        "Framework :: Pyramid",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: User Interfaces",
        ],
    keywords='kotti add-on',
    author='Natan Žabkar',
    author_email='natan.zabkar@gmail.com',
    url='https://github.com/nightmarebadger/kotti_disqus',
    license='BSD',
    packages=find_packages(exclude=('kotti_disqus.tests',)),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Kotti',
        'kotti_settings>=0.1',
        ],
    message_extractors={
        'kotti_disqus': [
            ('**.py', 'lingua_python', None),
            ('**.zcml', 'lingua_xml', None),
            ('**.pt', 'lingua_xml', None),
            ]
        },
    )
