import inspect
from .events import *

class EventRegistry:
    def __init__(self):
        self._midi_events = dict()
        self._sysex_events = dict()
        self._meta_events = dict()
        self._binary_types = dict()
        self._binary_type_values = set()

    def _register(self, binary_type, base_type):
        # TODO register by type instead of status message
        if binary_type.statusmsg is 0xFF:
            self._meta_events[binary_type.meta_command] = binary_type
        elif binary_type.statusmsg in (0xF0, 0xF7):
            self._sysex_events[binary_type.statusmsg] = binary_type
        else:
            self._midi_events[binary_type.statusmsg] = binary_type

        self._binary_types[base_type] = binary_type
        self._binary_type_values.add(binary_type)

    def is_midi_event(self, status_byte):
        # status byte consists of [statusmsg channel] with 4 bit each
        statusmsg = status_byte & 0xF0

        return statusmsg in self._midi_events

    def is_sysex_event(self, status_byte):
        return status_byte in self._sysex_events

    def is_meta_event(self, status_byte):
        return status_byte == 0xFF
        # return status_byte is BinaryMetaEventMixin.statusmsg

    def get_event(self, status_byte):
        if self.is_meta_event(status_byte):
            return self.get_meta_event(status_byte)

        if self.is_midi_event(status_byte):
            return self.get_midi_event(status_byte)

        if self.is_sysex_event(status_byte):
            return self.get_sysex_event(status_byte)

        raise ValueError("No event with status byte " + str(status_byte))

    def get_midi_event(self, status_byte):
        # status byte consists of [statusmsg channel] with 4 bit each
        statusmsg = status_byte & 0xF0

        return self._midi_events[statusmsg]

    def get_sysex_event(self, status_byte):
        return self._sysex_events[status_byte]

    def get_meta_event(self, meta_command):
        return self._meta_events[meta_command]

    def get_midi_events(self):
        return self._midi_events.values()

    def get_sysex_events(self):
        return self._sysex_events.values()

    def get_meta_events(self):
        return self._meta_events.values()

    def get_binary_type(self, base_type):
        if base_type in self._binary_type_values:
            return base_type

        # TODO cater for inheritance
        return self._binary_types[base_type]

    # TODO
    # def get_status_messages(self):
    #     return STATUS_BYTES
    #
    # def get_meta_commands(self):
    #     return { cmd for cmd in self._meta_events }

EVENTIO_REGISTRY = EventRegistry()

def copy_from(base):
    """
    Add an adapter function from the base class to the class and register the class.

    The added adapter function can be called with any subclass of the provided base
    class and will invoke the constructor of the decorated class. For the constructor
    call the values will be read from the base class properties with the same names.
    """
    def decorator(clazz):
        def copy_method(cls, base_instance):
            if isinstance(base_instance, clazz):
                return base_instance

            arg_names = [ name for name in inspect.getfullargspec(clazz.__init__).args
                    if name is not "self" ]
            args = { arg: getattr(base_instance, arg) for arg in arg_names }

            return cls(**args)

        setattr(clazz, "copy_from", classmethod(copy_method))

        EVENTIO_REGISTRY._register(clazz, base)

        return clazz

    return decorator


class BinaryNoteEventMixin:
    length = 2

    @classmethod
    def from_data(cls, tick, data, channel=0):
        return cls(tick, data[0], data[1], channel)

    @property
    def data(self):
        return (self.pitch, self.velocity)

@copy_from(NoteOnEvent)
class BinaryNoteOnEvent(NoteOnEvent, BinaryNoteEventMixin):
    statusmsg = 0x90

@copy_from(NoteOffEvent)
class BinaryNoteOffEvent(NoteOffEvent, BinaryNoteEventMixin):
    statusmsg = 0x80


@copy_from(AfterTouchEvent)
class BinaryAfterTouchEvent(AfterTouchEvent):
    statusmsg = 0xA0
    length = 2

    @classmethod
    def from_data(cls, tick, data, channel=0):
        return cls(tick, data[0], data[1], channel)

    @property
    def data(self):
        return (self.pitch, self.value)


@copy_from(ControlChangeEvent)
class BinaryControlChangeEvent(ControlChangeEvent):
    statusmsg = 0xB0
    length = 2

    @classmethod
    def from_data(cls, tick, data, channel=0):
        return cls(tick, data[0], data[1], channel)

    @property
    def data(self):
        return (self.control, self.value)


@copy_from(ProgramChangeEvent)
class BinaryProgramChangeEvent(ProgramChangeEvent):
    statusmsg = 0xC0
    length = 1

    @classmethod
    def from_data(cls, tick, data, channel=0):
        return cls(tick, data[0], channel)

    @property
    def data(self):
        return (self.value, )


@copy_from(ChannelAfterTouchEvent)
class BinaryChannelAfterTouchEvent(ChannelAfterTouchEvent):
    statusmsg = 0xD0
    length = 1

    @classmethod
    def from_data(cls, tick, data, channel=0):
        return cls(tick, data[0], channel)

    @property
    def data(self):
        return (self.value, )


@copy_from(PitchWheelEvent)
class BinaryPitchWheelEvent(PitchWheelEvent):
    statusmsg = 0xE0
    length = 2

    @classmethod
    def from_data(cls, tick, data, channel=0):
        pitch = ((self.data[1] << 7) | self.data[0]) - 0x2000
        return cls(tick, pitch, channel)

    @property
    def data(self):
        value = pitch + 0x2000

        return (value & 0x7F, (value >> 7) & 0x7F)


@copy_from(SysexEvent)
class BinarySysexEvent(SysexEvent):
    statusmsg = 0xF0

    @classmethod
    def from_data(cls, tick, data):
        return cls(tick, data)

class BinaryMetaEventMixin():
    statusmsg = 0xFF

    @classmethod
    def from_data(cls, tick, data):
        return cls(tick)

    @property
    def data(self):
        return ()

class BinaryMetaEventWithTextMixin(BinaryMetaEventMixin):
    @classmethod
    def from_data(cls, tick, data):
        text = ''.join(chr(datum) for datum in self.data)
        return cls(tick, text)

    @property
    def data(self):
        return self.text.encode('ascii')

@copy_from(TextMetaEvent)
class BinaryTextMetaEvent(TextMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x01

@copy_from(CopyrightMetaEvent)
class BinaryCopyrightMetaEvent(CopyrightMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x02

@copy_from(TrackNameMetaEvent)
class BinaryTrackNameMetaEvent(TrackNameMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x03

@copy_from(InstrumentNameMetaEvent)
class BinaryInstrumentNameMetaEvent(InstrumentNameMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x04

@copy_from(LyricsMetaEvent)
class BinaryLyricsMetaEvent(LyricsMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x05

@copy_from(MarkerMetaEvent)
class BinaryMarkerMetaEvent(MarkerMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x06

@copy_from(CuePointMetaEvent)
class BinaryCuePointMetaEvent(CuePointMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x07


@copy_from(SequenceNumberMetaEvent)
class BinarySequenceNumberMetaEvent(SequenceNumberMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x00


@copy_from(ChannelPrefixMetaEvent)
class BinaryChannelPrefixMetaEvent(ChannelPrefixMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x20


@copy_from(EndOfTrackMetaEvent)
class BinaryEndOfTrackMetaEvent(EndOfTrackMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x2F


@copy_from(SetTempoMetaEvent)
class BinarySetTempoMetaEvent(SetTempoMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x51
    length = 3

    @classmethod
    def from_data(cls, tick, data):
        assert(len(data) == self.length)

        vals = [data[x] << (16 - (8 * x)) for x in range(self.length)]
        micros_per_quarter = sum(vals)

        return cls(tick, micros_per_quarter)

    @property
    def data(self):
        return [ (self.get_micros_per_quarter >> (16 - (8 * x)) & 0xFF)
            for x in range(self.length) ]


@copy_from(SmpteOffsetMetaEvent)
class BinarySmpteOffsetMetaEvent(SmpteOffsetMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x54


@copy_from(TimeSignatureMetaEvent)
class BinaryTimeSignatureMetaEvent(TimeSignatureMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x58
    length = 4

    @classmethod
    def from_data(cls, tick, data):
        nominator = data[0]
        denominator = 2 ** data[1]
        metronome = data[2]
        thirtyseconds_per_quarter = data[3]

        return cls(tick, nominator, denominator, metronome, thirtyseconds_per_quarter)

    @property
    def data(self):
        return (self.nominator, int(math.log(self.denominator, 2)),
            self.metronome, self.thirtyseconds_per_quarter)


@copy_from(KeySignatureMetaEvent)
class BinaryKeySignatureMetaEvent(KeySignatureMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x59
    length = 2

    @classmethod
    def from_data(cls, tick, data):
        alternatives = data[0] - 256 if data[0] > 127 else data[0]
        minor = data[1]

        return cls(tick, alternatives, minor)

    @property
    def data(self):
        a = self.alternatives

        return (256 + a if a < 0 else a, self.minor)


@copy_from(SequencerSpecificMetaEvent)
class BinarySequencerSpecificMetaEvent(SequencerSpecificMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x7F


# Non-standard events

@copy_from(ProgramNameMetaEvent)
class BinaryProgramNameMetaEvent(ProgramNameMetaEvent, BinaryMetaEventWithTextMixin):
    meta_command = 0x08

@copy_from(PortMetaEvent)
class BinaryPortMetaEvent(PortMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x21


@copy_from(TrackLoopMetaEvent)
class BinaryTrackLoopMetaEvent(TrackLoopMetaEvent, BinaryMetaEventMixin):
    meta_command = 0x2E
