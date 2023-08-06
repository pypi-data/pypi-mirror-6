#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals


HTML_HEADER = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Bibliography</title>
</head>
<body>
<h1>Bibliography</h1>"""
HTML_FOOTER = """\
</body>
</html>"""


def export_html(filepath, entries):
    # Open HTML file
    html = open(filepath, 'w')
    # Write HTML header lines
    html.write(HTML_HEADER)

    year = 0
    for entry in entries:
        if year != int(entry['year']):
            year = int(entry['year'])
            html.write('<h2>%d</h2>\n' % year)
        html.write('<p>\n')
        html.write(_entry_html(entry))
        html.write('</p>\n')

    # Write HTML footer lines
    html.write(HTML_FOOTER)


def _entry_html(entry):
    result = ''
    result += '%s<br>\n' % entry['author']
    result += '%s<br>\n' % entry['title']
    if 'journal' in entry:
        result += entry['journal'] + ' '
        if 'year' in entry:
            result += entry['year']
        if 'month' in entry:
            result += ' ' + entry['month']
        result += ';'
        if 'volume' in entry:
            result += entry['volume']
        if 'number' in entry:
            result += '(%s)' % entry['number']
        if 'pages' in entry:
            result += ':%s' % entry['pages']
        result += '.<br>\n'
    return result
