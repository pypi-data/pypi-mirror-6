"""Initialize the database with data for the Plumage model.

The database must be empty otherwise an Integrity error will be raised. The
table is not cleared first in case the script is run inadvertently on an
existing database.
"""
from checklists import get_data_path
from checklists.models import Plumage

from utils import create_objects, get_object_data


def run():
    create_objects(Plumage, get_object_data(get_data_path('plumage'), 'slug'))
