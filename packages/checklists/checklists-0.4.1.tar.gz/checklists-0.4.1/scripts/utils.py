from csvkit import CSVKitReader


def get_csv_data(filename, encoding='utf-8'):
    """Load CSV formatted data from a a file.

    Args:
        filename (str): the path to the file

    Keyword Args:
         encoding (str): the character encoding for the file.

    Return:
        a table containing the data
    """
    with open(filename, 'rb') as fp:
        return list(CSVKitReader(fp, encoding=encoding))


def get_column_values(name, table):
    values = set()
    for idx, row in enumerate(table):
        if idx == 0:
            column = row.index(name)
        else:
            values.add(row[column])
    return values
