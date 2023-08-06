from PySide import QtGui
import numpy as np
from pyqtgraph import GraphicsLayoutWidget, mkPen
from pypore.filetypes import event_database as eD
from pyporegui.graphicsItems.histogram_item import HistogramItem
from pyporegui.graphicsItems.scatter_plot_item import ScatterPlotItem

__all__ = ['EventAnalysisPlotWidget']


class EventAnalysisPlotWidget(GraphicsLayoutWidget):

    def __init__(self):
        super(EventAnalysisPlotWidget, self).__init__()

        self.plot_eventdepth = HistogramItem(title='Event Depth', rotate=True)
        self.addItem(self.plot_eventdepth)
        self.plot_eventdepth.setMouseEnabled(x=False, y=True)
        self.plot_eventdur_eventdepth = self.addPlot(name='Depth vs. Duration', title='Depth vs. Duration')
        self.plot_eventdepth.setYLink('Depth vs. Duration')

        self.nextRow()

        self.plot_scatterselect = self.addPlot(title='Single Event')

        self.plot_eventdur = HistogramItem(title='Event Duration')
        self.addItem(self.plot_eventdur)
        self.plot_eventdur.setXLink('Depth vs. Duration')
        self.plot_eventdur.setMouseEnabled(x=True, y=False)

        self.lastScatterClicked = []

        self.nbins = 0
        self.bins = np.zeros(0)

    def add_selections(self, file_names, params):
        '''
        Plots event statistics.
        '''
        files = []
        counts = []
        eventCount = 0
        for filename in file_names:
            h5file = eD.open_file(filename, mode='r')
            files.append(h5file)
            count = h5file.get_event_count()
            eventCount += count
            counts.append(count)

        currentBlockade = np.empty(eventCount)
        dwellTimes = np.empty(eventCount)
        count = 0
        for j, filex in enumerate(files):
            eventTable = filex.get_event_table()
            sample_rate = filex.get_sample_rate()
            for i, row in enumerate(eventTable):
                currentBlockade[count + i] = row['current_blockage']
                dwellTimes[count + i] = row['event_length'] / sample_rate
            count += counts[j]

        color = params['color']
        newcolor = QtGui.QColor(color.red(), color.green(), color.blue(), 128)

        self.plot_eventdur.add_histogram(dwellTimes, color=newcolor)

        self.plot_eventdepth.add_histogram(currentBlockade, color=newcolor)

        scatterItem = ScatterPlotItem(size=10, pen=mkPen(None), brush=newcolor, files=file_names, counts=counts)
        scatterItem.setData(dwellTimes, currentBlockade)
        self.plot_eventdur_eventdepth.addItem(scatterItem)
        scatterItem.sigClicked.connect(self.onScatterPointsClicked)

        for filex in files:
            filex.close()

        return

    def removeFilter(self, index):
        self.plot_eventdur.remove_item_at(index)
        self.plot_eventdepth.remove_item_at(index)
        self.plot_eventdur_eventdepth.removeItem(self.plot_eventdur_eventdepth.listDataItems()[index])

    def onScatterPointsClicked(self, plot, points):
        """
        Callback for when a scatter plot points are clicked.
        Highlights the points and unhighlights previously selected points.

        plot should be a MyScatterPlotItem
        points should be a MySpotItem
        """
        for p in self.lastScatterClicked:
            p.resetPen()
            # remove point we've already selected so we
            # can select points behind it.
            if p in points and len(points) > 1:
                points.remove(p)
#         print 'Points clicked:', points, plot
        for point in points:
            point.setPen('w', width=2)
            self.lastScatterClicked = [point]
            break  # only take first point

        # Plot the new point clicked on the single event display
        filename, position = plot.get_file_name_from_position(self.lastScatterClicked[0].event_position)

        h5file = eD.open_file(filename, mode='r')

        table = h5file.root.events.eventTable
        row = h5file.get_event_row(position)
        array_row = row['array_row']
        sample_rate = h5file.get_sample_rate()
        event_length = row['event_length']
        raw_points_per_side = row['raw_points_per_side']

        raw_data = h5file.get_raw_data_at(array_row)

        n = len(raw_data)

        times = np.linspace(0.0, 1.0 * n / sample_rate, n)

        self.plot_scatterselect.clear()
        self.plot_scatterselect.plot(times, raw_data)
        # plot the event points in yellow
        self.plot_scatterselect.plot(times[raw_points_per_side:raw_points_per_side + event_length], \
                                     raw_data[raw_points_per_side:raw_points_per_side + event_length], pen='y')

        # Plot the cusum levels
        n_levels = row['n_levels']
        baseline = row['baseline']
        # left, start-1, start,
        levels = h5file.get_levels_at(array_row)
        indices = h5file.get_level_lengths_at(array_row)

        levelTimes = np.zeros(2 * n_levels + 4)
        levelValues = np.zeros(2 * n_levels + 4)

        levelTimes[1] = 1.0 * (raw_points_per_side - 1) / sample_rate
        levelValues[0] = levelValues[1] = baseline
        i = 0
        length = 0
        for i in xrange(n_levels):
            levelTimes[2 * i + 2] = times[raw_points_per_side] + 1.0 * (length) / sample_rate
            levelValues[2 * i + 2] = levels[i]
            levelTimes[2 * i + 3] = times[raw_points_per_side] + 1.0 * (length + indices[i]) / sample_rate
            levelValues[2 * i + 3] = levels[i]
            length += indices[i]
        i += 1
        levelTimes[2 * i + 2] = times[raw_points_per_side + event_length]
        levelTimes[2 * i + 3] = times[n - 1]
        levelValues[2 * i + 2] = levelValues[2 * i + 3] = baseline

        self.plot_scatterselect.plot(levelTimes, levelValues, pen='g')

        h5file.close()