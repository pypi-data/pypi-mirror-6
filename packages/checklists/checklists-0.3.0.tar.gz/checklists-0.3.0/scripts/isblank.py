"""isblank.py: does a CSV file contain empty values.

This script is used to check whether any of the values in a given column of a
CSV file are blank. This is useful when working with translations to see
whether there are any that have been missed.

"""
import sys

from utils import get_csv_data


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ""
        print "usage: isblank.py <file> <column name>"
        sys.exit(1)

    file_path = sys.argv[1]
    column_name = sys.argv[2]

    table = get_csv_data(file_path)

    for idx, row in enumerate(table):
        if idx == 0:
            column = row.index(column_name)
        else:
            if not row[column].strip():
                print "Row %d is blank"
