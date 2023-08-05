# -*- coding: utf-8 -*-
#
#   mete0r.recipe.whoami : a zc.buildout recipe to know whoami
#   Copyright (C) 2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This file is part of mete0r.recipe.whoami.
#
#   mete0r.recipe.whoami is free software: you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public License as
#   published by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
#
#   mete0r.recipe.whoami is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#   License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
from distutils.spawn import find_executable

try:
    from subprocess import check_output
except ImportError:
    raise NotImplementedError('subprocess:check_output')


ITEM_OPT_MAP = {
    'user': 'un',
    'user-id': 'u',
    'group': 'gn',
    'group-id': 'g',
    'real-user': 'unr',
    'real-user-id': 'ur',
    'real-group': 'gnr',
    'real-group-id': 'gr',
}


id_executable = find_executable('id')


def get(item):
    if not id_executable:
        return None

    opt = ITEM_OPT_MAP[item]
    stdout = check_output([id_executable, '-' + opt])
    return stdout.strip()


class Recipe:

    def __init__(self, buildout, name, options):
        for item in ITEM_OPT_MAP.keys():
            options[item] = get(item)

    def install(self):
        return []

    def update(self):
        pass
