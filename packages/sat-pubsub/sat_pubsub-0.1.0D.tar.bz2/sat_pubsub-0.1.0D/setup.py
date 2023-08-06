#!/usr/bin/python
#-*- coding: utf-8 -*-

# Copyright (c) 2003-2011 Ralph Meijer
# Copyright (C) 2011-2014 Jérôme Poisson <goffi@goffi.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This program is based on Idavoll (http://idavoll.ik.nu/),
# originaly written by Ralph Meijer (http://ralphm.net/blog/)
# It is sublicensed under AGPL v3 (or any later version) as allowed
# by the original license.

# Here is a copy of the original license:

# Copyright (c) 2003-2011 Ralph Meijer

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
from setuptools import setup
from sat_pubsub import __version__


# seen here: http://stackoverflow.com/questions/7275295
try:
    from setuptools.command import egg_info
    egg_info.write_toplevel_names
except (ImportError, AttributeError):
    pass
else:
    def _top_level_package(name):
        return name.split('.', 1)[0]

    def _hacked_write_toplevel_names(cmd, basename, filename):
        pkgs = dict.fromkeys(
            [_top_level_package(k)
                for k in cmd.distribution.iter_distribution_names()
                if _top_level_package(k) != "twisted"
            ]
        )
        cmd.write_file("top-level names", filename, '\n'.join(pkgs) + '\n')

    egg_info.write_toplevel_names = _hacked_write_toplevel_names


install_requires = [
    'wokkel >= 0.7.1',
    'simplejson',
]

if sys.version_info < (2, 5):
    install_requires.append('uuid')

setup(name='sat_pubsub',
      version=__version__,
      description=u'XMPP Publish-Subscribe Service Component, build for the need of the « Salut à Toi » project',
      maintainer='Jérôme Poisson',
      maintainer_email='goffi@goffi.org',
      url='http://repos.goffi.org/sat_pubsub',
      license='AGPLv3+',
      packages=[
          'sat_pubsub',
          'sat_pubsub.test',
          'twisted.plugins',
      ],
      package_data={'twisted.plugins': ['twisted/plugins/sat_pubsub.py']},
      data_files=[('share/sat_pubsub', ['db/pubsub.sql', 'doc/examples/sat_pubsub.tac'])],
      zip_safe=False,
      install_requires=install_requires,
)
