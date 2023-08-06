#!/usr/bin/python

from __future__ import print_function
import sys
import argparse
import os
import json # the bookmark file is json serialized


# debug use
# import ipdb

CURDIR = os.getcwd()
BM_PATH=os.path.expanduser('~/.brownfox')
BM_JSON = None

def _load_data():
    global BM_JSON
    # be a little bit cautious
    if not os.path.isfile(BM_PATH) or os.path.getsize(BM_PATH) == 0:
        BM_JSON = {}
    else:
        with open(BM_PATH) as fd:
            try:
                BM_JSON = json.load(fd)
            except ValueError as e:
                print("CANNOT_LOAD_JSON: ", e, file=sys.stderr)
                sys.exit(1)

_list_all = object()
OPTIONS = {
        ("save", "-s"): {
            "help": "bookmark the current directory",
            },
        ("delete", "-d"): {
            "help": "delete the bookmark entry",
            "nargs": '*',
            },
        ("list", "-l"): {
            "help": "list all bookmark entries. if specified, list the path of that bookmark.",
            "nargs": '?',
            "const": _list_all, # another dirty hack
            },
        ("jump", "jump"): {
            "help": "jump to the destination directory",
            "nargs": "?",
            }
        }

def _init_parser():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    for name, opt in OPTIONS.iteritems():
        # what the heck we must specify a positional argument
        group.add_argument(name[-1], **opt)
    return parser

def parse():
    p = _init_parser()
    args = p.parse_args()
    for name, opt in OPTIONS.iteritems():
        # XXX it's dirty here.
        val = getattr(args, name[-1].lstrip('-'))
        if val is not None:
            globals()["do_"+name[0]](val)
            break

def do_save(name, *args, **kwargs):
    if name in BM_JSON:
        nprint(name=name, path=BM_JSON[name], type_=1)
    else:
        BM_JSON[name] = CURDIR
        writeback()

def do_delete(name, *args, **kwargs):
    if isinstance(name, (list, tuple)):
        for name_ in name:
            if name_ in BM_JSON:
                del BM_JSON[name_]
    elif isinstance(name, basestring):
        if name in BM_JSON:
            del BM_JSON[name]
    writeback()

def do_list(name, *args, **kwargs):
    if name == _list_all:
        # list all bookmarks
        nprint(type_=2)
    else:
        nprint(type_=1, name=name)

def do_jump(name, *args, **kwargs):
    if name in BM_JSON:
        print(BM_JSON[name])
    else:
        print("")

def writeback():
    with open(BM_PATH, 'w') as fd:
        json.dump(BM_JSON, fd)

def nprint(type_=2, name="", *args, **kwargs):
    """
    short for nice-print, not no-print. :-)
    @type_: 1: bookmark already exists
            2: list all bookmarks
    
    """
    if type_ == 2:
        print(" ".join(name_ for name_ in BM_JSON))
    elif type_ == 1:
        print(BM_JSON.get(name, ""))


def main():
    _load_data()
    parse()

if __name__ == "__main__":
    main()

