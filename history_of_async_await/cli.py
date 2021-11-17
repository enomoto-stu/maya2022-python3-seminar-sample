#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from collections.abc import Generator
import concurrent.futures
import json
import sys


def my_range_list(n):
    # type: (int) -> list[int]
    result = []
    for _index in range(n):
        print(u"adding {0}".format(_index))
        result.append(_index)

    return result


def my_range_generator(n):
    # type: (int) -> Generator[int, None, None]
    for _index in range(n):
        print(u"generating {0}".format(_index))
        yield _index


def iterate_manually():
    # type: () -> None
    u"""nextを用いたイテレーションの例"""
    _generator = my_range_generator(5)
    print(_generator, type(_generator))

    # 0～2
    next(_generator)
    next(_generator)
    next(_generator)

    # 3, 4
    print(u"get {0}".format(next(_generator)))
    print(u"get {0}".format(next(_generator)))

    try:
        # イテレーションの終わりまで来ているため、
        # nextの実行によりStopIteration例外を送出する
        print(u"get {0}".format(next(_generator)))
    except StopIteration:
        print(u"iteration finished")
    print()


def example_of_generator():
    # type: () -> None
    # リストを用いた繰り返し処理
    print(u"run my_range_list")
    for index in my_range_list(5):
        print("get {0}".format(index))
    print()

    # Generatorを用いた繰り返し処理
    print(u"run my_range_generator")
    for index in my_range_generator(5):
        print("get {0}".format(index))
    print()

    print(u"run iterate_manually")
    iterate_manually()


def double_generator():
    # type: () -> Generator[int, int, None]
    print(u"coroutine start")
    while True:
        _value = (yield) * 2
        print(u"received")
        yield _value


def example_of_generator_with_send():
    # type: () -> None
    _coroutine = double_generator()

    for i in [2, 5, 10]:
        next(_coroutine)
        print(u"sending {0}, get {1}".format(i, _coroutine.send(i)))
    print()


def continuation_coroutine(start):
    # type: (int) -> Generator[int, int, None]
    print(u"coroutine start")
    _number = start
    yield _number

    while True:
        delta = yield
        print(u"received incremental {0}".format(delta))
        if delta < 0:
            break
        _number += delta
        yield _number

    print(u"coroutine finished")


def example_of_pep342_coroutine():
    # コルーチンを実行するが、この時点ではまだ何も起きない
    print(u"run continuation_coroutine")
    _coroutine = continuation_coroutine(5)

    # 最初のyieldに到達し、初期値を返す
    initial_number = next(_coroutine)
    print(u"received initial number {0}".format(initial_number))

    # この関数内での処理

    # whileの後のyieldに到達
    next(_coroutine)

    # yieldに値を渡し、次のyieldで値を返す
    number = _coroutine.send(123)
    print(u"number from coroutine {0}".format(number))

    # この関数内での処理

    # whileの後のyieldに到達
    next(_coroutine)

    # yieldに値を渡し、次のyieldで値を返す
    number = _coroutine.send(33)
    print(u"number from coroutine {0}".format(number))

    try:
        # whileの後のyieldに到達
        next(_coroutine)

        # yieldへ渡した値が負のため、whileループを抜けてコルーチンを終了する (StopIteration例外を送出)
        _coroutine.send(-1)
    except StopIteration:
        print(u"coroutine has stopped")

    print(u"program finished")
    print()


def double_concurrent(value):
    return 2 * value


def show_double_concurrent(i):
    _double = double_concurrent(i)
    print(u"sending {0}, get {1}".format(i, _double))

    return _double


def example_of_concurrent_loop_using_multiprocess():
    u"""マルチプロセスによる非同期処理。高速"""
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        _arg_and_futures = []
        for i in [2, 5, 10]:
            _future = executor.submit(show_double_concurrent, i)
            if i == 5:
                _future.cancel()
            _arg_and_futures.append((i, _future))

        for _arg, _future in _arg_and_futures:
            print(u"Argument value: {0}, Running: {1}, Done: {2}, Cancel: {3}".format(
                _arg,
                _future.running(),
                _future.done(),
                _future.cancelled()
            ))
            if not _future.cancelled():
                print(u"{0} -> {1}".format(_arg, _future.result()))
            else:
                print(u"{0} -> Cancelled".format(_arg))
            print()


async def double(value):
    return 2 * value


async def show_double(i):
    print(u"sending {0}, get {1}".format(i, await double(i)))


async def example_of_async_loop():
    _tasks = []
    _loop = asyncio.get_event_loop()
    for i in [2, 5, 10]:
        # # Coroutineを渡すとTaskが返される
        _task = _loop.create_task(show_double(i))

        # # asyncio.ensure_futureにCoroutineを渡すとTaskが返される
        # _task = asyncio.ensure_future(show_double(i))

        # # Coroutineを渡すとTaskが返される(Python3.7以降で動作)
        # _task = asyncio.create_task(show_double(i))

        print(u"number: {0}".format(i))
        print(_task)

        # # asyncio.ensure_futureにTaskを渡すとTaskが返される
        # print(asyncio.ensure_future(_task))
        _tasks.append(_task)

    print()

    print(_tasks)
    print()

    # asyncio.gatherの返り値はFuture
    _future = asyncio.gather(*_tasks)
    print(_future)

    # asyncio.ensure_futureにFutureを渡すとFutureが返される
    print(asyncio.ensure_future(_future))
    print()

    # 以下、コメントアウト部非推奨
    # # Futureにはresultがセットできる
    # _future.set_result((u"hoge", u"fuga", u"piyo"))
    #
    # # resultがセットされていると、doneがTrueを返す
    # if _future.done():
    #     print(u"done.")
    #     print()
    #
    # # resultがセットされたことが表示からわかる
    # print(_future)

    # resultを取り出す
    print(await _future)
    print()


def main():
    # Generatorのおさらい
    example_of_generator()

    # # sendを使ったGeneratorの例
    # example_of_generator_with_send()

    # # Generatorを用いたCoroutineの例
    # example_of_pep342_coroutine()

    # # concurrent.futuresを用いた非同期処理の例
    # example_of_concurrent_loop_using_multiprocess()

    # # asyncioを使用した非同期処理の例(EventLoopを使用した場合)
    # _loop = asyncio.get_event_loop()
    # _loop.run_until_complete(example_of_async_loop())

    # # EventLoopを使用した場合と同様(Python3.7以降で動作)
    # asyncio.run(example_of_async_loop())

    return 0


if __name__ == u"__main__":
    sys.exit(main())
