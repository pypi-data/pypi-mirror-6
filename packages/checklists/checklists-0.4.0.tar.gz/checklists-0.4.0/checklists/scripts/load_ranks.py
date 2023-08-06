"""Initialize the database with data for the Rank model.

The database must be empty otherwise an Integrity error will be raised. The
table is not cleared first in case the script is run inadvertently on an
existing database.
"""
from checklists import get_data_path
from checklists.models import Rank, set_current_user, clear_current_user

from utils import create_objects, get_object_data


def run():
    set_current_user('load_ranks')
    create_objects(Rank, get_object_data(get_data_path('rank'), 'slug'))
    clear_current_user()
