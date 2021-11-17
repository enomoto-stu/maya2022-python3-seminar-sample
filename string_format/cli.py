#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import math
import sys


def main():
    greetings = u"Hello"
    name = u"STU"
    print(u"%s %s!" % (greetings, name))
    print(u"{0} {1}!".format(greetings, name))
    print(f"{greetings} {name}!")
    print()

    print(u"pi = %.4f" % math.pi)
    print(u"pi = {0:.4f}".format(math.pi))
    print(f"pi = {math.pi:.4f}")
    print()

    answer = 42
    print(u"answer is %04d" % answer)
    print(u"answer is {0:04d}".format(answer))
    print(f"answer is {answer:04d}")
    print()

    text = u"centering!"
    # print(u"%^20s" % text)  # 対応していない
    print(u"{0:^20s}".format(text))
    print(f"{text:^20s}")

    return 0


if __name__ == u"__main__":
    sys.exit(main())
