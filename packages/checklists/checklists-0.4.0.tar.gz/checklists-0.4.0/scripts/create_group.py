"""create_group.py: Generate the SpeciesGroup file from a list of species.

"""
import sys

from utils import get_csv_data
from csvkit import CSVKitWriter


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ""
        print "usage: create_group.py <file> <file>"
        sys.exit(1)

    filein = sys.argv[1]
    fileout = sys.argv[2]

    table = get_csv_data(filein)

    genera = set()
    ordered = [['genus']]

    for idx, row in enumerate(table):
        if idx == 0:
            column = row.index('scientific_name')
        else:
            genus = row[column].split()[0]
            if genus not in genera:
                genera.add(genus)
                ordered.append([genus])

    with open(fileout, 'wb') as fp:
        writer = CSVKitWriter(fp)
        writer.writerows(ordered)