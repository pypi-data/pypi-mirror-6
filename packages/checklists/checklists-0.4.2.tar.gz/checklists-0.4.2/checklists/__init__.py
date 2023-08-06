"""A Django project for managing a database of checklists of birds."""

import os

VERSION = (0, 4, 2, 'final')

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def get_version():
    main = '.'.join(str(x) for x in VERSION[:3])
    sub = VERSION[3] if VERSION[3] != 'final' else ''
    return str(main + sub)


def get_data_path(*args):
    return os.path.join(DATA_DIR, *args)
