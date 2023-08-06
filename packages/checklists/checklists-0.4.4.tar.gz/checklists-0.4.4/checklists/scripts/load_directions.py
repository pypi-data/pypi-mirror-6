"""Initialize the database with data for the Direction model.

The database must be empty otherwise an Integrity error will be raised. The
table is not cleared first in case the script is run inadvertently on an
existing database.
"""
from checklists import get_data_path
from checklists.models import Direction, set_current_user, clear_current_user

from utils import create_objects, get_object_data


def run():
    set_current_user('load_directions')
    create_objects(Direction, get_object_data(get_data_path('direction'), 'slug'))
    clear_current_user()
