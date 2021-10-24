#!/usr/local/bin/python3

import sys
import os
import argparse
import unittest

from engine.fast_engine import is_valid_name
from engine import fast_engine

STORAGE = "{}/.fl_storage".format(os.path.expanduser("~"))

def improve_args(arglist):
    result_args = arglist
    argvs = arglist[1:]
    if len(argvs) == 0:
        result_args = [arglist[0], 'list']
    elif len(argvs) == 1:
        if argvs[0] not in ["add", "rm", "view", "update"]:
            result_args = [arglist[0], "view", argvs[0]]

    return result_args


def _format_entry(fl_dict, key):
    tags = ''
    if "tags" in fl_dict[key]:
        tags = ','.join(fl_dict[key]["tags"])
    return '{} |{}| -> {}'.format(key.ljust(15), tags.ljust(20), fl_dict[key]["link"])


def list_all(args):
    fl_dict = fast_engine.read(STORAGE)
    for key in sorted(fl_dict.keys()):
        print(_format_entry(fl_dict, key))


def add_fast_link(args):
    fl_dict = fast_engine.read(STORAGE)
    try:
        fl_dict = fast_engine.add_new(fl_dict, args.fast_link, args.link, args.tags)
        fast_engine.save(fl_dict, STORAGE)
    except ValueError as e:
        print(e)


def update_fast_link(args):
    fl_dict = fast_engine.read(STORAGE)
    fl_dict = fast_engine.update(fl_dict, args.fast_link, args.link, args.tags)
    fast_engine.save(fl_dict, STORAGE)


def view_fast_link(args):
    try:
        fl_dict = fast_engine.read(STORAGE)
        result = fast_engine.view(fl_dict, args.fast_link)
        for key in result:
            print(_format_entry(result, key))
    except KeyError as err:
        print(err)
    

def remove_fl(args):
    fl_dict = fast_engine.read(STORAGE)
    if fl_dict.pop(args.fl, None) is None:
        print("fast link '{}' does not exist Hint: try 'fd list' command for a complete list of fast dirs".format(args.fl))
    else:
        print("fast link '{}' was successfully removed".format(args.fl))

    fast_engine.save(fl_dict, STORAGE)


def parse_args():
    sys.argv = improve_args(sys.argv)

    parser = argparse.ArgumentParser(description="Fast Link v.1", prog="fl", allow_abbrev=True)

    subparsers = parser.add_subparsers(help='commands')
    list_parser = subparsers.add_parser('list', help='list fast links')
    list_parser.set_defaults(func=list_all)

    add_parser = subparsers.add_parser('add', help='add a new fast link')
    add_parser.add_argument("fast_link", help="fast link name")
    add_parser.add_argument("link", help="actual link. Must be surrounded by quotes")
    add_parser.add_argument("--tags", help="add comma separated tags")
    add_parser.set_defaults(func=add_fast_link)

    update_parser = subparsers.add_parser('update', help='update existing fast link')
    update_parser.add_argument("fast_link", help="fast link name")
    update_parser.add_argument("--link", help="actual link. Must be surrounded by quotes")
    update_parser.add_argument("--tags", help="add comma separated tags")
    update_parser.set_defaults(func=update_fast_link)

    view_parser = subparsers.add_parser('view', help='view existing fast link')
    view_parser.add_argument("fast_link", help="fast link name")
    view_parser.set_defaults(func=view_fast_link)

    rm_parser = subparsers.add_parser('rm', help='remove a fast link')
    rm_parser.add_argument("fl", help="fast link")
    rm_parser.set_defaults(func=remove_fl)

    args = parser.parse_args()
    args.func(args)

    return None


def main():
    parse_args()


if __name__ == '__main__':
    main()


class TestFastLink(unittest.TestCase):
    def test_is_valid_fast_link_name(self):
        a_fd = "abc123"
        self.assertTrue(is_valid_name(a_fd))
        self.assertFalse(is_valid_name("a!xy"))

    def test_add_new_invalid_source(self):
        with self.assertRaises(ValueError):
            fast_engine.add_new({}, None, 'abc.com', 'x,y')

    def test_add_new(self):
        expected = {'g1': {'link': 'google.com', 'tags': ['abc', 'def']}}
        actual = fast_engine.add_new({}, 'g1', 'google.com', 'abc,def')
        self.assertDictEqual(actual, expected)

    def test_add_new_with_empty_dest(self):
        with self.assertRaises(ValueError):
            fast_engine.add_new({}, 'g1', None, 'abc,def')

    def test_add_new_duplicate(self):
        actual = {'g1': {'link': 'google.com'}}
        with self.assertRaises(ValueError):
            fast_engine.add_new(actual, 'g1', 'abc.com', None)

    def test_update_empty_tags(self):
        expected = {'g1': {'link': 'google.com', 'tags': ['abc', 'def']}}
        actual = fast_engine.update({'g1': {'link': 'google.com'}}, 'g1', 'google.com', 'abc,def')
        self.assertDictEqual(actual, expected)

    def test_update_existing_tags(self):
        expected = {'g1': {'link': 'google.com', 'tags': ['abc', 'def']}}
        actual = fast_engine.update({'g1': {'link': 'google.com', 'tags':['aaa','bbb']}}, 'g1', 'google.com', 'abc,def')
        self.assertDictEqual(actual, expected)

    def test_update_dest(self):
        expected = {'g1': {'link': 'google.com'}}
        actual = fast_engine.update({'g1': {'link': 'abc'}}, 'g1', 'google.com', None)
        self.assertDictEqual(actual, expected)

    def test_update_with_none_dest(self):
        expected = {'g1':{'link':'abc'}}
        actual = fast_engine.update({'g1':{'link':'abc'}}, 'g1', None, None)
        self.assertDictEqual(actual, expected)

    def test_update_inexisting_source(self):
        with self.assertRaises(KeyError):
            fast_engine.update({'g1':{'link':'abc'}}, 'g2', None, 'mmm,xxx')

    def test_view_inexisting_source(self):
        initial = {}
        expected = {}
        self.assertDictEqual(expected, fast_engine.view(initial, 'g1'))

    def test_view_source(self):
        initial = {'g2': {'link':'abc.com'},'g1': {'link':'abc.com'}}
        expected = {'g1': {'link':'abc.com'}}
        self.assertDictEqual(expected, fast_engine.view(initial, 'g1'))
