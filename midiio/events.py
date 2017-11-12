import math

class _AbstractEvent:
    name = "Generic MIDI Event"

    def __init__(self, tick):
        self._tick = tick

    @property
    def tick(self):
        return self._tick

    def __cmp__(self, other):
        return self._tick - other._tick

    def __baserepr__(self, keys=[]):
        keys = ['tick'] + keys
        body = []
        for key in keys:
            val = getattr(self, key)
            keyval = "%s=%r" % (key, val)
            body.append(keyval)
        body = str.join(', ', body)
        return "midi.%s(%s)" % (self.__class__.__name__, body)

    def __repr__(self):
        return self.__baserepr__()


class MidiEvent(_AbstractEvent):
    name = 'Generic Midi Event'

    def __init__(self, tick, channel=0):
        super().__init__(tick)
        self._channel = channel

    @property
    def channel(self):
        return self._channel


class _NoteEvent(MidiEvent):
    def __init__(self, tick=None, pitch=None, velocity=None, channel=0):
        super().__init__(tick, channel)
        self._pitch = pitch
        self._velocity = velocity

    @property
    def pitch(self):
        return self._pitch

    @property
    def velocity(self):
        return self._velocity

class NoteOnEvent(_NoteEvent):
    name = 'Note On'

class NoteOffEvent(_NoteEvent):
    name = 'Note Off'


class AfterTouchEvent(MidiEvent):
    name = 'After Touch'

    def __init__(self, tick=None, pitch=None, value=None, channel=0):
        super().__init__(tick, channel)
        self._pitch = pitch
        self._value = value

    @property
    def pitch(self):
        return self._pitch

    @property
    def value(self):
        return self._value


class ControlChangeEvent(MidiEvent):
    name = 'Control Change'

    def __init__(self, tick=None, control=None, value=None, channel=0):
        super().__init__(tick, channel)
        self._control = control
        self._value = value

    @property
    def control(self):
        return self._control

    @property
    def value(self):
        return self._value


class ProgramChangeEvent(MidiEvent):
    name = 'Program Change'

    def __init__(self, tick=None, value=None, channel=0):
        super().__init__(tick, channel)
        self._value = value

    @property
    def value(self):
        return self._value


class ChannelAfterTouchEvent(MidiEvent):
    name = 'Channel After Touch'

    def __init__(self, tick=None, value=None, channel=0):
        super().__init__(tick, channel)
        self._value = value

    @property
    def value(self):
        return self._value


class PitchWheelEvent(MidiEvent):
    name = 'Pitch Wheel'

    def __init__(self, tick=None, pitch=None, channel=0):
        super().__init__(tick, channel)
        self._pitch = pitch

    @property
    def pitch(self):
        return self._pitch


class SysexEvent(_AbstractEvent):
    name = 'SysEx'

    def __init__(self, tick, data):
        super().__init__(tick)
        self._data = data

    @property
    def data(self):
        return self._data


class MetaEvent(_AbstractEvent):
    name = 'Meta Event'

class SequenceNumberMetaEvent(MetaEvent):
    name = 'Sequence Number'

class MetaEventWithText(MetaEvent):
    def __init__(self, tick, text):
        super().__init__(tick)
        self._text = text

    @property
    def text(self):
        return self._text

    def __repr__(self):
        return self.__baserepr__(['text'])

class TextMetaEvent(MetaEventWithText):
    name = 'Text'

class CopyrightMetaEvent(MetaEventWithText):
    name = 'Copyright Notice'

class TrackNameMetaEvent(MetaEventWithText):
    name = 'Track Name'

class InstrumentNameMetaEvent(MetaEventWithText):
    name = 'Instrument Name'

class LyricsMetaEvent(MetaEventWithText):
    name = 'Lyrics'

class MarkerMetaEvent(MetaEventWithText):
    name = 'Marker'

class CuePointMetaEvent(MetaEventWithText):
    name = 'Cue Point'

class ProgramNameMetaEvent(MetaEventWithText):
    name = 'Program Name'

class ChannelPrefixMetaEvent(MetaEvent):
    name = 'Channel Prefix'

class PortMetaEvent(MetaEvent):
    name = 'MIDI Port/Cable'

class TrackLoopMetaEvent(MetaEvent):
    name = 'Track Loop'

class EndOfTrackMetaEvent(MetaEvent):
    name = 'End of Track'

class SetTempoMetaEvent(MetaEvent):
    name = 'Set Tempo'

    def __init__(self, tick=None, micros_per_quarter=None):
        super().__init__(tick)
        self._micros_per_quarter = micros_per_quarter

    @property
    def bpm(self, bpm):
        return float(6e7) / self._micros_per_quarter

    @property
    def micros_per_quarter(self):
        return self._micros_per_quarter

class SmpteOffsetMetaEvent(MetaEvent):
    name = 'SMPTE Offset'

class TimeSignatureMetaEvent(MetaEvent):
    name = 'Time Signature'
    metacommand = 0x58
    length = 4

    def __init__(self, tick=None, nominator=None, denominator=None,
        metronome=None, thirtyseconds_per_quarter=None):
        super().__init__(tick)
        self._nominator = nominator
        self._denominator = denominator
        self._metronome = metronome
        self._thirtys_per_quarter = thirtyseconds_per_quarter

    @property
    def nominator(self):
        return self._nominator

    @property
    def denominator(self):
        return self._denominator

    @property
    def metronome(self):
        return self._metronome

    @property
    def thirtyseconds_per_quarter(self):
        return self._thirtys_per_quarter

class KeySignatureMetaEvent(MetaEvent):
    name = 'Key Signature'
    metacommand = 0x59
    length = 2

    def __init__(self, tick=None, alternatives=None, minor=None):
        super().__init__(tick)
        self._alternatives = alternatives
        self._minor = minor

    @property
    def alternatives(self):
        return self._alternatives

    @property
    def minor(self):
        return self._minor

class SequencerSpecificMetaEvent(MetaEvent):
    name = 'Sequencer Specific'
    metacommand = 0x7F


if __name__ == '__main__':
    import inspect
    from pprint import pprint

    pprint(KeySignatureEvent().__dict__)
    pprint(dict(KeySignatureEvent))
    pprint(type(KeySignatureEvent))
