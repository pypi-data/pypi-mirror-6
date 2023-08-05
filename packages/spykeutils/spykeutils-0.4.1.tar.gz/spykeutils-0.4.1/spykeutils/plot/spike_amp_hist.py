import scipy as sp
import quantities as pq

from guiqwt.plot import BaseImageWidget
from guiqwt.builder import make

from ..progress_indicator import ProgressIndicator
from .. import SpykeException
from ..stationarity import spike_amplitude_histogram as sah
import helper
from dialog import PlotDialog


@helper.needs_qt
def spike_amplitude_histogram(trains, num_bins, uniform_y_scale=True,
                              x_unit=pq.uV, progress=None):
    """ Create a spike amplitude histogram.

    This plot is useful to assess the drift in spike amplitude over a longer
    recording. It shows histograms (one for each `trains` entry, e.g. segment)
    of maximum and minimum spike amplitudes.

    :param list trains: A list of lists of :class:`neo.core.SpikeTrain`
        objects. Each entry of the outer list will be one point on the
        x-axis (they could correspond to segments), all amplitude occurences
        of spikes contained in the inner list will be added up.
    :param int num_bins: Number of bins for the histograms.
    :param bool uniform_y_scale: If True, the histogram for each channel
        will use the same bins. Otherwise, the minimum bin range is computed
        separately for each channel.
    :param Quantity x_unit: Unit of Y-Axis.
    :param progress: Set this parameter to report progress.
    :type progress: :class:`spykeutils.progress_indicator.ProgressIndicator`
    :return:
    """
    if not trains:
        raise SpykeException('No spikes trains for Spike Amplitude Histogram!')
    if not progress:
        progress = ProgressIndicator()

    hist, down, up = sah(trains, num_bins, uniform_y_scale, x_unit, progress)
    num_channels = len(down)

    columns = int(round(sp.sqrt(num_channels)))

    win = PlotDialog(toolbar=True, wintitle="Spike Amplitude Histogram")
    for c in xrange(num_channels):
        pW = BaseImageWidget(
            win, yreverse=False, lock_aspect_ratio=False)
        plot = pW.plot
        img = make.image(sp.log(hist[:, :, c] + 1),
                         ydata=[down[c], up[c]],
                         interpolation='nearest')
        plot.add_item(img)
        plot.set_axis_title(plot.Y_LEFT, 'Amplitude')
        plot.set_axis_unit(plot.Y_LEFT, x_unit.dimensionality.string)
        win.add_plot_widget(pW, c, column=c % columns)

    progress.done()
    win.add_custom_image_tools()
    win.add_x_synchronization_option(True, range(num_channels))
    win.add_y_synchronization_option(uniform_y_scale,
        range(num_channels))
    win.show()

    return win