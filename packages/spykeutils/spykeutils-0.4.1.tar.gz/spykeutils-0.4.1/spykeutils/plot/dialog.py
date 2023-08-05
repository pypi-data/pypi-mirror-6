""" Contains a helper class for creating windows containing guiqwt plots.
"""

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QDialog, QGridLayout, QToolBar, QHBoxLayout,
                         QVBoxLayout, QFrame, QWidget)
try:
    from PyQt4 import QtCore
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from PyQt4.QtGui import QColor, QScrollArea, QWidget, QFrame
from guiqwt.baseplot import BasePlot
from guiqwt.curve import CurvePlot
from guiqwt.image import ImagePlot
from guiqwt.plot import PlotManager
from guiqwt.shapes import Marker
from guiqwt.curve import CurveItem
from guiqwt.tools import (SelectTool, RectZoomTool, BasePlotMenuTool,
                          DeleteItemTool, ItemListPanelTool,
                          AntiAliasingTool, AxisScaleTool, DisplayCoordsTool,
                          ExportItemDataTool, ItemCenterTool, SignalStatsTool,
                          ColormapTool, ReverseYAxisTool, AspectRatioTool,
                          ContrastPanelTool, XCSPanelTool, YCSPanelTool,
                          CrossSectionTool, AverageCrossSectionTool,
                          SaveAsTool, PrintTool, CopyToClipboardTool)
from guiqwt.signals import SIG_PLOT_AXIS_CHANGED
from guidata.configtools import get_icon

import icons_rc
import guiqwt_tools


# Monkeypatch curve and image plot so synchronizing axes works with all tools
def fixed_do_zoom_rect_view(self, *args, **kwargs):
    CurvePlot.old_do_zoom_rect_view(self, *args, **kwargs)
    self.emit(SIG_PLOT_AXIS_CHANGED, self)

CurvePlot.old_do_zoom_rect_view = CurvePlot.do_zoom_rect_view
CurvePlot.do_zoom_rect_view = fixed_do_zoom_rect_view


def fixed_do_autoscale(self, *args, **kwargs):
    CurvePlot.old_do_autoscale(self, *args, **kwargs)
    if not isinstance(self, ImagePlot):
        self.emit(SIG_PLOT_AXIS_CHANGED, self)

CurvePlot.old_do_autoscale = CurvePlot.do_autoscale
CurvePlot.do_autoscale = fixed_do_autoscale


def fixed_do_autoscale_image(self, *args, **kwargs):
    ImagePlot.old_do_autoscale(self, *args, **kwargs)
    self.emit(SIG_PLOT_AXIS_CHANGED, self)

ImagePlot.old_do_autoscale = ImagePlot.do_autoscale
ImagePlot.do_autoscale = fixed_do_autoscale_image


class PlotDialog(QDialog, PlotManager):
    """ Implements a dialog to which an arbitrary number of plots can be
    added.

    This class implements a `QDialog` with a number of plots on it. The
    axes of the plots can be arbitrarily synchronized and option checkboxes
    can be added which provide callbacks when the checkbox state changes.

    :param str wintitle: Title of the window.
    :param bool major_grid: Show major grid in plots.
    :param bool minor_grid: Show minor grid in plots.
    :param bool toolbar: Show toolbar.
    :param parent: Parent window.
    :param panels: A list of guiqwt panels to be added to the window.
    :param int min_plot_width: Default minimum width for plots.
    :param int min_plot_height: Default minimum height for plots.
    """

    def __init__(self, wintitle='Plot window', major_grid=True,
                 minor_grid=False, toolbar=True,  parent=None,
                 panels=None, min_plot_width=100, min_plot_height=75):
        QDialog.__init__(self, parent)
        self.setWindowFlags(Qt.Window)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(':/Application/Main')),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.major_grid = major_grid
        self.minor_grid = minor_grid
        self.min_plot_width = min_plot_width
        self.min_plot_height = min_plot_height

        # WidgetMixin copy
        PlotManager.__init__(self, main=self)
        
        self.main_layout = QVBoxLayout(self)
        self.color_layout = QHBoxLayout()
        self.plot_layout = QGridLayout()
        self.plot_layout.setMargin(0)
        self.plot_scroll_widget = QWidget()
        self.plot_scroll_area = QScrollArea()
        self.plot_scroll_area.setFrameShape(QFrame.NoFrame)
        self.plot_scroll_area.setWidgetResizable(True)
        self.option_layout = QHBoxLayout()

        self.plot_widget = None

        if panels is not None:
            for panel in panels:
                self.add_panel(panel)

        self.toolbar = QToolBar('Tools')
        if not toolbar:
            self.toolbar.hide()

        # Configuring widget layout
        self._setup_widget_properties(wintitle=wintitle, icon=icon)
        self._setup_widget_layout()
        
        # Options
        self.option_callbacks = {}
        self.legend = None
        self.axis_syncplots = {}
        
    def _setup_widget_properties(self, wintitle, icon):
        self.setWindowTitle(wintitle)
        if isinstance(icon, basestring):
            icon = get_icon(icon)
        self.setWindowIcon(icon)
        self.setMinimumSize(320, 240)
        self.resize(720, 540)
        
    def _setup_widget_layout(self):
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addLayout(self.color_layout)
        self.main_layout.addWidget(self.plot_scroll_area)
        self.plot_scroll_area.setWidget(self.plot_scroll_widget)
        self.plot_scroll_widget.setLayout(self.plot_layout)
        self.main_layout.addLayout(self.option_layout)
        self.setLayout(self.main_layout)
        
    def add_custom_curve_tools(self, antialiasing=True,
                               activate_zoom=True,
                               signal_stats=False):
        """ Adds typically needed curve tools to the window.

        :param bool antialiasing: Determines if the antialiasing tool is
            added.
        :param bool activate_zoom: Determines if the zoom tool is activated
            initially (otherwise, the selection tool will be activated).
        :param bool signal_stats: Determines if the signal stats tool is
            available.
        """
        self.add_toolbar(self.toolbar)

        t = self.add_tool(SelectTool)
        if not activate_zoom:
            self.set_default_tool(t)
        self.add_tool(BasePlotMenuTool, "item")
        self.add_tool(ExportItemDataTool)
        try:  # Old versions of guiqwt and spyderlib do not support this
            import spyderlib.widgets.objecteditor
            from guiqwt.tools import EditItemDataTool
            self.add_tool(EditItemDataTool)
        except ImportError:
            pass
        self.add_tool(ItemCenterTool)
        self.add_tool(DeleteItemTool)

        self.add_separator_tool()
        t = self.add_tool(RectZoomTool)
        if activate_zoom:
            self.set_default_tool(t)
        self.add_tool(guiqwt_tools.HomeTool)
        self.add_tool(guiqwt_tools.PanTool)

        self.add_separator_tool()
        self.add_tool(BasePlotMenuTool, "grid")
        self.add_tool(BasePlotMenuTool, "axes")
        self.add_tool(DisplayCoordsTool)
        if self.get_itemlist_panel():
            self.add_tool(ItemListPanelTool)

        if signal_stats:
            self.add_separator_tool()
            self.add_tool(SignalStatsTool)

        if antialiasing:
            self.add_tool(AntiAliasingTool)
        self.add_tool(AxisScaleTool)
        self.add_separator_tool()
        self.add_tool(SaveAsTool)
        self.add_tool(CopyToClipboardTool)
        self.add_tool(PrintTool)
        self.add_tool(guiqwt_tools.HelpTool)
        self.add_separator_tool()
        self.get_default_tool().activate()

    def add_custom_image_tools(self, activate_zoom=True):
        """ Adds typically needed image tools to the window.
        """
        self.add_toolbar(self.toolbar)

        t = self.add_tool(SelectTool)
        if not activate_zoom:
            self.set_default_tool(t)
        self.add_tool(BasePlotMenuTool, "item")
        self.add_tool(ExportItemDataTool)
        try:  # Old versions of guiqwt and spyderlib do not support this
            import spyderlib.widgets.objecteditor
            from guiqwt.tools import EditItemDataTool
            self.add_tool(EditItemDataTool)
        except ImportError:
            pass
        self.add_tool(ItemCenterTool)
        self.add_tool(DeleteItemTool)

        self.add_separator_tool()
        t = self.add_tool(RectZoomTool)
        if activate_zoom:
            self.set_default_tool(t)
        self.add_tool(guiqwt_tools.HomeTool)
        self.add_tool(guiqwt_tools.PanTool)

        self.add_separator_tool()
        self.add_tool(BasePlotMenuTool, "grid")
        self.add_tool(BasePlotMenuTool, "axes")
        self.add_tool(DisplayCoordsTool)
        if self.get_itemlist_panel():
            self.add_tool(ItemListPanelTool)

        self.add_separator_tool()
        self.add_tool(ColormapTool)
        self.add_tool(ReverseYAxisTool)
        self.add_tool(AspectRatioTool)
        if self.get_contrast_panel():
            self.add_tool(ContrastPanelTool)
        if self.get_xcs_panel() and self.get_ycs_panel():
            self.add_tool(XCSPanelTool)
            self.add_tool(YCSPanelTool)
            self.add_tool(CrossSectionTool)
            self.add_tool(AverageCrossSectionTool)

        self.add_separator_tool()
        self.add_tool(SaveAsTool)
        self.add_tool(CopyToClipboardTool)
        self.add_tool(PrintTool)
        self.add_tool(guiqwt_tools.HelpTool)
        self.add_separator_tool()
        self.get_default_tool().activate()
    
    def add_option(self, name, change_callback, active=False):
        """ Add an option (using a checkbox) to the window.

        :param str name: The name of the option.
        :param func change_callback: A function accepting the new state as
            a parameter. The function will be called whenever the state
            of the option changes.
        :param bool active: Determines if the option is activated initially.
        """
        checkBox = QtGui.QCheckBox(self)
        checkBox.setChecked(active)
        checkBox.setText(name)
        checkBox.stateChanged.connect(self._option_callback)
        self.option_callbacks[checkBox] = change_callback
        self.option_layout.addWidget(checkBox)

    def add_x_synchronization_option(self, active, ids=None):
        """ Offer an option for X axes synchronization. This method should
        be called after show(), so that a proper initial synchronization
        can be performed.

        :param bool active: Determines whether the axes are synchronized
            initially.
        :param sequence ids: List of plot ids to synchronize.
        """
        self.axis_syncplots[BasePlot.X_BOTTOM] = ids
        if active and ids:
            self.synchronize_axis(BasePlot.X_BOTTOM)
        self.add_option('Synchronize X Axes',
                        PlotDialog._synchronization_option_x, active)

    def add_y_synchronization_option(self, active, ids=None):
        """ Offer an option for Y axes synchronization. This method should
        be called after show(), so that a proper initial synchronization
        can be performed.

        :param bool active: Determines whether the axes are synchronized
            initially
        :param sequence ids: List of plot ids to synchronize.
        """
        self.axis_syncplots[BasePlot.Y_LEFT] = ids
        if active and ids:
            self.synchronize_axis(BasePlot.Y_LEFT)
        self.add_option('Synchronize Y Axes',
                        PlotDialog._synchronization_option_y, active)

    def _synchronization_option_x(self, state):
        """ Callback for x-axis synchronization
        """
        if state:
            self.synchronize_axis(BasePlot.X_BOTTOM)
        else:
            self.unsynchronize_axis(BasePlot.X_BOTTOM)

    def _synchronization_option_y(self, state):
        """ Callback for y-axis synchronization
        """
        if state:
            self.synchronize_axis(BasePlot.Y_LEFT)
        else:
            self.unsynchronize_axis(BasePlot.Y_LEFT)

    def replace_colors(self, replace_list):
        """ Replace colors of items in all plots.

            This can be useful when changing the background color to black
            and black items should be drawn in white:
            ``replace_colors([('#000000', '#ffffff']))``

        :param list replace_list: A list of tuples of Qt color names. The
            first color in each tuple is replaced by the second color.
        """
        for plot in self.plots.itervalues():
            for i in plot.get_items():
                if isinstance(i, CurveItem):
                    pen = i.pen()
                elif isinstance(i, Marker):
                    pen = i.linePen()
                else:
                    continue
                for color in replace_list:
                    c1 = QColor(color[0])
                    c2 = QColor(color[1])
                    if pen.color() != c1:
                        continue
                    pen.setColor(c2)
                    break
                if isinstance(i, CurveItem):
                    i.setPen(pen)
                elif isinstance(i, Marker):
                    i.setLinePen(pen)
            plot.replot()

    def set_background_color(self, color):
        """ Set the background color for all plots.

        :param str color: A Qt color name (e.g. '#ff0000')
        """
        for p in self.plots.itervalues():
            p.setCanvasBackground(QColor(color))
            p.replot()
        
    def add_unit_color(self, color, name='Unit color:'):
        """ Create a small legend on top of the window with only one entry.

        :param str color: A Qt color name (e.g. '#ff0000')
        :param str name: The name of the legend item. It will be displayed
            on the left of the color.
        """
        label = QtGui.QLabel(self)
        label.setText(name)
        label.setAlignment(Qt.AlignRight)
        self.color_layout.addWidget(label)
        label = QtGui.QLabel(self)
        label.setStyleSheet('background-color:' + str(color))
        label.setFrameShape(QFrame.StyledPanel)
        label.setMaximumWidth(80)
        self.color_layout.addWidget(label)

    def add_custom_label(self, legend_string):
        """ Add a label on the right of the plots

        :param str legend_string: An arbitrary string (which can contain
            newlines) to display on the right of the plots
        """
        label = QtGui.QLabel(self)
        label.setText(legend_string)
        self.plot_layout.addWidget(
            label, 0, self.plot_layout.columnCount(), -1, 1)

    def add_color_legend(self, legend, show_option=None):
        """ Create a legend on the right of the plots with colors and names.

        :param sequence legend: List of (color, text) tuples, where `color`
            is a Qt color name (e.g. '#ff0000') and `text` is the
            corresponding text to display in the legend.
        :param bool show_option: Determines whether a toggle for the legend
            will be shown (if the parameter is not ``None``) and if the legend
            is visible initially (``True``/``False``).
        """
        widget = QWidget(self)
        layout = QGridLayout(widget)
        widget.setLayout(layout)
        for l in legend:
            label = QtGui.QLabel(self)
            label.setStyleSheet('background-color:' + str(l[0]))
            label.setFrameShape(QFrame.StyledPanel)
            label.setMaximumWidth(80)
            label.setMaximumHeight(12)
            layout.addWidget(label, layout.rowCount(), 0, 1, 1)
            label = QtGui.QLabel(self)
            label.setText(l[1])
            layout.addWidget(label, layout.rowCount() - 1, 1, 1, 1)

        self.plot_layout.addWidget(
            widget, 0, self.plot_layout.columnCount(), -1, 1)
        if show_option is not None:
            widget.setVisible(show_option)
            self.add_option(
                'Show Legend Sidebar', lambda w, s: widget.setVisible(s),
                show_option)
    
    def add_legend_option(self, legends, active):
        """ Create a user option to show or hide a list of legend objects.

        :param sequence legends: The legend objects affected by the option.
        :param bool active: Determines whether the legends will be visible
            initially.
        """
        self.legends = legends
        self._set_legend_visibility(active)
        self.add_option('Show legend', self._legend_callback, active)
        if active:
            self._set_legend_visibility(True)
        
    def _option_callback(self, state):
        self.option_callbacks[self.sender()](self, state)

    #noinspection PyUnusedLocal
    def _legend_callback(self, win, state):
        self._set_legend_visibility(state > 0)
    
    def _set_legend_visibility(self, visible):
        for p in self.plots.itervalues():
            for l in self.legends:
                p.set_item_visible(l, visible)

    def add_plot_widget(self, plot_widget, plot_id, row=-1, column=0,
                        min_plot_width=None, min_plot_height=None):
        """ Adds a guiqwt plot to the window.

        :param plot_widget: The plot to add.
        :type plot_widget: guiqwt plot widget
        :param int plot_id: The id of the new plot.
        :param int row: The row of the new plot. If this is -1, the new plot
            will be added in a new row (if `column` is 0) or
            in the last row.
        :param int column: The column of the new plot.
        :param int min_plot_width: The minimum width of this plot. If
            ``None``, the default minimum width for this dialog
            is used.
        :param int max_plot_height: The minimum height of this plot. If
            ``None``, the default minimum height for this dialog
            is used.
        """
        if row == -1:
            if column == 0:
                row = self.plot_layout.rowCount()
            else:
                row = self.plot_layout.rowCount() - 1
        pw = min_plot_width
        if pw is None:
            pw = self.min_plot_width
        ph = min_plot_height
        if ph is None:
            ph = self.min_plot_height
        plot_widget.setMinimumSize(pw, ph)
        self.plot_layout.addWidget(plot_widget, row, column)
        new_plot = plot_widget.plot
        self.add_plot(new_plot, plot_id)
        
    def synchronize_axis(self, axis, plots=None):
        if plots is None:
            if axis in self.axis_syncplots:
                plots = self.axis_syncplots[axis]
            else:
                plots = self.plots.keys()
        if len(plots) < 1:
            return

        PlotManager.synchronize_axis(self, axis, plots)

        # Find interval that needs to be shown in order to include all
        # currently shown parts in the synchronized plots
        plot_objects = [self.plots[p] for p in plots]
        lb = min((p.axisScaleDiv(axis).lowerBound() for p in plot_objects))
        ub = max((p.axisScaleDiv(axis).upperBound() for p in plot_objects))
        for p in plot_objects:
            p.setAxisScale(axis, lb, ub)
            p.replot()

    def unsynchronize_axis(self, axis, plots=None):
        if plots is None:
            if axis in self.axis_syncplots:
                plots = self.axis_syncplots[axis]
            else:
                plots = self.plots.keys()
        for plot_id in plots:
            if not plot_id in self.synchronized_plots:
                continue
            synclist = self.synchronized_plots[plot_id]
            for plot2_id in plots:
                if plot_id == plot2_id:
                    continue
                item = (axis, plot2_id)
                if item in synclist:
                    synclist.remove(item)
        
    def plot_axis_changed(self, plot):
        ids = [k for k, p in self.plots.iteritems() if p == plot]
        if len(ids) < 1:
            return
        plot_id = ids[0]
        if plot_id not in self.synchronized_plots:
            return
        for (axis, other_plot_id) in self.synchronized_plots[plot_id]:
            scalediv = plot.axisScaleDiv(axis)
            other = self.get_plot(other_plot_id)
            lb = scalediv.lowerBound()
            ub = scalediv.upperBound()
            other.setAxisScale(axis, lb, ub)
            other.replot()

    def set_plot_title(self, plot, title):
        """ Set the title of a guiqwt plot and use the same font as for the
            rest of the window.

        :param plot: The plot for which the title is set.
        :param str title: The new title of the plot.
        """
        plot.setTitle(title)
        l = plot.titleLabel()
        l.setFont(self.font())
        plot.setTitle(l.text())

    def show(self):
        for p in self.plots.itervalues():
            if not self.minor_grid:
                p.grid.gridparam.min_xenabled = False
                p.grid.gridparam.min_yenabled = False
            if not self.major_grid:
                p.grid.gridparam.maj_xenabled = False
                p.grid.gridparam.maj_yenabled = False
            p.grid.update_params()
        super(PlotDialog, self).show()