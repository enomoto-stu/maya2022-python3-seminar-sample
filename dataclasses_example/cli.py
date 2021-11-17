#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import dataclasses
import json
import sys


@dataclasses.dataclass(frozen=True)
class MyDataClass(object):
    id: int
    name: str = u"Enomoto"
    language: str = dataclasses.field(default="Python", init=False)


def main():
    # type: () -> int
    u"""メイン関数"""
    my_dataclass = MyDataClass(0)

    print(my_dataclass)

    # dataclasses.FrozenInstanceError
    # my_dataclass.language = u"JavaScript"

    _dict = dataclasses.asdict(my_dataclass)
    print(type(_dict))
    print(json.dumps(_dict, indent=2))
    print()

    _tuple = dataclasses.astuple(my_dataclass)
    print(type(_tuple))
    print(json.dumps(_tuple, indent=2))

    return 0


if __name__ == u"__main__":
    sys.exit(main())
