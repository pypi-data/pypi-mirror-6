#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright (c) 2013 ESDAnalysisTools Development Team

#  This file is part of Thunderstorm.
#
#  ThunderStrom is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ThunderStorm is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with ThunderStorm.  If not, see <http://www.gnu.org/licenses/>.

"""Python setup script for ThunderStorm
"""

from distutils.core import setup

from thunderstorm import __version__

setup(name='ThunderStorm',
      version=__version__,
      author='ESDAnalysisTools Development Team',
      author_email='david.trem at gmail.com Dimitri Linten at gmail.com',
      url='http://code.google.com/p/esdanalysistools/',
      license='LGPL',
      platforms=['any'],
      packages=['thunderstorm',
                'thunderstorm.thunder',
                'thunderstorm.thunder.importers',
                'thunderstorm.lightning',
                'thunderstorm.istormlib',
                'thunderstorm.thunder.analysis'],
      package_data={'thunderstorm.thunder': ['ESDAnalysisTool.css']},
      )
