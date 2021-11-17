#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import asyncio
import dataclasses
import math
import os.path
import ssl
import time
from typing import List

import aiohttp
import pymel.core as pm
import requests


def thisdir():
    return os.path.normpath(os.path.abspath(os.path.dirname(__file__)))


ssl_context = ssl.create_default_context(cafile=os.path.join(
    thisdir(),
    u"..",
    u"site-packages",
    u"cp37-cp37m-win_amd64",
    u"certifi",
    u"cacert.pem"
))


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print(u"elapsed time: {0} ms".format(self.msecs))


@dataclasses.dataclass
class WebAPI(object):
    header: dict
    base_url: str
    api_path: str
    query: str


class Model(object):
    name: str
    earth_radius: float = 6378137.0
    base_latitude: float
    base_longitude: float
    max_elevation: float
    step: float
    n: int
    scale: float

    def __init__(
            self,
            name,
            base_latitude=None,
            base_longitude=None,
            min_latitude=None,
            min_longitude=None,
            step=0.01,
            n=160,
            scale=0.01
    ):
        self.name = name
        self.step = step
        self.n = n
        self.scale = scale

        if base_latitude and not min_latitude:
            self.base_latitude = base_latitude
            self.min_latitude: float = base_latitude - step * (n / 2)
            self.max_latitude: float = base_latitude + step * (n / 2)
        elif not base_latitude and min_latitude:
            self.min_latitude: float = min_latitude
            self.max_latitude: float = min_latitude + step * n
            self.base_latitude = (self.max_latitude + min_latitude) / 2
        else:
            raise ValueError

        if base_longitude and not min_longitude:
            self.base_longitude = base_longitude
            self.min_longitude: float = base_longitude - step * (n / 2)
            self.max_longitude: float = base_longitude + step * (n / 2)
        elif not base_longitude and min_longitude:
            self.min_longitude: float = min_longitude
            self.max_longitude: float = min_longitude + step * n
            self.base_longitude = (self.max_longitude + min_longitude) / 2
        else:
            raise ValueError

        self.delta_latitude: float = self.max_latitude - self.min_latitude
        self.delta_longitude: float = self.max_longitude - self.min_longitude

        self.length_along_latitude: float = math.radians(self.delta_latitude) * self.earth_radius
        self.length_along_longitude: float = math.radians(self.delta_longitude) * self.earth_radius


def post_elevation(web_api: WebAPI, payload: dict) -> dict:
    url = f"{web_api.base_url}{web_api.api_path}"
    response = requests.post(url, json=payload, headers=web_api.header)
    return response.json()


def get_payload(model: Model) -> dict:
    payload = {u"locations": []}
    for latitude_index in range(model.n):
        _latitude = model.min_latitude + model.step * latitude_index
        for longitude_index in range(model.n):
            _longitude = model.min_longitude + model.step * longitude_index
            payload[u"locations"].append({
                u"latitude": _latitude,
                u"longitude": _longitude
            })

    return payload


def fetch_points(web_api: WebAPI, model: Model) -> dict:
    payload = get_payload(model)
    return post_elevation(web_api, payload)


async def async_post(url: str, payload: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, ssl=ssl_context) as response:
            return await response.json()


async def async_post_elevation(web_api: WebAPI, payload: dict) -> dict:
    url = f"{web_api.base_url}{web_api.api_path}"
    return await async_post(url, payload)


async def async_fetch_points(web_api: WebAPI, model: Model) -> dict:
    payload = get_payload(model)
    return await async_post_elevation(web_api, payload)


def translate_elevations(
        vertices: List[pm.general.MeshVertex],
        response: dict,
        model: Model,
        sub_model: Model
) -> None:
    for index in range(sub_model.n):
        for column in range(sub_model.n):
            _index = sub_model.n * index + column
            _vertex = vertices[_index]
            _coordinate = _vertex.getPosition(space=u"world")

            _longitude = response[u"results"][_index][u"longitude"]
            _elevation = response[u"results"][_index][u"elevation"]
            _latitude = response[u"results"][_index][u"latitude"]

            _new_coordinate = [
                _coordinate[0],
                _elevation * model.scale,
                _coordinate[2]
            ]
            _vertex.setPosition(_new_coordinate, space=u"world")


def create_sub_mesh(
        web_api: WebAPI,
        model: Model,
        latitude_index: int,
        longitude_index: int,
        mesh_size: int
) -> pm.nodetypes.PolyPlane:
    _name = u"{0}_{1}_{2}".format(model.name, latitude_index, longitude_index)
    _sub_model = Model(
        name=_name,
        min_latitude=model.min_latitude + (mesh_size - 1) * model.step * latitude_index,
        min_longitude=model.min_longitude + (mesh_size - 1) * model.step * longitude_index,
        step=model.step,
        n=mesh_size,
        scale=model.scale
    )
    _sub_area = pm.polyPlane(
        name=_name,
        axis=[0, 1, 0],
        width=_sub_model.length_along_longitude * _sub_model.scale,
        height=_sub_model.length_along_latitude * _sub_model.scale,
        subdivisionsX=_sub_model.n - 1,
        subdivisionsY=_sub_model.n - 1
    )[0]
    _sub_area.translate.set([
        _sub_model.length_along_longitude * longitude_index * _sub_model.scale,
        0,
        -_sub_model.length_along_latitude * latitude_index * _sub_model.scale
    ])

    response = fetch_points(web_api, _sub_model)

    _vertices = _sub_area.vtx
    translate_elevations(_vertices, response, model, _sub_model)

    return _sub_area


async def async_create_sub_mesh(
        web_api: WebAPI,
        model: Model,
        latitude_index: int,
        longitude_index: int,
        mesh_size: int
) -> pm.nodetypes.PolyPlane:
    _name = u"async_{0}_{1}_{2}".format(model.name, latitude_index, longitude_index)
    _sub_model = Model(
        name=_name,
        min_latitude=model.min_latitude + (mesh_size - 1) * model.step * latitude_index,
        min_longitude=model.min_longitude + (mesh_size - 1) * model.step * longitude_index,
        step=model.step,
        n=mesh_size,
        scale=model.scale
    )
    _sub_area = pm.polyPlane(
        name=_name,
        axis=[0, 1, 0],
        width=_sub_model.length_along_longitude * _sub_model.scale,
        height=_sub_model.length_along_latitude * _sub_model.scale,
        subdivisionsX=_sub_model.n - 1,
        subdivisionsY=_sub_model.n - 1
    )[0]
    _sub_area.translate.set([
        _sub_model.length_along_longitude * longitude_index * _sub_model.scale,
        0,
        -_sub_model.length_along_latitude * latitude_index * _sub_model.scale
    ])

    response = await async_fetch_points(web_api, _sub_model)

    _vertices = _sub_area.vtx
    translate_elevations(_vertices, response, model, _sub_model)

    return _sub_area


def main():
    _open_elevation_api = WebAPI(
        header={
            u"Accept": u"application/json",
            u"Content-Type": u"application/json"
        },
        base_url=u"https://api.open-elevation.com",
        api_path=u"/api/v1/lookup",
        query=u"?locations={latitude},{longitude}"
    )
    _mt_fuji_model = Model(
        name=u"mt_fuji",
        base_latitude=35.363,
        base_longitude=138.730,
        step=0.002,
        n=320,
        scale=0.01
    )

    _size = 20
    _section = _mt_fuji_model.n // _size
    sub_areas = []
    for latitude_index in range(_section):
        for longitude_index in range(_section):
            sub_areas.append(create_sub_mesh(
                web_api=_open_elevation_api,
                model=_mt_fuji_model,
                latitude_index=latitude_index,
                longitude_index=longitude_index,
                mesh_size=_size
            ))
    pm.select(sub_areas, replace=True)
    pm.polyAverageNormal(postnormalize=False, distance=0.1, replaceNormalXYZ=(1, 0, 0))
    pm.select(clear=True)

    return 0


async def async_main():
    _open_elevation_api = WebAPI(
        header={
            u"Accept": u"application/json",
            u"Content-Type": u"application/json"
        },
        base_url=u"https://api.open-elevation.com",
        api_path=u"/api/v1/lookup",
        query=u"?locations={latitude},{longitude}"
    )
    _mt_fuji_model = Model(
        name=u"mt_fuji",
        base_latitude=35.363,
        base_longitude=138.730,
        step=0.002,
        n=320,
        scale=0.01
    )

    _size = 20
    _section = _mt_fuji_model.n // _size
    coroutines = []
    for latitude_index in range(_section):
        for longitude_index in range(_section):
            coroutines.append(async_create_sub_mesh(
                web_api=_open_elevation_api,
                model=_mt_fuji_model,
                latitude_index=latitude_index,
                longitude_index=longitude_index,
                mesh_size=_size
            ))
    sub_areas = await asyncio.gather(*coroutines)
    pm.select(sub_areas, replace=True)
    pm.polyAverageNormal(postnormalize=False, distance=0.1, replaceNormalXYZ=(1, 0, 0))
    pm.select(clear=True)

    return 0


def run():
    with Timer(True):
        main()


def async_run():
    with Timer(True):
        asyncio.run(async_main())
