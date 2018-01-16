#from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox


class AxesCanvas(FigureCanvasQTAgg):
    """
    A canvas widget containing a Matplotlib figure and axes, with some
    specialized resizing behavior to guarantee pixel-precise borders
    around the axes.
    """

    def __init__(
        self, fixed_width = None, fixed_height = None,
        padding_left = 0, padding_right = 0,
        padding_above = 0, padding_below = 0):

        self.padding_left = padding_left
        self.padding_right = padding_right
        self.padding_above = padding_above
        self.padding_below = padding_below

        # Get standard background color
        bgcolor = QApplication.palette().color(QPalette.Normal, QPalette.Window)
        bgcolor = [bgcolor.redF(), bgcolor.greenF(), bgcolor.blueF()]

        # Create a MatPlotLib figure to plot on
        self.figure = plt.figure(edgecolor=bgcolor, facecolor=bgcolor)

        # Create axes inside the figure
        self.axes = self.figure.add_axes([0, 0, 1, 1])

        # Call parent constructor
        FigureCanvasQTAgg.__init__(self, self.figure)

        # Define resize policy
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding)

        # If requested, set the canvas to a fixed width
        if fixed_width != None:
            self.setMinimumWidth(fixed_width)
            self.setMaximumWidth(fixed_width)
            policy = self.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Fixed)
            self.setSizePolicy(policy)

        # If requested, set the canvas to a fixed height
        if fixed_height != None:
            self.setMinimumHeight(fixed_height)
            self.setMaximumHeight(fixed_height)
            policy = self.sizePolicy()
            policy.setVerticalPolicy(QSizePolicy.Fixed)
            self.setSizePolicy(policy)

        # notify the system of updated policy
        self.updateGeometry()

    def sizeHint(self):
        return QSize(150,150)

    def resizeEvent(self, event):
        # Call the parent class resize event.
        FigureCanvasQTAgg.resizeEvent(self, event)

        # Set new bounding box with the requested padding (in pixels)
        pos = Bbox.from_bounds(0,0,1,1)
        pos = pos.transformed(self.figure.transFigure)
        pos.x0 = self.padding_left
        pos.y0 = self.padding_below
        pos.x1 -= self.padding_right
        pos.y1 -= self.padding_above
        pos = pos.inverse_transformed(self.figure.transFigure)
        self.axes.set_position(pos)
