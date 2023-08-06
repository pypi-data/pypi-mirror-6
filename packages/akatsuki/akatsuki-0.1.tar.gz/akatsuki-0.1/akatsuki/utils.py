#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals


MONTH_DICT = {
    'JAN': 1,
    'FEB': 2,
    'MAR': 3,
    'APR': 4,
    'MAY': 5,
    'JUN': 6,
    'JUL': 7,
    'AUG': 8,
    'SEP': 9,
    'OCT': 10,
    'NOV': 11,
    'DEC': 12
}


def sort_by_date(entries, reverse=False):
    """Sort entries by year and month of the entry"""
    for entry in entries:
        # Convert month name to number
        if 'month' not in entry:
            entry['month_n'] = 0
        else:
            month_u = entry['month'].upper()
            if month_u in MONTH_DICT:
                entry['month_n'] = MONTH_DICT[month_u]
            else:
                entry['month_n'] = 0
    return sorted(entries,
                  key=lambda e: int(e['year']) * 100 + int(e['month_n']),
                  reverse=reverse)
