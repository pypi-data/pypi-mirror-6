#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# multisuite tests many suits in one run
#
# Copyright (C) 2014 DResearch Fahrzeugelektronik GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 3 of the License, or (at your option) any later version.
#

"""
Run test suites independently to allow separate pip requirements for each
suite.

You can check if a directory is a recognisable suite like this::

    $ multisuite issuite path/to/suite_x

You can run a set of test suites like this::

    $ multisuite test suite_1 suite_2 # suite_ prefix not required to write

And if you are in the parent directory of some suites you can run all of them
like this::

    $ multisuite # or explicitely with "multisuite autotest"

"""

import re
import os
import sys
import os.path as op
import subprocess as sub
import argparse


suite_pre = "suite_"
suite_name = re.compile("{}.*".format(suite_pre))
suite_file = "suite.py"
req_file = "requirements.txt"
init_file = "__init__.py"

default_test = """
def test_hi():
    # simple succeeding test
    pass"""

def issuite(path):
    """ checks if a path is a suite

    :param path: the directory that should be checked.
    :return: True if legal suite, otherwise False
    """
    return suite_name.match(op.basename(path)) and \
            op.isfile(op.join(path, suite_file)) and \
            op.isfile(op.join(path, req_file))

def autodiscover(path="."):
    """ find subdirs that are legal suites

    :param path: the directory that should be checked
    :return: list of subdirs of path that are suites
    """
    return [d for d in os.listdir(path) if issuite(d)]

def test(*suite):
    """ run tests for all suites given

    :param suites: the list of suites to be processed.
    :return: a list of test results that contain nosetests returncodes for each
             test
    """
    return [_testone(s) for s in suite]

def autotest(print_summary=True):
    """ find and run all legal suites in the current directory

    :param print_summary: say whether a summary should be printed at the end.
    :return: 0 if all suites ran without errors, otherwise 1
    """
    suites = autodiscover()
    results = test(*suites)
    if print_summary:
        for r,s in zip(results, suites):
            print "suite '{}' {}".format(s, "fail:"+str(r) if r else "ok")
    return _summarize_results(*results)

def makesuite(*name):
    results = []
    for n in name:
        long_name = n if suite_name.match(n) else suite_pre + n
        calls = [
                "mkdir -p {}".format(long_name),
                "touch {}".format(op.join(long_name,req_file)),
                "touch {}".format(op.join(long_name,init_file)),
                "touch {}".format(op.join(long_name,suite_file)),
                "echo \"{}\" >{}".format(default_test, op.join(long_name,suite_file)),
        ]
        results.append(sub.call("; ".join(calls), shell=True))
    return _summarize_results(*results)

def shell_cmd(suite, cmd):
    svenv = "venv" + suite
    calls = [
            "virtualenv " + svenv,
            ". {}/bin/activate".format(svenv),
            "pip install -U nose",
            "pip install -U -r {}/{}".format(suite, req_file),
            cmd,
    ]
    return sub.call("; ".join(calls), shell=True)


def _summarize_results(*results):
    """ take a list of returncodes and decide if success or not

    :param results: the list of results to be parsed
    :return: 0 if all results are 0, otherwise 1
    """
    return 0 if sum(results)==0 else 1

def _testone(suite):
    """ test a given suite

    :param suite: the corresponding suite directory. Correctness can be checked
                  with `issuite` first
    :return: returncode from nosetests
    """
    return shell_cmd(suite, "nosetests {}.suite".format(suite))

def _parse_suitename(suite):
    """ Make sure a suite name is a suite name

    by adding the prefix "suite_" if it is not set by the user.

    :param suite: the name of a suite, with or without the "suite_" prefix

    :return: the name of the suite, with the "suite_" prefix.
    """
    return suite if suite_name.match(suite) else "suite_" + suite


def main():
    parser = argparse.ArgumentParser(
            description="test suites with different requirements together")

    subparser = parser.add_subparsers(dest="cmd")

    # autotest parser
    parser_autotest = subparser.add_parser("autotest",
            help="find and execute all testsuites")
    parser_autotest.add_argument("-ns", "--no-summary", action="store_false",
            help="don't print a summary at the end")

    # test parser
    parser_test = subparser.add_parser("test",
            help="run tests for a list of suites",)
    parser_test.add_argument("suite", nargs="*",
            help="the suites that should be tested; should have module path format not directory format",)

    # issuite parser
    parser_issuite = subparser.add_parser("issuite",
            help="checks wether a directory can be understood as suite",)
    parser_issuite.add_argument("-p", "--path",
            help="the path that should be checked",)

    # autodiscover parser
    parser_autodisc = subparser.add_parser("list",
            help="lists all of the current directories that are suites",)

    # make a suite parser
    parser_make = subparser.add_parser("makesuite",
            help="create a simple default suite",)
    parser_make.add_argument("name", nargs="*",
            help="the name of the suites to be created")

    # shell parser
    parser_shell = subparser.add_parser("shell",
            help="activate a python shell in a suite's environment, for testing and debugging")
    parser_shell.add_argument("suite",
            help="the suite whose environment should be loaded for the shell")

    # finalise arg parsing
    if len(sys.argv) <= 1:
        sys.argv.append("autotest")
    args = parser.parse_args()

    if args.cmd == "autotest":
        #no_summary has store_false so is actually already inverted
        exit(autotest(print_summary=args.no_summary))
    elif args.cmd == "test":
        exit(_summarize_results(*test(map(_parse_suitename, *args.suite))))
    elif args.cmd == "issuite":
        exit(0 if issuite(args.path) else 1)
    elif args.cmd == "list":
        dirs = autodiscover()
        print os.linesep.join(dirs)
        exit(0 if dirs else 1)
    elif args.cmd == "makesuite":
        exit(makesuite(*args.name))
    elif args.cmd == "shell":
        exit(shell_cmd(_parse_suitename(args.suite), "python"))
    else:
        print args

if __name__ == "__main__":
    main()
