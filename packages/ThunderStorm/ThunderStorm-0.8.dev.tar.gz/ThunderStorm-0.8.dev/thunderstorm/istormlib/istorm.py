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

"""
Created on Thu Mar 14 10:12:56 2013

@author: dtremoui
"""

import os

from matplotlib.pyplot import figure
import h5py

from .storm import Storm
from .istorm_view import View
from ..thunder.importers.tools import plug_dict

from ..lightning.simple_plots import (TLPOverlayWithLeakEvol, TLPOverlay)


class InteractiveStorm(object):

    def __init__(self, storm=None):
        if storm is None:
            #TODO create a tmp file if None
            #self.storm = Storm()
            raise NotImplementedError
        elif type(storm) is str:
            if not os.path.exists(storm):
                h5py.File(storm, 'w')
            self.storm = Storm(storm)
        else:
            self.storm = storm

        for importer_name in plug_dict.keys():
            importer = plug_dict[importer_name]()
            setattr(self, 'import_' + importer_name,
                    self._gen_import_data(importer))

    def _gen_import_data(self, importer):
        def import_func(filename, comments=""):
            self.storm.append(View(importer.load(filename, comments,
                                                 h5file=self.storm._h5file)))
        return import_func

    @property
    def filename(self):
        return self.storm._h5file.filename

    def __repr__(self):
        if len(self.storm) == 0:
            return "Empty"
        showtxt = "Storm name: %s\n" % self.filename
        for idx, elem in enumerate(self.storm):
            showtxt += "%s : %s" % (idx, elem)
        return showtxt

    def overlay_raw_tlp(self, index_list, experiment_list=(),
                        withleakevol=True):
        if withleakevol:
            self.overlay_tlp_fig = TLPOverlayWithLeakEvol(figure())
        else:
            self.overlay_tlp_fig = TLPOverlay(figure())

        self.storm.overlay_raw_tlp(self.overlay_tlp_fig,
                                   index_list, experiment_list)
        return self.overlay_tlp_fig
