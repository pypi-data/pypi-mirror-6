#!/usr/bin/env python
from setuptools import setup, find_packages

version = __import__('testimony').get_version()

install_requires = [
    'Django>=1.4',
    'django-cms>=2.3.5',
]

dependency_links = []

setup(
    name = "django-testimony",
    version = version,
    url = 'https://bitbucket.org/oddotterco/django-testimony',
    license = 'BSD',
    platforms=['Linux'],
    description = "A Django app that will create a pluggable django-cms testimony form and content plugin within your project..",
    keywords='django, cms, theme',
    author = "Odd Otter Co",
    author_email = 'testimony@oddotter.com',
    packages = find_packages(),
    install_requires = install_requires,
    dependency_links = dependency_links,
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    package_dir = {
        'testimony': 'testimony',
    },
)
