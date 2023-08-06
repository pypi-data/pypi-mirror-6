# -*- coding: utf-8 -*-

#  Copyright (c) 2013, ESDAnalysisTools Development Team
#  Copyright (C) 2010 Trémouilles David

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
Simple typical TLP curves plot
"""

import logging

import numpy as np

from .utils import UniversalCursors


class PulsesFigure(object):
    """ Plot all transient curve
    """
    def __init__(self, figure, pulses, title=""):
        time = np.arange(pulses.pulses_length) * pulses.delta_t
        offseted_time = pulses.offsets_t + time[:, np.newaxis]
        offseted_time = offseted_time * 1e9
        # time in nanosecond
        # V curves
        v_pulse_plot = figure.add_subplot(211)
        v_pulse_plot.grid(True)
        v_pulse_plot.set_ylabel("Voltage")
        v_pulse_plot.set_title(title)
        v_pulse_plot.plot(offseted_time, pulses.voltage.T)
        # I curves
        i_pulse_plot = figure.add_subplot(212, sharex=v_pulse_plot)
        i_pulse_plot.grid(True)
        i_pulse_plot.set_xlabel("time (ns)")
        i_pulse_plot.set_ylabel("Current")
        i_pulse_plot.set_title(title)
        i_pulse_plot.plot(offseted_time, pulses.current.T)

        self.v_plot = v_pulse_plot
        self.i_plot = i_pulse_plot
        figure.canvas.draw()


class TLPplot(object):
    def __init__(self, axes, title=""):
        self.title = title
        self.axes = axes
        self.clean()
        self.decorate()
        axes.set_xlim((0, 10))
        axes.set_ylim((0, 5))

    def clean(self):
        axes = self.axes
        axes.cla()
        # Ensure that (0,0) point is always visible on graph
        line, = axes.plot(0, 0)
        line.set_visible(False)

    def decorate(self):
        axes = self.axes
        axes.grid(True)
        axes.set_xlabel("Voltage (V)")
        axes.set_ylabel("Current (A)")
        axes.set_title(self.title)

    def add_curve(self, raw_tlp_data):
        return self.axes.plot(raw_tlp_data.tlp_curve[0],
                              raw_tlp_data.tlp_curve[1], '-o')


class LeakEvolPlot(object):
    def __init__(self, axes):
        self.axes = axes
        self.no_leak_curve_yet = True
        self.clean()
        self.decorate()
        axes.set_xscale('log')
        axes.set_xlim((1e-12, 1e-5))
        axes.xaxis.get_major_locator().numticks = 3

    def clean(self):
        axes = self.axes
        axes.cla()
        # Set x axis
        axes.xaxis.tick_top()
        axes.xaxis.set_label_position('top')
        # Remove y tick labels
        for label in axes.get_yticklabels():
            label.set_visible(False)
        self.no_leak_curve_yet = True

    def decorate(self):
        self.axes.grid(True)

    def add_curve(self, raw_tlp_data, line, tlp_plot_ax):
        if raw_tlp_data.has_leakage_evolution:
            self.axes.semilogx(raw_tlp_data.leak_evol,
                               raw_tlp_data.tlp_curve[1],
                               '%s-o' % line.get_color(),
                               markersize=2)
            self.no_leak_curve_yet = False
        else:
            log = logging.getLogger('thunderstorm.lightning')
            log.warn("Leakage evolution cannot be plotted, no data")
            # Need to update y bound of leak plot if no leakage data
            # for proper autoscaling
            tlp_plot_ax.relim()
            lim_tlp = tlp_plot_ax.dataLim
            lim_leak = self.axes.dataLim
            if self.no_leak_curve_yet is True:
                self.axes.set_xscale('log')
                lim_leak_interval = np.array([1e-12, 1e-5])
            else:
                lim_leak_interval = lim_leak.intervalx
            lim_leak.update_from_data_xy(list(zip(lim_leak_interval,
                                                  lim_tlp.intervaly)))


class TLPOverlay(object):
    """ A tool to visualize overlay of TLP I-V curves
    """
    def __init__(self, figure, title=""):
        self.tlp_plot = TLPplot(figure.add_subplot(111), title=title)
        self.title = title
        self.figure = figure
        self.figure.canvas.draw()

    def clean(self):
        self.tlp_plot.clean()

    def decorate(self):
        self.tlp_plot.decorate()

    def add_curve(self, raw_tlp_data):
        self.tlp_plot.add_curve(raw_tlp_data)
        self.figure.canvas.draw()


class TLPOverlayWithLeakEvol(object):
    """ A tool to visualize overlay of TLP I-V curves
    """
    def __init__(self, figure, title=""):
        self.title = title
        self.figure = figure
        self.tlp_plot = TLPplot(figure.add_axes([0.1, 0.1, 0.64, 0.8]),
                                title=title)
        self.lke_plot = LeakEvolPlot(figure.add_axes([0.75, 0.1, 0.20, 0.8],
                                     sharey=self.tlp_plot.axes))
        self.cursors = UniversalCursors()
        self.add_cursors()
        self.figure.canvas.draw()

    def add_cursors(self):
        self.cursors.add('i', (self.tlp_plot.axes, self.lke_plot.axes),
                         orient='horizontal', lw=1, color='r')
        self.cursors.add('leak', (self.lke_plot.axes, ),
                         orient='vertical', lw=1, color='r')
        self.cursors.add('v', (self.tlp_plot.axes,),
                         orient='vertical', lw=1,
                         color='r')

    def clean(self):
        self.tlp_plot.clean()
        self.lke_plot.clean()

    def decorate(self):
        self.tlp_plot.decorate()
        self.lke_plot.decorate()

    def add_curve(self, raw_tlp_data):
        line, = self.tlp_plot.add_curve(raw_tlp_data)
        self.lke_plot.add_curve(raw_tlp_data, line, self.tlp_plot.axes)
        self.tlp_plot.axes.autoscale_view()
        self.lke_plot.axes.autoscale_view()
        self.lke_plot.axes.xaxis.get_major_locator().numticks = 3
        self.figure.canvas.draw()


class TLPFigure(object):
    """A simple TLP figure
    """
    def __init__(self, figure, tlp_curve_data, title="",
                 leakage_evol=None):
        tlp_plot = figure.add_subplot(111)
        tlp_plot.grid(True)
        tlp_plot.set_xlabel("Voltage (V)")
        tlp_plot.set_ylabel("Current (A)")
        tlp_plot.set_title(title)
        tlp_plot.plot(tlp_curve_data[0], tlp_curve_data[1], '-o')

        if leakage_evol is None:
            log = logging.getLogger('thunderstorm.lightning')
            log.warn("Leakage evolution cannot be plotted, no data")
        else:
            self._leak_evol_with_v = None
            self._leak_evol_with_i = None
            self.leak_evol_state = [True, False, False]
            self.init_leak_evol(tlp_plot, tlp_curve_data, leakage_evol)
            figure.canvas.mpl_connect('key_press_event',
                                      self.on_key_press)
        self.figure = figure
        self.draw = figure.canvas.draw
        self.draw()

    def init_leak_evol(self, tlp_plot, tlp_curve_data, leakage_evol):
        leak_evol_with_v = tlp_plot.twinx()
        leak_evol_with_v.semilogy(tlp_curve_data[0],
                                  np.abs(leakage_evol),
                                  'g-o',
                                  markersize=2)
        leak_evol_with_i = tlp_plot.twiny()
        leak_evol_with_i.semilogx(np.abs(leakage_evol),
                                  tlp_curve_data[1],
                                  'g-o',
                                  markersize=2)
        leak_evol_with_i.set_navigate(False)
        leak_evol_with_v.set_navigate(False)
        leak_evol_with_v.set_visible(False)
        self.leak_evol_state = [True, False, False]
        self._leak_evol_with_v = leak_evol_with_v
        self._leak_evol_with_i = leak_evol_with_i

    def on_key_press(self, event):
        if event.inaxes:
            if event.key == 'n':
                leak_state = self.leak_evol_state
                leak_state.insert(0, leak_state.pop())
                self._leak_evol_with_i.set_visible(leak_state[0])
                self._leak_evol_with_v.set_visible(leak_state[1])
                self.draw()


class LeakageIVsFigure(object):
    """Plot all leakge-iv data
    """
    def __init__(self, figure, ivs_data, title=""):
        ivs_plot = figure.add_subplot(111)
        ivs_plot.grid(True)
        ivs_plot.set_xlabel("Voltage (V)")
        ivs_plot.set_ylabel("Current (A)")
        ivs_plot.set_title(title)
        ivs_data = np.array(ivs_data)
        ivs_plot.plot(ivs_data[:, 0].T, ivs_data[:, 1].T)
        self.absolute_current_value = False
        figure.canvas.mpl_connect('key_press_event',
                                  self.on_key_press)
        self._ivs_data = ivs_data
        self._ivs_plot = ivs_plot
        self.figure = figure
        self.draw = figure.canvas.draw
        self.draw()

    def on_key_press(self, event):
        if event.inaxes:
            if event.key == 'a':
                ivs_data = self._ivs_data
                self.absolute_current_value = not(self.absolute_current_value)
                if self.absolute_current_value:
                    self._ivs_plot.clear()
                    self._ivs_plot.plot(np.abs(ivs_data[:, 0].T),
                                        np.abs(ivs_data[:, 1].T))
                else:
                    self._ivs_plot.clear()
                    self._ivs_plot.plot(ivs_data[:, 0].T,
                                        ivs_data[:, 1].T)
                self.draw()
