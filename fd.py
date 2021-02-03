#!/usr/local/bin/python3

import sys
import argparse
import unittest
import json
import os.path
import os


ERRORS = {
    "malformed_fd": "Malformed fast dir file. Hint: check your ~/.fd file"
}


def error(key):
    if key in ERRORS:
        return ERRORS[key]
    else:
        return "Unknown error"


def is_valid_fd(fd):
    return fd.isalnum()


def is_valid_dir(dir_name):
    return os.path.exists(dir_name)


def add_fd(fd_dict, fdir_name, dir_name, replace=False):
    if fdir_name not in fd_dict:
        fd_dict[fdir_name] = dir_name
        print("added {} -> {}".format(fdir_name, dir_name))
    else:
        if replace:
            print("replaced {}: {} with {}: {}".format(fdir_name, fd_dict[fdir_name], fdir_name, dir_name))
            fd_dict[fdir_name] = dir_name
        else:
            print("fast dir {} already exists. Hint: use add -r to overwrite".format(fdir_name))
    return fd_dict


def read_fd():
    filename = "{}/.fd".format(os.path.expanduser("~"))
    if not os.path.isfile(filename):
        with open(filename, 'w') as json_file:
            json.dump({}, json_file)

    with open(filename, "r") as myfile:
        try:
            fd_dict = json.load(myfile)
            return fd_dict
        except Exception as e:
            print(error("malformed_fd"))

    return {}


def save_fd(fd_dict):
    filename = "{}/.fd".format(os.path.expanduser("~"))
    with open(filename, 'w') as json_file:
        json.dump(fd_dict, json_file)


def list_all(args):
    fd_dict = read_fd()
    for key in sorted(fd_dict.keys()):
        print('{} -> {}'.format(key, fd_dict[key]))


def add_fast_dir(args):
    fd_dict = read_fd()
    if is_valid_dir(args.dir):
        fd_dict = add_fd(fd_dict, args.fast_dir, args.dir, args.replace)
        save_fd(fd_dict)
    else:
        print("dir '{}' does not exist, fast dir '{}' was not created".format(args.dir, args.fast_dir))


def go(args):
    fd_dict = read_fd()
    if args.fd in fd_dict:
        if is_valid_dir(fd_dict[args.fd]):
            print('cd {}'.format(fd_dict[args.fd]))
        else:
            print("dir '{}' does not exist => removing fast dir '{}'".format(fd_dict[args.fd], args.fd))
            remove_fd(args)
    else:
        print("Fast dir '{}' does not exist. Hint: try 'fd list' command for a complete list of fast dirs".format(args.fd))


def remove_fd(args):
    fd_dict = read_fd()
    if fd_dict.pop(args.fd, None) is None:
        print("fast dir '{}' does not exist Hint: try 'fd list' command for a complete list of fast dirs".format(args.fd))
    else:
        print("fast dir '{}' was successfully removed".format(args.fd))

    save_fd(fd_dict)


def improve_args(arglist):
    result_args = arglist
    argvs = arglist[1:]
    if len(argvs) == 0:
        result_args = [arglist[0], 'list']
    elif len(argvs) == 1:
        if argvs[0] not in ["add", "list", "go"]:
            result_args = [arglist[0], "go", argvs[0]]

    return result_args


def parse_args():
    sys.argv = improve_args(sys.argv)

    parser = argparse.ArgumentParser(description="Fast Dir v.1", prog="fd", allow_abbrev=True)

    subparsers = parser.add_subparsers(help='commands')
    list_parser = subparsers.add_parser('list', help='list fast dirs')
    list_parser.set_defaults(func=list_all)

    add_parser = subparsers.add_parser('add', help='add a new fast dir')
    add_parser.add_argument("-r", "--replace", action="store_true",
                            help="replaces fast dir if it exist", required=False)
    add_parser.add_argument("fast_dir", help="fast dir name")
    add_parser.add_argument("dir", help="path to dir")
    add_parser.set_defaults(func=add_fast_dir)

    go_parser = subparsers.add_parser('go', help='change dir to fast dir')
    go_parser.add_argument("fd", help="fast dir")
    go_parser.set_defaults(func=go)

    rm_parser = subparsers.add_parser('rm', help='remove a fast dir')
    rm_parser.add_argument("fd", help="fast dir")
    rm_parser.set_defaults(func=remove_fd)

    args = parser.parse_args()
    args.func(args)

    return None


def main():
    parse_args()


if __name__ == '__main__':
    main()


class TestFastDir(unittest.TestCase):
    def test_add_fd_with_replace(self):
        a_fd_d = {
            "mov": "/Users/a_user/Movies"
        }

        expected_fd_d = {
            "mov": "/Users/a_user/Movies",
            "mus": "/Users/a_user/Music"
        }

        self.assertDictEqual(expected_fd_d, add_fd(a_fd_d, "mus", "/Users/a_user/Music", True))

    def test_add_fd_without_replace(self):
        a_fd_d = {
            "mov": "/Users/a_user/Movies"
        }

        expected_fd_d = {
            "mov": "/Users/a_user/Movies",
        }

        self.assertDictEqual(expected_fd_d, add_fd(a_fd_d, "mov", "/Users/a_user2/Music"))

    def test_is_valid_fast_dir_name(self):
        a_fd = "abc123"
        self.assertTrue(is_valid_fd(a_fd))

    def test_is_valid_dir_name(self):
        self.assertFalse(is_valid_dir("abc/de"))
        self.assertTrue(is_valid_dir(os.path.expanduser("~")))

    def test_improve_args(self):
        self.assertEqual(["fd", "-h"], improve_args(["fd"]))
        self.assertEqual(["fd", "go", "abc"], improve_args(["fd", "abc"]))
        self.assertEqual(["fd", "list"], improve_args(["fd", "list"]))
        self.assertEqual(["fd", "add", "a", "b/c"], improve_args(["fd", "add", "a", "b/c"]))
        self.assertEqual(["fd", "go", "a"], improve_args(["fd", "go", "a"]))
        self.assertEqual(["fd", "rm", "abc"], improve_args(["fd", "rm", "abc"]))
