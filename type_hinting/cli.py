#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import sys
from typing import List, Union


def show_numbers(numbers):
    # type: (Union[List[int], List[float]]) -> None
    u"""数字を表示する

    リスト内の型は全て同じであること
    """
    print(u"-----start-----")
    if all([isinstance(number, int) for number in numbers]):
        for number in numbers:
            print(u"{0:4d}".format(number))
    elif all([isinstance(number, float) for number in numbers]):
        for number in numbers:
            print(u"{0:4.2f}".format(number))
    else:
        raise ValueError
    print(u"-----done-----")
    print()


def python_2_main():
    # type: () -> int
    u"""メイン関数"""
    numbers = [i * 10 for i in range(1, 11)]  # type: List[int]
    show_numbers(numbers)

    return 0


def python_3_main() -> int:
    numbers: List[float] = [i * 0.1 for i in range(1, 11)]
    show_numbers(numbers)

    strings: List[str] = [chr(97 + i) for i in range(10)]
    try:
        show_numbers(strings)
    except ValueError:
        print(u"数値のリストを渡してください")
        return 1

    return 0


if __name__ == u"__main__":
    python_2_main()
    sys.exit(python_3_main())
