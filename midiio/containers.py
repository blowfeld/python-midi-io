from pprint import pformat

class Pattern(object):
    def __init__(self, tracks=[], resolution=220, format=1):
        self._format = format
        self._resolution = resolution
        self._tracks = tuple(tracks)

    @property
    def format(self):
        return self._format
    @property
    def resolution(self):
        return self._resolution
    @property
    def tracks(self):
        return self._tracks

    def append(track):
        return Pattern(self._format, self.resolution, self._tracks + (track, ))

    def extend(tracks):
        return Pattern(self._format, self.resolution, self._tracks + tuple(tracks))

    def __getitem__(self, key):
        return self._tracks[key]

    def __iter__(self):
        return iter(self._tracks)

    def __len__(self):
        return len(self._tracks)

    def __repr__(self):
        return "midiio.Pattern(format=%r, resolution=%r, tracks=\\\n%s)" % \
            (self.format, self.resolution, pformat(list(self._tracks)))


class Track(object):
    def __init__(self, events=[]):
        self._events = tuple(events)

    @property
    def events(self):
        return self._events

    def append(event):
        return Track(self._events + (event, ))

    def extend(events):
        return Track(self._events + tuple(events))

    def __getitem__(self, key):
        return self._events[key]

    def __iter__(self):
        return iter(self._events)

    def __len__(self):
        return len(self._events)

    def __repr__(self):
        return "midiio.Track(\\\n  %s)" % (pformat(list(self._events)).replace('\n', '\n  '), )
