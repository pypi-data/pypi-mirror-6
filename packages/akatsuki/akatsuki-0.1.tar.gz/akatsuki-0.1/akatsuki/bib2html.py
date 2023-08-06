#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from akatsuki.exporter import export_html
from akatsuki.parser import load_bibtex_file
from akatsuki.utils import sort_by_date


def main(bibtex_file, html_file):
    """Load BibTeX file and export to HTML file"""
    entries = load_bibtex_file(bibtex_file)
    entries = sort_by_date(entries, reverse=True)
    export_html(html_file, entries)
