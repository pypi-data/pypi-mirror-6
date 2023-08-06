"""Initialize the database with data for the SpeciesGroup model.

The database must be empty otherwise an Integrity error will be raised. The
table is not cleared first in case the script is run inadvertently on an
existing database.
"""

from checklists import get_data_path
from checklists.models import SpeciesGroup, set_current_user, \
    clear_current_user

from utils import get_data, make_inner_join, get_names, create_objects


def run(*args):
    data_dir = get_data_path('species_group')
    join_on_family = make_inner_join('family')
    join_on_genus = make_inner_join('genus')

    if len(args):
        list_name = 'list_%s.csv' % args[0]
        initial = join_on_genus(get_data(data_dir, list_name),
                                get_data(data_dir, 'initial.csv'))
    else:
        initial = get_data(data_dir, 'initial.csv')

    table = reduce(join_on_family, get_names(data_dir), initial)
    set_current_user('load_species_groups')
    create_objects(SpeciesGroup, table)
    clear_current_user()

