"""Utilities for initializing the database."""

import os

from django.conf import settings

from csvkit import CSVKitReader, join


def get_data(directory, filename, encoding='utf-8'):
    """Load CSV formatted data from a a file.

    Args:
        directory (str): the directory to load the data from.
        filename (str): the name of the file in the directory

    Return:
        a table containing the data
    """
    with open(os.path.join(directory, filename), 'rb') as fp:
        return list(CSVKitReader(fp, encoding=encoding))


def get_languages():
    """Get the list of languages supported by the model.

    Returns:
        a list of the language suffixes from the LANGUAGES setting.
    """
    return [lang[0] for lang in settings.LANGUAGES]


def get_names_for_language(directory, language):
    """Get the names for a given language.

    The translated names for a given model are stored in a CSV file with
    a name that takes the form name_<lang>.csv where <lang> is the language
    code from the LANGUAGES setting.

    If a translation does not exist for the language then a default set of
    names (empty strings) are loaded form the file, default.csv. This allows
    the model to be initialized and the names can be added later.

    Args:
        directory (str): the directory to load the data from.
        language (str): the language code.

    Returns:
        a table created from the contents of the file.
    """
    table = get_data(directory, "names_%s.csv" % language)
    if table is None:
        table = get_data(directory, 'default.csv')
        table[0][table[0].index('default')] = 'names_%s' % language
    return table


def make_inner_join(column):
    """Get a function to join to two tables on a given column.

    Args:
        column (str): the name of the column.

    Returns:
        a function that performs an inner join on two tables.

    """
    def inner_join(left, right):
        """Join two tables on the specified column.

        Args:
            left (list): the table on the left side of the inner join.
            right (list): the table on the right side of the inner join.
            column (str): the name of the column to perform the join on.

        Returns:
            the joined table.
        """
        left_column = left[0].index(column)
        right_column = right[0].index(column)
        return join.inner_join(left, left_column, right, right_column)
    return inner_join


def get_names(directory):
    """Get the translated names for a model.

    Args:
        directory (str): the directory to load the data from.

    Returns:
        a generator which returns the translated names for each language
        supported by the model.
    """
    for language in get_languages():
        yield get_names_for_language(directory, language)


def get_object_data(directory, column):
    """Get all the values used to initialize the model.

    Args:
        directory (str): the directory to load the data from.
        column (str): the name of the column to perform inner joins on.

    Returns:
        a table containing the initial data merged with all the names for
        the various languages supported by the model.
    """
    return reduce(make_inner_join(column),
                  get_names(directory),
                  get_data(directory, 'initial.csv'))


def create_objects(model, table):
    """Create model objects from a table of data.

    The names of the object attributes are defined in the first row of the
    table.

    Args:
        model (class): the Model class.
        table (list): the table of data for the objects.

    Raises:
        IntegrityError if the object already exists.
    """
    keys = table[0]
    for values in table[1:]:
        model.objects.create(**dict(zip(keys, values)))
