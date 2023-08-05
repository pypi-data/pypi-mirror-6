# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Copyright (c) 2013, Mathijs Dumon
# All rights reserved.
# Complete license can be found in the LICENSE file.

from pyxrd.gtkmvc.model import Signal

import numpy as np
from scipy import stats
from scipy.interpolate import interp1d

from pyxrd.data import settings
from pyxrd.generic.io import unicode_open, storables, Storable
from pyxrd.generic.models import ChildModel, DataModel, PropIntel, MultiProperty
from pyxrd.generic.models.mixins import CSVMixin, ObjectListStoreChildMixin
from pyxrd.generic.peak_detection import multi_peakdetect, score_minerals

class MineralScorer(DataModel):
    # MODEL INTEL:
    __parent_alias__ = 'specimen'
    __model_intel__ = [
        PropIntel(name="matches", data_type=list, has_widget=True),
        PropIntel(name="minerals", data_type=list, has_widget=True),
        PropIntel(name="matches_changed", data_type=object, has_widget=False, storable=False)
    ]

    matches_changed = None

    _matches = None
    def get_matches_value(self):
        return self._matches

    _minerals = None
    def get_minerals_value(self):
        # Load them when accessed for the first time:
        if self._minerals == None:
            self._minerals = list()
            with unicode_open(settings.DATA_REG.get_file_path("MINERALS")) as f:
                mineral = ""
                abbreviation = ""
                position_flag = True
                peaks = []
                for line in f:
                    line = line.replace('\n', '')
                    try:
                        number = float(line)
                        if position_flag:
                            position = number
                        else:
                            intensity = number
                            peaks.append((position, intensity))
                        position_flag = not position_flag
                    except ValueError:
                        if mineral != "":
                            self._minerals.append((mineral, abbreviation, peaks))
                        position_flag = True
                        if len(line) > 25:
                            mineral = line[:24].strip()
                        if len(line) > 49:
                            abbreviation = line[49:].strip()
                        peaks = []
        sorted(self._minerals, key=lambda mineral:mineral[0])
        return self._minerals

    # ------------------------------------------------------------
    #      Initialisation and other internals
    # ------------------------------------------------------------
    def __init__(self, marker_peaks=[], *args, **kwargs):
        super(MineralScorer, self).__init__(*args, **kwargs)
        self._matches = []
        self.matches_changed = Signal()

        self.marker_peaks = marker_peaks # position, intensity

    # ------------------------------------------------------------
    #      Methods & Functions
    # ------------------------------------------------------------
    def auto_match(self):
        self._matches = score_minerals(self.marker_peaks, self.minerals)
        self.matches_changed.emit()

    def del_match(self, index):
        if self.matches:
            del self.matches[index]
            self.matches_changed.emit()

    def add_match(self, name, abbreviation, peaks):
        matches = score_minerals(self.marker_peaks, [(name, abbreviation, peaks)])
        if len(matches):
            name, abbreviation, peaks, matches, score = matches[0]
        else:
            matches, score = [], 0.
        self.matches.append([name, abbreviation, peaks, matches, score])
        sorted(self._matches, key=lambda match: match[-1], reverse=True)
        self.matches_changed.emit()

    pass # end of class

class ThresholdSelector(ChildModel):

    # MODEL INTEL:
    __parent_alias__ = 'specimen'
    __model_intel__ = [ # TODO add labels
        PropIntel(name="pattern", data_type=str, storable=True, has_widget=True, widget_type="combo"),
        PropIntel(name="max_threshold", data_type=float, storable=True, has_widget=True, widget_type="float_entry"),
        PropIntel(name="steps", data_type=int, storable=True, has_widget=True),
        PropIntel(name="sel_threshold", data_type=float, storable=True, has_widget=True, widget_type="float_entry"),
        PropIntel(name="sel_num_peaks", data_type=int, storable=True, has_widget=True, widget_type="label"),
        PropIntel(name="threshold_plot_data", data_type=object, storable=True),
    ]

    # PROPERTIES:
    pattern = MultiProperty(
        "exp",
        lambda i: i,
        lambda self, p, v: self.update_threshold_plot_data(),
        { "exp": "Experimental Pattern", "calc": "Calculated Pattern" }
    )

    _max_threshold = 0.32
    def get_max_threshold_value(self): return self._max_threshold
    def set_max_threshold_value(self, value):
        value = min(max(0, float(value)), 1) # set some bounds
        if value != self._max_threshold:
            self._max_threshold = value
            self.update_threshold_plot_data()

    _steps = 20
    def get_steps_value(self): return self._steps
    def set_steps_value(self, value):
        value = min(max(3, value), 50) # set some bounds
        if value != self._steps:
            self._steps = value
            self.update_threshold_plot_data()

    _sel_threshold = 0.1
    sel_num_peaks = 0
    def get_sel_threshold_value(self): return self._sel_threshold
    def set_sel_threshold_value(self, value):
        if value != self._sel_threshold:
            self._sel_threshold = value
            if self._sel_threshold >= self.threshold_plot_data[0][-1]:
                self.sel_num_peaks = self.threshold_plot_data[1][-1]
            elif self._sel_threshold <= self.threshold_plot_data[0][0]:
                self.sel_num_peaks = self.threshold_plot_data[1][0]
            else:
                self.sel_num_peaks = int(interp1d(*self.threshold_plot_data)(self._sel_threshold))

    threshold_plot_data = None

    # ------------------------------------------------------------
    #      Initialisation and other internals
    # ------------------------------------------------------------
    def __init__(self, **kwargs):
        super(ThresholdSelector, self).__init__(self, **kwargs)

        self.max_threshold = self.get_kwarg(kwargs, self.max_threshold, "max_threshold")
        self.steps = self.get_kwarg(kwargs, self.steps, "steps")
        self.sel_threshold = self.get_kwarg(kwargs, self.sel_threshold, "sel_threshold")

        if self.parent.experimental_pattern.size > 0:
            self.pattern = "exp"
        else:
            self.pattern = "calc"

        # self.update_threshold_plot_data()

    # ------------------------------------------------------------
    #      Methods & Functions
    # ------------------------------------------------------------
    def get_xy(self):
        if self._pattern == "exp":
            data_x, data_y = self.parent.experimental_pattern.xy_store.get_raw_model_data()
        elif self._pattern == "calc":
            data_x, data_y = self.parent.calculated_pattern.xy_store.get_raw_model_data()
        if data_y.size > 0:
            data_y = data_y / np.max(data_y)
        return data_x, data_y

    def update_threshold_plot_data(self):
        if self.parent is not None:
            data_x, data_y = self.get_xy()
            length = data_x.size

            if length > 2:

                def calculate_deltas_for(max_threshold, steps):
                    resolution = length / (data_x[-1] - data_x[0])
                    delta_angle = 0.05
                    window = int(delta_angle * resolution)
                    window += (window % 2) * 2

                    steps = max(steps, 2) - 1
                    factor = max_threshold / steps

                    deltas = [i * factor for i in range(0, steps)]

                    numpeaks = []
                    maxtabs, mintabs = multi_peakdetect(data_y, data_x, 5, deltas)
                    for maxtab, mintab in zip(maxtabs, mintabs):
                        numpeak = len(maxtab)
                        numpeaks.append(numpeak)
                    numpeaks = map(float, numpeaks)

                    return deltas, numpeaks

                # update plot:
                deltas, numpeaks = calculate_deltas_for(self.max_threshold, self.steps)
                self.threshold_plot_data = deltas, numpeaks

                # update auto selected threshold:

                # METHOD 1:
                #  Fit several lines with increasing number of points from the
                #  generated threshold / marker count graph. Stop when the
                #  R-coefficiënt drops below 0.95 (past linear increase from noise)
                #  Then repeat this by increasing the resolution of data points
                #  and continue until the result does not change anymore

                last_solution = None
                solution = False
                max_iters = 10
                itercount = 0
                delta_x = None
                while not solution:
                    ln = 4
                    max_ln = len(deltas)
                    stop = False
                    while not stop:
                        x = deltas[0:ln]
                        y = numpeaks[0:ln]
                        slope, intercept, R, p_value, std_err = stats.linregress(x, y)
                        ln += 1
                        if abs(R) < 0.98 or ln >= max_ln:
                            stop = True
                        delta_x = -intercept / slope
                    itercount += 1
                    if last_solution:
                        if itercount < max_iters and last_solution - delta_x >= 0.001:
                            deltas, numpeaks = calculate_deltas_for(delta_x[-1], self.steps)
                        else:
                            solution = True
                    last_solution = delta_x

                if delta_x:
                    self.sel_threshold = delta_x
    pass # end of class


def get_inherit_attribute_pair(name, inherit_name, levels=1, parent_prefix="display_marker", signal=None):
    def get_inherit_attribute_value(self):
        return getattr(self, "_%s" % inherit_name)
    def set_inherit_attribute_value(self, value):
        setattr(self, "_%s" % inherit_name, bool(value))
        if getattr(self, signal, None) is not None: getattr(self, signal, None).emit()

    def get_attribute_value(self):
        if getattr(self, inherit_name, False) and self.parent is not None and self.parent.parent is not None:
            parent = self.parent
            for level in range(levels - 1):
                parent = parent.parent
            return getattr(parent, "%s_%s" % (parent_prefix, name))
        else:
            return getattr(self, "_%s" % name)
    def set_attribute_value(self, value):
        setattr(self, "_%s" % name, value)
        if getattr(self, signal, None) is not None: getattr(self, signal, None).emit()

    return get_inherit_attribute_value, set_inherit_attribute_value, get_attribute_value, set_attribute_value

@storables.register()
class Marker(DataModel, Storable, ObjectListStoreChildMixin, CSVMixin):

    # MODEL INTEL:
    __parent_alias__ = 'specimen'
    __model_intel__ = [ # TODO add labels
        PropIntel(name="label", data_type=unicode, storable=True, has_widget=True, is_column=True),
        PropIntel(name="visible", data_type=bool, storable=True, has_widget=True, is_column=True),
        PropIntel(name="position", data_type=float, storable=True, has_widget=True, widget_type="float_entry"),
        PropIntel(name="x_offset", data_type=float, storable=True, has_widget=True, widget_type="float_entry"),
        PropIntel(name="y_offset", data_type=float, storable=True, has_widget=True, widget_type="float_entry"),
        PropIntel(name="align", data_type=str, storable=True, has_widget=True, inh_name="inherit_align", widget_type="combo"),
        PropIntel(name="inherit_align", data_type=bool, storable=True, has_widget=True),
        PropIntel(name="color", data_type=str, storable=True, has_widget=True, inh_name="inherit_color", widget_type="color"),
        PropIntel(name="inherit_color", data_type=bool, storable=True, has_widget=True),
        PropIntel(name="base", data_type=int, storable=True, has_widget=True, inh_name="inherit_base", widget_type="combo"),
        PropIntel(name="inherit_base", data_type=bool, storable=True, has_widget=True),
        PropIntel(name="top", data_type=int, storable=True, has_widget=True, inh_name="inherit_top", widget_type="combo"),
        PropIntel(name="inherit_top", data_type=bool, storable=True, has_widget=True),
        PropIntel(name="top_offset", data_type=float, storable=True, has_widget=True, inh_name="inherit_top_offset", widget_type="float_entry"),
        PropIntel(name="inherit_top_offset", data_type=bool, storable=True, has_widget=True),
        PropIntel(name="angle", data_type=float, storable=True, has_widget=True, inh_name="inherit_angle", widget_type="float_entry"),
        PropIntel(name="inherit_angle", data_type=bool, storable=True, has_widget=True),
        PropIntel(name="style", data_type=str, storable=True, has_widget=True, inh_name="inherit_style", widget_type="combo"),
        PropIntel(name="inherit_style", data_type=bool, storable=True, has_widget=True),
    ]
    __csv_storables__ = [ (prop.name, prop.name) for prop in __model_intel__ ]
    __store_id__ = "Marker"

    # PROPERTIES:
    _label = ""
    def get_label_value(self): return self._label
    def set_label_value(self, value):
        self._label = value
        self.liststore_item_changed()
        self.visuals_changed.emit()

    # Color:
    _color = settings.MARKER_COLOR
    _inherit_color = settings.MARKER_INHERIT_COLOR
    (get_inherit_color_value,
    set_inherit_color_value,
    get_color_value,
    set_color_value) = get_inherit_attribute_pair(
        "color", "inherit_color",
        levels=2, parent_prefix="display_marker", signal="visuals_changed"
    )

    # Angle:
    _angle = settings.MARKER_ANGLE
    _inherit_angle = settings.MARKER_INHERIT_ANGLE
    (get_inherit_angle_value,
    set_inherit_angle_value,
    get_angle_value,
    set_angle_value) = get_inherit_attribute_pair(
        "angle", "inherit_angle",
        levels=2, parent_prefix="display_marker", signal="visuals_changed"
    )

    # Angle:
    _top_offset = settings.MARKER_TOP_OFFSET
    _inherit_top_offset = settings.MARKER_INHERIT_TOP_OFFSET
    (get_inherit_top_offset_value,
    set_inherit_top_offset_value,
    get_top_offset_value,
    set_top_offset_value) = get_inherit_attribute_pair(
        "top_offset", "inherit_top_offset",
        levels=2, parent_prefix="display_marker", signal="visuals_changed"
    )

    # Visible, position, X and Y offset:
    _visible = settings.MARKER_VISIBLE
    _position = settings.MARKER_POSITION
    _x_offset = settings.MARKER_X_OFFSET
    _y_offset = settings.MARKER_Y_OFFSET
    @ChildModel.getter("visible", "position", "x_offset", "y_offset")
    def get_plot_value(self, prop_name):
        return getattr(self, "_%s" % prop_name)
    @ChildModel.setter("visible", "position", "x_offset", "y_offset")
    def set_plot_value(self, prop_name, value):
        setattr(self, "_%s" % prop_name, value)
        self.visuals_changed.emit()

    def cbb_callback(self, prop_name, value):
        self.visuals_changed.emit()

    # Alignment:
    _inherit_align = settings.MARKER_INHERIT_ALIGN
    (get_inherit_align_value,
    set_inherit_align_value,
    get_align_value,
    set_align_value) = get_inherit_attribute_pair(
        "align", "inherit_align",
        levels=2, parent_prefix="display_marker", signal="visuals_changed"
    )
    align = MultiProperty(settings.MARKER_ALIGN, lambda i: i, cbb_callback, {
        "left": "Left align",
        "center": "Centered",
        "right": "Right align"
    })

    # Base connection point:
    _inherit_base = settings.MARKER_INHERIT_BASE
    (get_inherit_base_value,
    set_inherit_base_value,
    get_base_value,
    set_base_value) = get_inherit_attribute_pair(
        "base", "inherit_base",
        levels=2, parent_prefix="display_marker", signal="visuals_changed"
    )
    base = MultiProperty(settings.MARKER_BASE, int, cbb_callback, {
        0: "X-axis",
        1: "Experimental profile",
        2: "Calculated profile",
        3: "Lowest of both",
        4: "Highest of both"
    })

    # Top connection point:
    _inherit_top = settings.MARKER_INHERIT_TOP
    (get_inherit_top_value,
    set_inherit_top_value,
    get_top_value,
    set_top_value) = get_inherit_attribute_pair(
        "top", "inherit_top",
        levels=2, parent_prefix="display_marker", signal="visuals_changed"
    )
    _tops = { 0: "Relative to base", 1: "Top of plot" }
    top = MultiProperty(settings.MARKER_TOP, int, cbb_callback, _tops)

    # Line style:
    _inherit_style = settings.MARKER_INHERIT_STYLE
    (get_inherit_style_value,
    set_inherit_style_value,
    get_style_value,
    set_style_value) = get_inherit_attribute_pair(
        "style", "inherit_style",
        levels=2, parent_prefix="display_marker", signal="visuals_changed"
    )
    style = MultiProperty(settings.MARKER_STYLE, lambda i: i, cbb_callback, {
        "none": "None", "solid": "Solid",
        "dashed": "Dash", "dotted": "Dotted",
        "dashdot": "Dash-Dotted", "offset": "Display at Y-offset"
    })

    # ------------------------------------------------------------
    #      Initialisation and other internals
    # ------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(Marker, self).__init__(*args, **kwargs)

        self.label = self.get_kwarg(kwargs, "", "label", "data_label")
        self.visible = self.get_kwarg(kwargs, True, "visible", "data_visible")
        self.position = float(self.get_kwarg(kwargs, 0.0, "position", "data_position"))
        self.x_offset = float(self.get_kwarg(kwargs, 0.0, "x_offset", "data_x_offset"))
        self.y_offset = float(self.get_kwarg(kwargs, 0.05, "y_offset", "data_y_offset"))
        self.top_offset = float(self.get_kwarg(kwargs, 0.0, "top_offset"))
        self.color = self.get_kwarg(kwargs, settings.MARKER_COLOR, "color", "data_color")
        self.base = int(self.get_kwarg(kwargs, settings.MARKER_BASE, "base", "data_base"))
        self.angle = float(self.get_kwarg(kwargs, 0.0, "angle", "data_angle"))
        self.align = self.get_kwarg(kwargs, settings.MARKER_ALIGN, "align")
        self.style = self.get_kwarg(kwargs, settings.MARKER_STYLE, "style", "data_align")

        # if top is not set and style is not "none",
        # assume top to be "Top of plot", otherwise (style is not "none")
        # assume top to be relative to the base point (using top_offset)
        self.top = int(self.get_kwarg(kwargs, 0 if self.style == "none" else 1, "top"))

        self.inherit_align = self.get_kwarg(kwargs, True, "inherit_align")
        self.inherit_color = self.get_kwarg(kwargs, True, "inherit_color")
        self.inherit_base = self.get_kwarg(kwargs, True, "inherit_base")
        self.inherit_top = self.get_kwarg(kwargs, True, "inherit_top")
        self.inherit_top_offset = self.get_kwarg(kwargs, True, "inherit_top_offset")
        self.inherit_angle = self.get_kwarg(kwargs, True, "inherit_angle")
        self.inherit_style = self.get_kwarg(kwargs, True, "inherit_style")

    # ------------------------------------------------------------
    #      Methods & Functions
    # ------------------------------------------------------------
    def get_nm_position(self):
        if self.parent is not None:
            return self.parent.goniometer.get_nm_from_2t(self.position)
        else:
            return 0.0

    def set_nm_position(self, position):
        if self.parent is not None:
            self.position = self.parent.goniometer.get_2t_from_nm(position)
        else:
            self.position = 0.0

    pass # end of class
