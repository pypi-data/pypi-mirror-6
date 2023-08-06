from django.conf import settings
from django.utils.encoding import force_unicode


codes = [lang[0] for lang in settings.LANGUAGES]


def i18n_fieldnames(name):
    return tuple(['%s_%s' % (name, code) for code in codes])


def i18n_migration(migration):
    for model, fields in migration.models.iteritems():
        if model.startswith('checklist'):
            updated = {}
            for field, definition in fields.iteritems():
                if field[-3:] == '_en':
                    for fieldname in i18n_fieldnames(field[:-3]):
                        updated[fieldname] = definition
                else:
                    updated[field] = definition
            migration.models[model] = updated


def parse_tags(status):
    """Parses a string containing one or more EntryTag names.

    The string is typically a comma separate list each entry comprised of one
    or more words. Entries may be double-quotes in which case they can also
    contains commas.

    Args:
       status (str): A comma-separated list of one or more words/phrases.

    Returns:
       list(str): a sorted list of unique names.

    Taken from Alex Gaynor's `django-taggit
    <https://github.com/alex/django-taggit/>`_
    """
    if not status:
        return []

    status = force_unicode(status)

    # Special case - if there are no commas or double quotes in the
    # input, we don't *do* a recall... I mean, we know we only need to
    # split on spaces.
    if u',' not in status and u'"' not in status:
        words = list(set(split_strip(status, u' ')))
        words.sort()
        return words

    words = []
    charbuf = []
    # Defer splitting of non-quoted sections until we know if there are
    # any unquoted commas.
    to_be_split = []
    saw_loose_comma = False
    open_quote = False
    i = iter(status)
    try:
        while True:
            c = i.next()
            if c == u'"':
                if charbuf:
                    to_be_split.append(u''.join(charbuf))
                    charbuf = []
                # Find the matching quote
                open_quote = True
                c = i.next()
                while c != u'"':
                    charbuf.append(c)
                    c = i.next()
                if charbuf:
                    word = u''.join(charbuf).strip()
                    if word:
                        words.append(word)
                    charbuf = []
                open_quote = False
            else:
                if not saw_loose_comma and c == u',':
                    saw_loose_comma = True
                charbuf.append(c)
    except StopIteration:
        # If we were parsing an open quote which was never closed treat
        # the buffer as unquoted.
        if charbuf:
            if open_quote and u',' in charbuf:
                saw_loose_comma = True
            to_be_split.append(u''.join(charbuf))
    if to_be_split:
        if saw_loose_comma:
            delimiter = u','
        else:
            delimiter = u' '
        for chunk in to_be_split:
            words.extend(split_strip(chunk, delimiter))
    words = list(set(words))
    words.sort()
    return words


def split_strip(string, delimiter=u','):
    """Splits 'string' on 'delimiter'.

    Taken from Alex Gaynor's `django-taggit
    <https://github.com/alex/django-taggit/>`_
    """
    if not string:
        return []

    words = [w.strip() for w in string.split(delimiter)]
    return [w for w in words if w]


def tags_string(objs):
    """Get the list of names for the EntryTag objects.

    Given list of EntryTag instances, creates a string representation of
    the list suitable for editing by the user, such that submitting the
    given string representation back without changing it will give the
    same list of tags.

    EntryTag values which contain commas will be double quoted.

    Taken from Alex Gaynor's `django-taggit
    <https://github.com/alex/django-taggit/>`_
    """
    names = []
    for obj in objs:
        name = obj.name
        if u',' in name or u' ' in name:
            names.append('"%s"' % name)
        else:
            names.append(name)
    return u', '.join(sorted(names))
