# -*- coding: latin-1 -*-

import math
import numpy as np


class AxesLimits:
    """This class encapsulates the x and y limits of an axes."""

    def __init__(self):
        # xmin, xmax, ymin, ymax
        self.limits = np.array([1.0, 1.0, 1.0, 1.0]) * float("NaN")

        # Make sure that upon construction the axes limits seem to have
        # just changed
        self.last_limits = np.array([0.0, 0.0, 0.0, 0.0])

        self.change_forced = False


    def set_limits(self, xmin = None, xmax = None, ymin = None, ymax = None):
        self.last_limits = self.limits.copy()

        if xmin != None:
            self.limits[0] = xmin
        if xmax != None:
            self.limits[1] = xmax
        if ymin != None:
            self.limits[2] = ymin
        if ymax != None:
            self.limits[3] = ymax


    def changed(self):
        """
        Determine whether the limits have changed during the last call to
        set_limits().
        """
        if self.change_forced:
            self.change_forced = False
            return True
        else:
            return not np.array_equal(self.limits, self.last_limits)


    def set_on_axes(self, ax):
        """Sets the current limits on a Matplotlib axes object."""
        ax.set_xlim(self.limits[0], self.limits[1])
        ax.set_ylim(self.limits[2], self.limits[3])


    def force_change(self):
        """Force the next call to changed() to return True."""
        self.change_forced = True
