"""Test for the files containing the translation strings.

Test Cases:

    EnglishLocaleTestCase - tests the English language strings.

Testing the contents of the .po files greatly simplifies the tests for the
various views. Instead of checking whether a specific string is displayed
you need to test that any string is displayed. That means the view test can
be language agnostic and you only need to test for the default language. This
has one limitation however, if a string is displayed outside of the trans or
blocktrans tags the view tests won't catch that. Hopefully this should be a
minor issue.
"""

import os
import polib

from django.conf import settings
from django.test import TestCase


def list_strings(entries):
    """Get all the strings surrounded by single-quotes."""
    return " ".join(["'%s'" % entry.msgid for entry in entries])


class LocaleTests(object):
    """Tests for the translation strings."""

    strings_file = None

    def setUp(self):
        path = os.path.join(settings.APP_ROOT, self.strings_file)
        self.pofile = polib.pofile(path)

    def test_for_untranslated_strings(self):
        """Verify that all strings have been translated."""
        entries = self.pofile.untranslated_entries()
        self.assertFalse(entries, "Untranslated: %s" % list_strings(entries))

    def test_for_fuzzy_strings(self):
        """Verify that no strings are marked as fuzzy."""
        entries = self.pofile.fuzzy_entries()
        self.assertFalse(entries, "Fuzzy: %s" % list_strings(entries))

    def test_for_obsolete_strings(self):
        """Verify that no strings are marked as obsolete."""
        entries = self.pofile.obsolete_entries()
        self.assertFalse(entries, "Obsolete: %s" % list_strings(entries))

    def test_for_duplicate_strings(self):
        """Verify that no strings duplicated where only the case changes."""
        dups = []
        strings = set()
        for entry in self.pofile:
            if entry.msgid.lower() in strings:
                dups.append(entry)
            else:
                strings.add(entry.msgid.lower())
        self.assertFalse(dups, "Duplicates: %s" % list_strings(dups))


class EnglishLocaleTests(LocaleTests, TestCase):

    strings_file = 'checklists/locale/en/LC_MESSAGES/django.po'


class PortugueseLocaleTests(LocaleTests, TestCase):

    strings_file = 'checklists/locale/pt/LC_MESSAGES/django.po'
