#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages


version = __import__('checklists').get_version()


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()


if 'sdist' in sys.argv:
    # clear compiled mo files before building the distribution
    walk = os.walk(os.path.join(os.getcwd(), 'checklists/locale'))
    for dirpath, dirnames, filenames in walk:
        if not filenames:
            continue
        if 'django.mo' in filenames:
            os.unlink(os.path.join(dirpath, 'django.mo'))
else:
    # compile the po files
    try:
        import django
    except ImportError:
        pass
    else:
        dir = os.getcwd()
        os.chdir(os.path.join(dir, 'checklists'))
        os.system('django-admin.py compilemessages')
        os.chdir(dir)

setup(
    name="checklists",
    version=version,
    description="A reusable Django model for managing checklists of birds.",
    long_description=read("README.rst"),
    author="Stuart MacKay",
    author_email="smackay@flagstonesoftware.com",
    license="BSD",
    url='http://www.github.com/StuartMacKay/checklists',
    packages=find_packages(),
    include_package_data=True,
    keywords='django checklists',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Natural Language :: English",
    ],
    test_suite='checklists.tests.runtests.runtests',
    tests_require=[
        'mock==1.0.1',
        'factory-boy==2.1.1',
        'polib==1.0.4',
    ],
    install_requires=[
        'pytz',
        'dbf==0.95.004',
        'django==1.4.10',
        'django-transmeta==0.6.9',
        'django-admin-enhancer==0.1.2',
        'django-autocomplete-light==1.1.7',
        'django-tablib==3.0.2',
        'django-extensions==1.3.3',
        'django-taggit==0.9.3',
        'south==0.7.6',
        'csvkit==0.7.2',
    ],
)
