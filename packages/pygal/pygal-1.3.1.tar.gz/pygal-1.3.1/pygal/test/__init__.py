# -*- coding: utf-8 -*-
# This file is part of pygal
#
# A python svg graph plotting library
# Copyright © 2012-2014 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pygal. If not, see <http://www.gnu.org/licenses/>.

import pygal
from pygal.util import cut
from datetime import datetime
from pygal.i18n import COUNTRIES
COUNTRY_KEYS = list(COUNTRIES.keys())


def get_data(i):
    return [
        [(-1, 1), (2, 0), (0, 4)],
        [(0, 1), (None, 2), (3, 2)],
        [(-3, 3), (1, 3), (1, 1)],
        [(1, 1), (1, 1), (1, 1)],
        [(3, 2), (2, 1), (1, 1)]][i]


def pytest_generate_tests(metafunc):
    if "Chart" in metafunc.funcargnames:
        metafunc.parametrize("Chart", pygal.CHARTS)
    if "datas" in metafunc.funcargnames:
        metafunc.parametrize(
            "datas",
            [
                [("Serie %d" % i, get_data(i)) for i in range(s)]
                for s in (5, 1, 0)
            ])


def adapt(chart, data):
    if isinstance(chart, pygal.DateY):
        # Convert to a credible datetime
        return list(map(
            lambda t:
            (datetime.fromtimestamp(1360000000 + t[0] * 987654)
             if t[0] is not None else None, t[1]), data))

    if isinstance(chart, pygal.XY):
        return data

    data = cut(data)
    if isinstance(chart, pygal.Worldmap):
        return list(map(lambda x: COUNTRY_KEYS[x % len(COUNTRIES)]
                        if x is not None else None, data))
    return data


def make_data(chart, datas):
    for i, data in enumerate(datas):
        chart.add(data[0],
                  adapt(chart, data[1]),
                  secondary=bool(i % 2))
    return chart
