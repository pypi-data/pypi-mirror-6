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
from __future__ import with_statement
import os.path


def _readfile(name):
    setup_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(setup_path, name)
    with file(path) as f:
        return f.read()


name = 'mete0r.recipe.whoami'
version = '0.1.dev0'

author = 'mete0r'
author_email = 'mete0r@sarangbang.or.kr'
license = 'GNU Lesser General Public License v3 or later (LGPLv3+)'
url = 'https://github.com/mete0r/recipe.whoami'

description = 'a zc.buildout recipe to know whoami'
long_description = _readfile('README.rst')
classifiers = '''
Development Status :: 3 - Alpha
Environment :: Plugins
Framework :: Buildout :: Recipe
Intended Audience :: Developers
License :: OSI Approved :: GNU Lesser General Public License v3 or later\
 (LGPLv3+)
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2.7
Programming Language :: Python :: Implementation :: CPython
'''.strip().split('\n')
keywords = 'zc.buildout recipe whoami'

packages = {
    'mete0r': '',
    'mete0r.recipe': '',
    'mete0r.recipe.whoami': ''
}
#
# setuptools specific
#
namespace_packages = [
    'mete0r',
    'mete0r.recipe'
]
entry_points = {
    'zc.buildout': 'default=mete0r.recipe.whoami:Recipe'
}
install_requires = [
    'setuptools',
]


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import ez_setup
    ez_setup.use_setuptools()

    from setuptools import setup
    setup(name=name,
          version=version,

          author=author,
          author_email=author_email,
          license=license,
          url=url,

          description=description,
          long_description=long_description,
          classifiers=classifiers,
          keywords=keywords,

          packages=packages,

          #
          # setuptools specific
          #
          namespace_packages=namespace_packages,
          entry_points=entry_points,
          install_requires=install_requires,
          zip_safe=True)


if __name__ == '__main__':
    main()
