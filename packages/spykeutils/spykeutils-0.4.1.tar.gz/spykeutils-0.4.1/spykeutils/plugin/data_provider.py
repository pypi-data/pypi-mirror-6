import neo

class DataProvider(object):
    """ Defines all methods that should be implemented by a
    selection/data provider class.

    A `DataProvider` encapsulates
    access to a selection of data. It can be used by plugins to
    acesss data currently selected in the GUI or in saved selections.
    It also contains an attribute `progress`, a
    :class:`spykeutils.progress_indicator.ProgressIndicator` that
    can be used to report the progress of an operation (and is used
    by methods of this class if they can lead to processing times
    of half a second or more).

    This class serves as an abstract base class and should not be
    instantiated."""
    _factories = {}
    no_unit = neo.Unit(name='No Unit')
    no_segment = neo.Segment(name='No segment')
    no_channel = neo.RecordingChannel(name='No recording channel')
    no_channelgroup = neo.RecordingChannelGroup(name='No recording channel group')
    no_unit.annotate(unique_id=-1)
    no_segment.annotate(unique_id=-1)
    no_channel.annotate(unique_id=-1)
    no_channelgroup.annotate(unique_id=-1)

    def __init__(self, name, progress):
        self.name = name
        self.progress = progress

    def _invert_indices(self, dictionary):
        """ Invert the indices of a dictionary of dictionaries.
        """
        dict_type = type(dictionary)
        ret = dict_type()
        for i1 in dictionary:
            for i2 in dictionary[i1]:
                if not i2 in ret:
                    ret[i2] = dict_type()
                ret[i2][i1] = dictionary[i1][i2]
        return ret

    def blocks(self):
        """ Return a list of selected Block objects.

        The returned objects will contain all regular references, not just to
        selected objects.
        """
        return []

    def segments(self):
        """ Return a list of selected Segment objects.

        The returned objects will contain all regular references, not just to
        selected objects.
        """
        return []

    def recording_channel_groups(self):
        """ Return a list of selected RecordingChannelGroup objects.

        The returned objects will contain all regular references, not just to
        selected objects.
        """
        return []

    def recording_channels(self):
        """ Return a list of selected RecordingChannel objects.

        The returned objects will contain all regular references, not just to
        selected objects.
        """
        return []

    def units(self):
        """ Return a list of selected Unit objects.

        The returned objects will contain all regular references, not just to
        selected objects.
        """
        return []

    def selection_blocks(self):
        """ Return a list of selected blocks.

        The returned blocks will contain references to all other selected
        elements further down in the object hierarchy, but no references to
        elements which are not selected. The returned hierarchy is a copy,
        so changes made to it will not persist. The main purpose
        of this function is to provide an object hierarchy that can be
        saved to a neo file. It is not recommended to use it for data
        processing, the respective functions that return objects lower
        in the hierarchy are better suited for that purpose.
        """
        return []

    def spike_trains(self):
        """ Return a list of :class:`neo.core.SpikeTrain` objects.
        """
        return []

    def spike_trains_by_unit(self):
        """ Return a dictionary (indexed by Unit) of lists of
        :class:`neo.core.SpikeTrain` objects.

        If spike trains not attached to a Unit are selected, their
        dicionary key will be ``DataProvider.no_unit``.
        """
        return {}

    def spike_trains_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        :class:`neo.core.SpikeTrain` objects.

        If spike trains not attached to a Segment are selected, their
        dictionary key will be ``DataProvider.no_segment``.
        """
        return {}

    def spike_trains_by_unit_and_segment(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of :class:`neo.core.SpikeTrain` objects.

        If there are multiple spike trains in one Segment for the same Unit,
        only the first will be contained in the returned dictionary. If spike
        trains not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return {}

    def spike_trains_by_segment_and_unit(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of :class:`neo.core.SpikeTrain` objects.

        If there are multiple spike trains in one Segment for the same Unit,
        only the first will be contained in the returned dictionary. If spike
        trains not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return self._invert_indices(self.spike_trains_by_unit_and_segment())

    def spikes(self):
        """ Return a list of :class:`neo.core.Spike` objects.
        """
        return []

    def spikes_by_unit(self):
        """ Return a dictionary (indexed by Unit) of lists of
        :class:`neo.core.Spike` objects.

        If spikes not attached to a Unit are selected, their
        dicionary key will be ``DataProvider.no_unit``.
        """
        return {}

    def spikes_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        :class:`neo.core.Spike` objects.

        If spikes not attached to a Segment are selected, their
        dictionary key will be ``DataProvider.no_segment``.
        """
        return {}

    def spikes_by_unit_and_segment(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of :class:`neo.core.Spike` lists.

        If there are multiple spikes in one Segment for the same Unit,
        only the first will be contained in the returned dictionary. If
        spikes not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return {}

    def spikes_by_segment_and_unit(self):
        """ Return a dictionary (indexed by Segment) of dictionaries
        (indexed by Unit) of lists of :class:`neo.core.Spike` lists.

        If spikes not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return self._invert_indices(self.spikes_by_unit_and_segment())

    def events(self, include_array_events = True):
        """ Return a dictionary (indexed by Segment) of lists of
        Event objects.

        :param bool include_array_events: Determines if EventArray objects
            should be converted to Event objects and included in the returned
            list.
        """
        return {}

    def labeled_events(self, label, include_array_events = True):
        """ Return a dictionary (indexed by Segment) of lists of Event
        objects with the given label.

        :param str label: The name of the Event objects to be returnded
        :param bool include_array_events: Determines if EventArray objects
            should be converted to Event objects and included in the returned
            list.
        """
        return []

    def event_arrays(self):
        """ Return a dictionary (indexed by Segment) of lists of
        EventArray objects.
        """
        return {}

    def epochs(self, include_array_epochs = True):
        """ Return a dictionary (indexed by Segment) of lists of
        Epoch objects.

        :param bool include_array_epochs: Determines if EpochArray objects
            should be converted to Epoch objects and included in the returned
            list.
        """
        return {}

    def labeled_epochs(self, label, include_array_epochs = True):
        """ Return a dictionary (indexed by Segment) of lists of Epoch
        objects with the given label.

        :param str label: The name of the Epoch objects to be returnded
        :param bool include_array_epochs: Determines if EpochArray objects
            should be converted to Epoch objects and included in the returned
            list.
        """
        return []

    def epoch_arrays(self):
        """ Return a dictionary (indexed by Segment) of lists of
        EpochArray objects.
        """
        return {}

    def analog_signals(self, conversion_mode=1):
        """ Return a list of :class:`neo.core.AnalogSignal` objects.

        :param int conversion_mode: Determines what signals are returned:

            1. AnalogSignal objects only
            2. AnalogSignal objects extracted from AnalogSignalArrays only
            3. Both AnalogSignal objects and extracted AnalogSignalArrays
        """
        return []

    def analog_signals_by_segment(self, conversion_mode=1):
        """ Return a dictionary (indexed by Segment) of lists of
        :class:`neo.core.AnalogSignal` objects.

        If analog signals not attached to a Segment are selected, their
        dictionary key will be ``DataProvider.no_segment``.

        :param int conversion_mode: Determines what signals are returned:

            1. AnalogSignal objects only
            2. AnalogSignal objects extracted from AnalogSignalArrays only
            3. Both AnalogSignal objects and extracted AnalogSignalArrays
        """
        return {}

    def analog_signals_by_channel(self, conversion_mode=1):
        """ Return a dictionary (indexed by RecordingChannel) of lists
        of :class:`neo.core.AnalogSignal` objects.

        If analog signals not attached to a RecordingChannel are selected,
        their dictionary key will be ``DataProvider.no_channel``.

        :param int conversion_mode: Determines what signals are returned:

            1. AnalogSignal objects only
            2. AnalogSignal objects extracted from AnalogSignalArrays only
            3. Both AnalogSignal objects and extracted AnalogSignalArrays
        """
        return {}

    def analog_signals_by_channel_and_segment(self, conversion_mode=1):
        """ Return a dictionary (indexed by RecordingChannel) of
        dictionaries (indexed by Segment) of :class:`neo.core.AnalogSignal`
        lists.

        If analog signals not attached to a Segment or
        RecordingChannel are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channel``,
        respectively.

        :param int conversion_mode: Determines what signals are returned:

            1. AnalogSignal objects only
            2. AnalogSignal objects extracted from AnalogSignalArrays only
            3. Both AnalogSignal objects and extracted AnalogSignalArrays
        """
        return {}

    def analog_signals_by_segment_and_channel(self, conversion_mode=1):
        """ Return a dictionary (indexed by Segment) of
        dictionaries (indexed by RecordingChannel) of :class:`neo.core.AnalogSignal`
        lists.

        If analog signals not attached to a Segment or
        RecordingChannel are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channel``,
        respectively.

        :param int conversion_mode: Determines what signals are returned:

            1. AnalogSignal objects only
            2. AnalogSignal objects extracted from AnalogSignalArrays only
            3. Both AnalogSignal objects and extracted AnalogSignalArrays
        """
        return self._invert_indices(
            self.analog_signals_by_channel_and_segment(conversion_mode))

    def analog_signal_arrays(self):
        """ Return a list of :class:`neo.core.AnalogSignalArray` objects.
        """
        return []

    def analog_signal_arrays_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        :class:`neo.core.AnalogSignalArray` objects.

        If analog signals arrays not attached to a Segment are selected,
        their dictionary key will be ``DataProvider.no_segment``.
        """
        return {}

    def analog_signal_arrays_by_channelgroup(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        lists of :class:`neo.core.AnalogSignalArray` objects.

        If analog signals arrays not attached to a RecordingChannel are
        selected, their dictionary key will be
        ``DataProvider.no_channelgroup``.
        """
        return {}

    def analog_signal_arrays_by_channelgroup_and_segment(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        dictionaries (indexed by Segment) of
        :class:`neo.core.AnalogSignalArray` objects.

        If there are multiple analog signals in one RecordingChannel for
        the same Segment, only the first will be contained in the returned
        dictionary. If analog signal arrays not attached to a Segment or
        RecordingChannelGroup are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channelgroup``,
        respectively.
        """
        return {}

    def analog_signal_arrays_by_segment_and_channelgroup(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        dictionaries (indexed by Segment) of
        :class:`neo.core.AnalogSignalArray` objects.

        If there are multiple analog signals in one RecordingChannel for
        the same Segment, only the first will be contained in the returned
        dictionary. If analog signal arrays not attached to a Segment or
        RecordingChannelGroup are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channelgroup``,
        respectively.
        """
        return self._invert_indices(
            self.analog_signal_arrays_by_channelgroup_and_segment())

    def refresh_view(self):
        """ Refresh associated views of the data.

        Use this method if when you change the neo hierarchy on which the
        selection is based (e.g. adding or removing objects). It will ensure
        that all current views on the data are updated, for example in
        Spyke Viewer.
        """
        pass

    def data_dict(self):
        """ Return a dictionary with all information to serialize the
        object.
        """
        return {}

    @classmethod
    def from_data(cls, data, progress=None):
        """ Create a new `DataProvider` object from a dictionary. This
        method is mostly for internal use.

        The respective type of `DataProvider` (e.g.
        :class:`spykeviewer.plugin_framework.data_provider_neo.DataProviderNeo`
        has to be imported in the environment where this function is
        called.

        :param dict data: A dictionary containing data from a `DataProvider`
            object, as returned by :func:`data_dict`.
        :param ProgressIndicator progress: The object where loading progress
            will be indicated.
        """
        if progress:
            return cls._factories[data['type']](data, progress)
        return cls._factories[data['type']](data)