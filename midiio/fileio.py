from .constants import *
from .containers import *
from .events import *
from .eventio import *
from .util import *


class _ChunkParserMixin(object):
    def parse_chunk(self, midi_reader):
        """
        A chunk always has three components. The three parts to each chunk are:

        * The track ID string which is four charcters long. For example, header
        chunk IDs are "MThd", and Track chunk IDs are "MTrk".
        * next is a four-byte unsigned value that specifies the number of bytes in
        the data section of the track (part 3).
        * finally comes the data section of the chunk. The size of the data is
        specified in the length field which follows the chunk ID (part 2).
        """
        chunk_id = midi_reader.read(4)
        chunk_size = read_long(midi_reader.read(4))
        chunk_data = bytes(midi_reader.read(chunk_size))

        return chunk_id, chunk_data


class MidiIO(_ChunkParserMixin):
    def __init__(self, event_registry = EVENTIO_REGISTRY):
        self._header_io = HeaderIO()
        self._track_io = TrackIO(event_registry)

    def parse(self, midi_reader):
        """
        A standard MIDI file is composed of "chunks". It starts with a header chunk and
        is followed by one or more track chunks. The header chunk contains data that
        pertains to the overall file. Each track chunk defines a logical track.

        SMF = <header_chunk> + <track_chunk> [+ <track_chunk> ...]
        """
        chunk_id, chunk_data = self.parse_chunk(midi_reader)

        if chunk_id != b'MThd':
            raise "Invalid file header: " + chunk_id.decode("ascii")

        tracks, resolution, format_version = self._header_io.parse(chunk_data)
        track_list = [ self._track_io.parse(midi_reader) for _ in range(tracks) ]

        return Pattern(track_list, resolution, format_version)

    def write(self, pattern, midi_writer):
        self._header_io.write_pattern_header(pattern, midi_writer)
        for track in pattern:
            self._track_io.write(track, midi_writer)


class HeaderIO(object):
    HEADER_LENGTH = 6

    def parse(self, header_data):
        """
        The header chunk consists of a literal string denoting the header, a length
        indicator, the format of the MIDI file, the number of tracks in the file, and a
        timing value specifying delta time units. Numbers larger than one byte are
        placed most significant byte first.

        header_chunk = "MThd" + <header_length> + <format> + <n> + <division>

        "MThd" 4 bytes
        the literal string MThd, or in hexadecimal notation: 0x4d546864. These four
        characters at the start of the MIDI file indicate that this is a MIDI file.
        <header_length> 4 bytes
        length of the header chunk (always 6 bytes long--the size of the next three
        fields which are considered the header chunk).
        <format> 2 bytes
        0 = single track file format
        1 = multiple track file format
        2 = multiple song file format (i.e., a series of type 0 files)
        <n> 2 bytes
        number of track chunks that follow the header chunk
        <division> 2 bytes (ticks per quarter note)
        unit of time for delta timing. If the value is positive, then it represents
        the units per beat. For example, +96 would mean 96 ticks per beat. If the
        value is negative, delta times are in SMPTE compatible units.
        """

        format_version = read_short(header_data[0:2])
        tracks = read_short(header_data[2:4])
        resolution = read_short(header_data[4:6])

        return tracks, resolution, format_version

    def write_pattern_header(self, pattern, midi_writer):
        return self.write(len(pattern), pattern.format, pattern.resolution,
                midi_writer)

    def write(self, tracks, format_version, resolution, midi_writer):
        header_length = long_to_bytes(self.HEADER_LENGTH)

        midi_writer.write(b'MThd')
        midi_writer.write(header_length)
        midi_writer.write(short_to_bytes(format_version))
        midi_writer.write(short_to_bytes(tracks))
        midi_writer.write(short_to_bytes(resolution))


class TrackIO(_ChunkParserMixin):
    def __init__(self, event_registry):
        self._event_io = EventIO(event_registry)
        self._event_registry = event_registry

    def parse(self, midi_reader):
        """
        A track chunk consists of a literal identifier string, a length indicator
        specifying the size of the track, and actual event data making up the track.

        track_chunk = "MTrk" + <length> + <track_event> [+ <track_event> ...]

        "MTrk" 4 bytes
        the literal string MTrk. This marks the beginning of a track.
        <length> 4 bytes
        the number of bytes in the track chunk following this number.
        <track_event>
        a sequenced track event.
        """
        chunk_id, chunk_data = self.parse_chunk(midi_reader)

        if chunk_id != b'MTrk':
            raise "Invalid track header: " + chunk_id.decode("ascii")

        events = self._event_io.parse_events(chunk_data)

        return Track(events)

    def write(self, track, midi_writer):
        buf = bytearray()
        for event in track:
            binary_event = self._event_registry.get_binary_type(type(event))\
                    .copy_from(event)
            buf.extend(self._event_io.encode_event(binary_event))

        header = self.encode_track_header(len(buf))

        midi_writer.write(header)
        midi_writer.write(buf)

    def encode_track_header(self, track_length):
        return b'MTrk' + long_to_bytes(track_length)


class EventIO(object):
    def __init__(self, event_registry):
        self._event_registry = event_registry

    def parse_events(self, track_data):
        """
        * Track Event

        A track event consists of a delta time since the last event, and one of three
        types of events.

           track_event = <v_time> + <midi_event> | <meta_event> | <sysex_event>

        <v_time>
            a variable length value specifying the elapsed time (delta time) from the
            previous event to this event.
        <midi_event>
            any MIDI channel message such as note-on or note-off. Running status is used
            in the same manner as it is used between MIDI devices.
        <meta_event>
            an SMF meta event.
        <sysex_event>
            an SMF system exclusive event.

        * Meta Event
        Meta events are non-MIDI data of various sorts consisting of a fixed prefix,
        type indicator, a length field, and actual event data..

           meta_event = 0xFF + <meta_type> + <v_length> + <event_data_bytes>

        <meta_type> 1 byte
        <v_length>
            length of meta event data expressed as a variable length value.
        <event_data_bytes>
            the actual event data.

        * System Exclusive Event
        A system exclusive event can take one of two forms:

        sysex_event = 0xF0 + <data_bytes> 0xF7 or sysex_event = 0xF7 + <data_bytes> 0xF7

        In the first case, the resultant MIDI data stream would include the 0xF0. In the
        second case the 0xF0 is omitted.
        """
        track_data = iter(track_data)

        runningStatus = None
        events = []

        while True:
            try:
                # first datum is varlen representing delta-time
                tick = read_varlen(track_data)
                # next byte is status message
                status_byte = next(track_data)
                if self._event_registry.is_midi_event(status_byte):
                    # status byte consists of [statusmsg channel] with 4 bit each
                    channel = status_byte & 0x0F
                    event_type = self._event_registry.get_midi_event(status_byte)
                    data = self._parse_midi_event(event_type, track_data)
                    event = event_type.from_data(tick, data, channel)
                    runningStatus = (channel, event_type)
                elif self._event_registry.is_sysex_event(status_byte):
                    if runningStatus is not None:
                        runningStatus = None
                        continue

                    event_type = self._event_registry.get_sysex_event(status_byte)
                    data = self._parse_sysex_event(event_type, track_data)
                    event = event_type.from_data(tick, data)
                elif self._event_registry.is_meta_event(status_byte):
                    cmd = next(track_data)
                    event_type = self._event_registry.get_meta_event(cmd)

                    data = self._parse_meta_event(event_type, track_data)
                    event = event_type.from_data(tick, data)
                    runningStatus = None
                else:
                    assert runningStatus, ("Bad byte value", tick,
                            status_byte, bytes(track_data))

                    channel, event_type = runningStatus
                    data = self._parse_midi_event(event_type, track_data)
                    event = event_type.from_data(tick, data, channel)

                    if isinstance(event, NoteOnEvent) and event.velocity is 0:
                        event = BinaryNoteOffEvent(tick, event.pitch, 0x40, channel)

                events.append(event)
            except StopIteration:
                break

        return tuple(events)

    def _parse_meta_event(self, event_type, track_data):
        datalen = read_varlen(track_data)

        return [ next(track_data) for _ in range(datalen) ]

    def _parse_sysex_event(self, event_type, track_data):
        data = []

        # TODO move to BinarySysexEvent
        current_byte = None
        while current_byte != 0xF7:
            current_byte = next(trackdata)
            data.append(current_byte)

        return data

    def _parse_midi_event(self, event_type, track_data):
        return [ next(track_data) for _ in range(event_type.length) ]

    def encode_event(self, event):
        assert isinstance(event.tick, int), event.tick

        result = bytearray()
        result.extend(write_varlen(event.tick))
        if isinstance(event, MetaEvent):
            result.append(event.statusmsg)
            result.append(event.meta_command)
            result.extend(write_varlen(len(event.data)))
            result.extend(event.data)
        elif isinstance(event, SysexEvent):
            result.append(SysexEvent.statusmsg)
            result.extend(event.data)
            # TODO
            result.append(0xF7)
        elif isinstance(event, MidiEvent):
            # For files let's not use a running Status and always set the status message
            result.append(event.statusmsg | event.channel)
            result.extend(event.data)
        else:
            raise ValueError("Unknown MIDI Event: " + str(event))

        return result


def write_midifile(midifile, pattern):
    if type(midifile) in (str, str):
        with open(midifile, 'wb') as out:
            return write_midifile(out, pattern)

    return MidiIO().write(pattern, midifile)

def read_midifile(midifile):
    if type(midifile) in (str, bytes):
        with open(midifile, 'rb') as inp:
            return read_midifile(inp)

    return MidiIO().parse(midifile)
