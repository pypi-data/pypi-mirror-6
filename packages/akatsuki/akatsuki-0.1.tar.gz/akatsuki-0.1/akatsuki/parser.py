#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from bibtexparser.bparser import BibTexParser


def load_bibtex_file(filepath):
    """Parse BibTeX file and return entry list"""
    with open(filepath, 'rU') as bibfile:
        bp = BibTexParser(bibfile)
        entries = bp.get_entry_list()

    entries = list(map(_capitalize_entry_title, entries))
    entries = list(map(_format_entry_authors, entries))
    return entries


def _capitalize_entry_title(entry):
    """Capitalize an entry title"""
    if 'title' in entry:
        entry['title'] = re.sub(r'{(\w+)}', r'\1', entry['title'])
    return entry


def _format_entry_authors(entry):
    """Format an entry author

    'A and B and C' -> 'A, B and C'"""
    if 'author' not in entry:
        return entry
    authors = entry['author'].split(' and ')
    authors = list(map(_format_entry_author, authors))
    last_author = authors[-1]
    authors.pop()
    text = ', '.join(authors)
    if text != '':
        text += ' and '
    text += last_author
    entry['author'] = text
    return entry


def _format_entry_author(author):
    author = author.strip()
    if author.endswith('.'):
        author = author.rstrip('.')
    return author
