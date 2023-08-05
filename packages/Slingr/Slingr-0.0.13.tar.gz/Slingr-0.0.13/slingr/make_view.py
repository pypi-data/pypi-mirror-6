#!/usr/bin/env python

"""
Create a new view
"""

import os, sys, os.path
import argparse

DESCRIPTION = "Create the directories required for a view"

def get_directory_structure(view_name):
    return {
        view_name: {
            'css': {},
            'html': {},
            'js': {
                'lang': {},
                'views': {},
            },
        }
    }

def make_directory_tree(current_directory, schema, dry_run=False):
    #utils.make_dir(current_directory)
    for subdir_name, subschema in schema.iteritems():
         subdir = os.path.join(current_directory, subdir_name)
         print("Making {0}".format(subdir))
         if not dry_run and not os.path.exists(subdir):
             os.mkdir(subdir)
         make_directory_tree(subdir, subschema, dry_run=dry_run)

def make_view(base_directory, view, args):
    schema = get_directory_structure(view)
    make_directory_tree(base_directory, schema, dry_run=args.dry_run)

def make_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--dry-run', '-n', action='store_true',
        help="Make a dry run.  Do not actually do any work")

    parser.add_argument('--base-directory', '-d',
        help='The base directory to create views.  Default: "%(default)s"', default=os.getcwd())

    parser.add_argument('views', metavar="VIEW", nargs='+', help='Name of a view to create')
    return parser

def run(parser=None, **kwargs):
    parser = make_parser(parser, **kwargs)
    args = parser.parse_args()
    for view in args.views:
        make_view(args.base_directory, view, args)

    return args, parser

if __name__ == '__main__':
    run()
