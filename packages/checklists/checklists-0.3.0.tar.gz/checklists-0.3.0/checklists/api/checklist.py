"""Functions for fetching Checklist objects from the database.

  checklist() - fetch checklists

  checklists_on() - fetch checklists for a given date.

  checklists_for() - fetch checklists for a given location on a given date.

  checklists_between() - fetch checklists between two given dates, inclusive.

  checklists_added_on() - fetch checklists added on a given date.

All of the function accept optional filters to narrow the set of checklists
fetched and an optional order to sort them.

"""

import operator

from django.db.models.query_utils import Q

from checklists.models import Checklist


def checklists(filters=None, order=None):
    """Return a set of Checklists, optionally filtered and ordered.

    An initial filter is used to select only Checklists that are marked as
    included. Additional filters may be added with the filters argument. The
    final query selects Checklists by ANDing all the filters together.

    The checklists can be sorted by passing in a tuple of the names of fields
    specifying the ordering for records fetched from the database.

    Kwargs:
        filters (list): a list of Q objects to select the checklists.
        order (tuple): ordering options used to sort the checklists.

    Returns:
        QuerySet. A QuerySet for the selected Checklist objects.
    """
    combined_filters = Q(include=True)
    if filters:
        combined_filters = reduce(operator.and_, filters, combined_filters)
    qs = Checklist.objects.filter(combined_filters)
    if order:
        qs = qs.order_by(*order)
    return qs


def checklists_on(date, filters=None, order=None):
    """Return the Checklists submitted for a given date.

    Args:
        date (date): the date a checklist is submitted for.

    Kwargs:
        filters (list): a list of Q objects to select the checklists.
        order (str tuple): the ordering options used to sort the checklists,
        overriding the default order (most recent first then location).

    Returns:
        QuerySet. A QuerySet for the selected Checklist objects.
    """
    initial = [Q(date=date)]
    if filters:
        initial.extend(filters)
    return checklists(initial, order)


def checklists_for(date, location, filters=None, order=None):
    """Return the Checklists submitted for a given date and location.

    Args:
        date (date): the date a checklist is submitted for.
        location (Location): the location a checklist was submitted for.

    Kwargs:
        filters (list): a list of Q objects to select the checklists.
        order (str tuple): the ordering options used to sort the checklists.

    Returns:
        QuerySet. A QuerySet for the selected Checklist objects.
    """
    initial = [Q(date=date), Q(location_id=location.id)]
    if filters:
        initial.extend(filters)
    return checklists(initial, order)


def checklists_between(earlier, later, filters=None, order=None):
    """Return the Checklists submitted between two dates.

    Args:
        earlier (date): the first date, inclusive, to select checklists
        later (date): the last date, inclusive, to select checklists

    Kwargs:
        filters (list): a list of Q objects to select the checklists.
        order (str tuple): the ordering options used to sort the checklists.

    Returns:
        QuerySet. A QuerySet for the selected Checklist objects.
    """
    initial = [Q(date__gte=earlier), Q(date__lte=later)]
    if filters:
        initial.extend(filters)
    return checklists(initial, order)


def checklists_added_on(date, filters=None, order=None):
    """Return the Checklists added on a given date.

    The date a checklist was added is used to identify recent updates to the
    database.

    Args:
        date (date): the date a checklist was added.

    Kwargs:
        filters (list): a list of Q objects to select the checklists.
        order (str tuple): the ordering options used to sort the checklists.

    Returns:
        QuerySet. A QuerySet for the selected Checklist objects.
    """
    initial = [Q(added_on=date)]
    if filters:
        initial.extend(filters)
    return checklists(initial, order)
