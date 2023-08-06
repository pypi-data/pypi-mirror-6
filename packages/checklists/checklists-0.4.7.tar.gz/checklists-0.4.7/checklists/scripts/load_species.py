"""Initialize the database with data for the Species model.

The database must be empty otherwise an Integrity error will be raised. The
table is not cleared first in case the script is run inadvertently on an
existing database.
"""

from checklists import get_data_path
from checklists.models import Species, Rank, SpeciesGroup, \
    set_current_user, clear_current_user

from utils import make_inner_join, get_data, get_names


def create_species(table):
    """Create Species objects from a table of data.

    The names of the object attributes are defined in the first row of the
    table. The columns 'rank' and 'genus' are replaced with matching objects
    from the Rank and SpeciesGroup models.

    Args:
        model (class): the Model class.
        table (list): the table of data for the objects.

    Raises:
        IntegrityError if the object already exists.
    """
    keys = table[0]
    for values in table[1:]:
        kwargs = dict(zip(keys, values))
        rank = kwargs.pop('rank', '')
        if rank:
            kwargs['rank'] = Rank.objects.get(slug=rank)
        genus = kwargs.pop('genus', '')
        if genus:
            try:
                kwargs['group'] = SpeciesGroup.objects.get(genus=genus)
            except SpeciesGroup.DoesNotExist:
                kwargs['group'] = None
                print "There is no SpeciesGroup for the genus %s" % genus
                print "Species created with group set to None"
                print kwargs

        Species.objects.create(**kwargs)

def run(*args):
    data_dir = get_data_path('species')
    joiner = make_inner_join('standard_name')

    if len(args):
        list_name = 'list_%s.csv' % args[0]
        initial = joiner(get_data(data_dir, list_name),
                         get_data(data_dir, 'initial.csv'))
    else:
        initial = get_data(data_dir, 'initial.csv')

    set_current_user('load_species')
    create_species(reduce(joiner, get_names(data_dir), initial))
    clear_current_user()
