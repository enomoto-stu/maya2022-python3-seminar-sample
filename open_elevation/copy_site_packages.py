#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function

import argparse
import logging
import os
import shutil
import sys

logger = logging.getLogger(u"stu.dev.deploy.copy_site_packages")

TITLE = u"STU CopySitePackages"
SEM_VERSION = (u"2", u"0", u"0")
TOOL_NAME = u"{0} - v{1}".format(TITLE, u".".join(SEM_VERSION))


class STUException(Exception):
    def __init__(self, message=u""):
        self.message = message

    def __repr__(self):
        return u"{0}: {1}".format(__name__, self.message)


class STUConfigError(STUException):
    pass


class STUOSTypeError(STUException):
    pass


def thisdir():
    return os.path.normpath(os.path.abspath(os.path.dirname(__file__)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        u"-D", u"--debug",
        dest=u"debug",
        action=u"store_true",
        default=False,
        help=u"debug mode."
    )
    parser.add_argument(
        u"--source",
        dest=u"source",
        default=os.path.join(os.path.expanduser(u"~"), u".virtualenvs"),
        help=u"Config file name"
    )
    parser.add_argument(
        u"--dest",
        dest=u"dest",
        default=os.path.join(thisdir(), u"..", u"..", u"site-packages"),
        help=u"Config file name"
    )
    args = parser.parse_args()

    _execute_message = u"EXECUTE {0}".format(TOOL_NAME)
    print(_execute_message)

    source_dir_path = args.source
    dest_dir_path = args.dest

    if not (os.path.exists(source_dir_path) and os.path.isdir(source_dir_path)):
        raise STUException(u"コピー元が存在しません: {0}".format(source_dir_path))

    if os.path.exists(dest_dir_path) and os.path.isdir(dest_dir_path):
        shutil.rmtree(dest_dir_path)

    shutil.copytree(source_dir_path, dest_dir_path)

    return 0


if __name__ == u"__main__":
    sys.exit(main())
