from pprint import pprint
import unittest
from midiio.events import *
from midiio.eventio import *

class TestEventsIO(unittest.TestCase):
    def test_registry(self):
        self.assertEqual(len(EVENTIO_REGISTRY.get_midi_events()), 7)
        self.assertEqual(len(EVENTIO_REGISTRY.get_sysex_events()), 1)
        self.assertEqual(len(EVENTIO_REGISTRY.get_meta_events()), 18)

        self.assertEqual(EVENTIO_REGISTRY.get_midi_event(0x90), BinaryNoteOnEvent)
        self.assertEqual(EVENTIO_REGISTRY.get_midi_event(0x80), BinaryNoteOffEvent)


    def test_status_bytes(self):
        # Midi Events
        self.assertEqual(BinaryNoteOffEvent.statusmsg, 0x80)
        self.assertEqual(BinaryNoteOnEvent.statusmsg, 0x90)
        self.assertEqual(BinaryAfterTouchEvent.statusmsg, 0xA0)
        self.assertEqual(BinaryControlChangeEvent.statusmsg, 0xB0)
        self.assertEqual(BinaryProgramChangeEvent.statusmsg, 0xC0)
        self.assertEqual(BinaryChannelAfterTouchEvent.statusmsg, 0xD0)
        self.assertEqual(BinaryPitchWheelEvent.statusmsg, 0xE0)

        # SysEx Event
        self.assertEqual(BinarySysexEvent.statusmsg, 0xF0)
        # self.assertEqual(BinarySysexEvent.statusmsg, 0xF7)

        # Meta Events
        self.assertEqual(BinarySequenceNumberMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinarySequenceNumberMetaEvent.meta_command, 0x00)
        self.assertEqual(BinaryTextMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryTextMetaEvent.meta_command, 0x01)
        self.assertEqual(BinaryCopyrightMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryCopyrightMetaEvent.meta_command, 0x02)
        self.assertEqual(BinaryTrackNameMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryTrackNameMetaEvent.meta_command, 0x03)
        self.assertEqual(BinaryInstrumentNameMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryInstrumentNameMetaEvent.meta_command, 0x04)
        self.assertEqual(BinaryLyricsMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryLyricsMetaEvent.meta_command, 0x05)
        self.assertEqual(BinaryMarkerMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryMarkerMetaEvent.meta_command, 0x06)
        self.assertEqual(BinaryCuePointMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryCuePointMetaEvent.meta_command, 0x07)
        self.assertEqual(BinaryChannelPrefixMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryChannelPrefixMetaEvent.meta_command, 0x20)
        self.assertEqual(BinaryEndOfTrackMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryEndOfTrackMetaEvent.meta_command, 0x2F)
        self.assertEqual(BinarySetTempoMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinarySetTempoMetaEvent.meta_command, 0x51)
        self.assertEqual(BinarySmpteOffsetMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinarySmpteOffsetMetaEvent.meta_command, 0x54)
        self.assertEqual(BinaryTimeSignatureMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryTimeSignatureMetaEvent.meta_command, 0x58)
        self.assertEqual(BinaryKeySignatureMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryKeySignatureMetaEvent.meta_command, 0x59)
        self.assertEqual(BinarySequencerSpecificMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinarySequencerSpecificMetaEvent.meta_command, 0x7F)

        # Non-standard ?
        self.assertEqual(BinaryProgramNameMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryProgramNameMetaEvent.meta_command, 0x08)
        self.assertEqual(BinaryPortMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryPortMetaEvent.meta_command, 0x21)
        self.assertEqual(BinaryTrackLoopMetaEvent.statusmsg, 0xFF)
        self.assertEqual(BinaryTrackLoopMetaEvent.meta_command, 0x2E)

    def test_copy_from_normal_event(self):
        noteOnEvent = NoteOnEvent(1, 2, 3, 4)

        binaryNoteOnEvent = BinaryNoteOnEvent.copy_from(noteOnEvent)

        self.assertEqual(binaryNoteOnEvent.tick, 1)
        self.assertEqual(binaryNoteOnEvent.pitch, 2)
        self.assertEqual(binaryNoteOnEvent.velocity, 3)
        self.assertEqual(binaryNoteOnEvent.channel, 4)

    def test_copy_from_binary_event(self):
        binaryNoteOnEvent = BinaryNoteOnEvent(1, 2, 3, 4)

        copy = BinaryNoteOnEvent.copy_from(binaryNoteOnEvent)

        self.assertIs(binaryNoteOnEvent, copy)


if __name__ == '__main__':
    unittest.main()
