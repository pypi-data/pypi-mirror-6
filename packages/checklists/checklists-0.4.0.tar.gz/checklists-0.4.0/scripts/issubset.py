"""issubset.py: is the data from a file a subset of the data from another.

Compare the values from a column in one file with the values from the
same column in another file and report whether the first set of values is
a subset of the second.

This script is used for checking the various data files used to populate the
database: verifying that the files used to load only species for a given
country or region only contain names which can be found in the main species
list. It is also used for checking that the entries in the main list for
populating the Species table only contains values which can be found in the
data for SpeciesGroup ensuring that the foreign key relationships can be
created when the data is loaded.

"""
import sys

from utils import get_csv_data, get_column_values


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print ""
        print "usage: issubset.py <file> <file> <column name>"
        sys.exit(1)

    subset_path = sys.argv[1]
    superset_path = sys.argv[2]
    column_name = sys.argv[3]

    superset_table = get_csv_data(superset_path)
    subset_table = get_csv_data(subset_path)

    superset = get_column_values(column_name, superset_table)
    subset = get_column_values(column_name, subset_table)

    print "The first file contains %d distinct values" % len(subset_table)
    print "The second file contains %d distinct values" % len(superset_table)

    missing = []

    for item in subset:
        if item not in superset:
            missing.append(item)

    if missing:
        print "The following values are in the first file but not in the" \
              " second:"
        for item in missing:
            print item
    else:
        print "The first file contains only values found in second."
