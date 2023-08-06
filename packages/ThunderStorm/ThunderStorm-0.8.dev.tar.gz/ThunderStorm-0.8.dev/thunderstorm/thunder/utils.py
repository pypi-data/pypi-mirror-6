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

import sys
from io import StringIO


def string2file(raw_string):
    """The function return a file like object contaiing the given string.
    """
    filelike = StringIO()
    if sys.version_info[0] < 3:  # Python 2
        filelike.write(unicode(raw_string))
    else:  # Python 3
        filelike.write(raw_string)
    filelike.flush()
    filelike.seek(0)
    return filelike
