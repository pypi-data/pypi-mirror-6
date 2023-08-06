#!/usr/bin/env python
# encoding: utf-8

from __future__ import division, absolute_import, print_function, unicode_literals

import argparse
import difflib
import os
import shutil
import sys
import subprocess


class Test(object):
    def __init__(self, name, executable):
        self.name = name
        self.executable = executable
        self.input_dir = os.path.join(self.name, "input")
        self.output_dir = os.path.join(self.name, "output")
        self.expected_dir = os.path.join(self.name, "expected")


    def build(self):
        ok = True
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.mkdir(self.output_dir)

        for name in os.listdir(self.input_dir):
            if not name.endswith(".qml"):
                continue
            out_path = os.path.join(self.output_dir, name + ".cpp")
            with open(out_path, "w") as out:
                ret = subprocess.call(
                    [self.executable, name],
                    stdout=out,
                    cwd=self.input_dir)
                if ret != 0:
                    self.error("doxyqml failed on {}".format(name))
                    ok = False
        return ok


    def update(self):
        if os.path.exists(self.expected_dir):
            shutil.rmtree(self.expected_dir)
        shutil.copytree(self.output_dir, self.expected_dir)


    def compare(self):
        lst = os.listdir(self.expected_dir)
        if not lst:
            self.error("expected_dir '{}' is empty".format(self.expected_dir))
            return False

        ok = True
        for name in lst:
            if name.startswith("."):
                continue
            out_path = os.path.join(self.output_dir, name)
            if not os.path.exists(out_path):
                self.error("File {} does not exist".format(out_path))
                ok = False
                continue

            out_lines = open(out_path).readlines()

            expected_path = os.path.join(self.expected_dir, name)
            expected_lines = open(expected_path).readlines()

            delta = difflib.unified_diff(expected_lines, out_lines, fromfile="expected", tofile="output")
            delta_lines = list(delta)
            if delta_lines:
                ok = False
                self.error("Failure on {}".format(name))
                for line in delta_lines:
                    sys.stderr.write(line)
        return ok

    def error(self, msg):
        print("{}: ERROR: {}".format(self.name, msg))


def main():
    script_dir = os.path.dirname(__file__) or "."

    default_doxyqml = os.path.abspath(os.path.join(script_dir, os.pardir, os.pardir, "bin", "doxyqml"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--update",
        help="Update expected output from test ID", metavar="ID")
    parser.add_argument("--doxyqml", default=default_doxyqml,
        help="Path to the doxyqml executable ({})".format(default_doxyqml))
    parser.add_argument("test_id", nargs="?",
        help="Run specified test only")
    args = parser.parse_args()

    executable = os.path.abspath(args.doxyqml)

    os.chdir(script_dir)

    if args.update:
        print("Updating {}...".format(args.update))
        test = Test(args.update, executable)
        if not test.build():
            return 1
        test.update()
        return 0

    if args.test_id:
        if not os.path.isdir(args.test_id):
            parser.error("Invalid test id '{}'".format(args.test_id))
        test_list = [args.test_id]
    else:
        test_list = [x for x in os.listdir(".") if os.path.isdir(x)]

    errors = 0
    for test_dir in test_list:
        print("Testing {}...".format(test_dir))
        test = Test(test_dir, executable)
        if not (test.build() and test.compare()):
            errors += 1
            continue

    print("")
    if errors:
        print("Failure: {} errors".format(errors))
        return 1
    else:
        print("Success")
        return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
