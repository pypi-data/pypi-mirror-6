"""Functions for fetching Entry objects from the database.

  entries() - fetch checklist entries.

  entries_on() - fetch checklist entries for a given date.

  entries_for() - fetch checklist entries for a given location, on a given date.

  entries_between() - fetch checklist entries between two given dates,
      inclusive.

  entries_added_on() - fetch checklist entries added on a given date.

  entries_added_between() - fetch checklist entries added between two given
      dates, inclusive.

All of the functions accept optional filters to narrow the set of entries
fetched and an optional order to sort them. The default is to order the entries
first by date of the checklist (most recent first) then alphabetically by the
name of the location."""

import operator

from django.db.models.query_utils import Q

from checklists.models import Entry


def entries(filters=None, order=None):
    """Return a list of Entries, optionally filtered and ordered.

    An initial filter is used to select only Entries that are marked as
    included and where the parent Checklist is also included. Additional
    filters may be added with the filters argument. The final query selects
    Entries by ANDing all the filters together.

    The entries can be sorted by passing in a tuple of the names of fields
    specifying the ordering for records fetched from the database.

    Kwargs:
        filters (list): a list of Q objects to to add to the initial set
        of filters.
        order (str tuple): the list of fields to add to the initial sort
        order.

    Returns:
        QuerySet. A QuerySet for the selected Entry objects in the defined
        order.
    """
    combined_filters = Q(include=True) & Q(checklist__include=True)
    if filters:
        combined_filters = reduce(operator.and_, filters, combined_filters)
    qs = Entry.objects.filter(combined_filters)
    if order:
        qs = qs.order_by(*order)
    return qs


def entries_on(date, filters=None, order=None):
    """Return all the Entries for a given date.

    Args:
        date (date): the date that the parent checklist were submitted for.

    Kwargs:
        filters (list): a list of Q objects to select the entries.
        order (str tuple): the ordering options used to sort the entries.

    Returns:
        QuerySet. A QuerySet for the selected Entry objects.
    """
    initial = [Q(checklist__date=date)]
    if filters:
        initial.extend(filters)
    return entries(initial, order)


def entries_for(date, location, filters=None, order=None):
    """Return all the Entries for a given date and location.

    Args:
        date (date): the date that the parent checklist were submitted for.
        location (Location): the location that the parent checklist were
        submitted for.

    Kwargs:
        filters (list): a list of Q objects to select the entries.
        order (str tuple): the ordering options used to sort the entries.

    Returns:
        QuerySet. A QuerySet for the selected Entry objects.
    """
    combined_filters = [
        Q(checklist__date=date), Q(checklist__location_id=location.id)]
    if filters:
        combined_filters.extend(filters)
    return entries(combined_filters, order)


def entries_between(earlier, later, filters=None, order=None):
    """Return all the Entries between two dates.

    Args:
        earlier (date): the first date, inclusive, that the parent
        checklist were submitted for.
        later (date): the last date, inclusive, that the parent checklist
        were submitted for.

    Kwargs:
        filters (list): a list of Q objects to select the entries.
        order (str tuple): the ordering options used to sort the entries.

    Returns:
        QuerySet. A QuerySet for the selected Entry objects.
    """
    initial = [Q(checklist__date__gte=earlier), Q(checklist__date__lte=later)]
    if filters:
        initial.extend(filters)
    return entries(initial, order)


def entries_added_on(date, filters=None, order=None):
    """Return all the Entries added on a given date.

    Args:
        date (date): the date that the parent checklist were added on

    Kwargs:
        filters (list): a list of Q objects to select the entries.
        order (str tuple): the ordering options used to sort the entries.

    Returns:
        QuerySet. A QuerySet for the selected Entry objects.
    """
    initial = [Q(checklist__added_on=date)]
    if filters:
        initial.extend(filters)
    return entries(initial, order)


def entries_added_between(earlier, later, filters=None, order=None):
    """Return all the Entries added between two dates.

    Args:
        earlier (date): the first date, inclusive, that the parent
        checklist were added on.
        later (date): the last date, inclusive, that the parent checklist
        were added on.

    Kwargs:
        filters (Q list): a list of additional filters to select the entries.
        order (str tuple): the ordering options used to sort the entries.

    Returns:
        QuerySet. A QuerySet for the selected Entry objects.
    """
    initial = [Q(checklist__added_on__gte=earlier),
               Q(checklist__added_on__lte=later)]
    if filters:
        initial.extend(filters)
    return entries(initial, order)
