#!/usr/bin/env python

"""
functionality related to templates
"""

import os
import sys
from optparse import OptionParser
from pkg_resources import iter_entry_points
from pkg_resources import resource_filename

def template_dirs():
    template_dirs = set()
    for formatter in iter_entry_points('decoupage.formatters'):
        try:
            formatter.load()
        except:
            continue
        template_dir = resource_filename(formatter.module_name, 'templates')
        if os.path.isdir(template_dir):
            template_dirs.add(template_dir)
    return template_dirs


def templates():
    templates = []
    for directory in template_dirs():
        templates.extend([os.path.join(directory, filename)
                          for filename in os.listdir(directory)
                          if filename.endswith('.html')])
    return templates


def main(args=sys.argv[1:]):

    # comman line option parser
    description = 'list available templates'
    parser = OptionParser(description=description)
    options, args = parser.parse_args(args)

    # list templates
    for template in templates():
        print template


if __name__ == '__main__':
    main()
