import unittest
import os
import midiio.fileio
import midiio.util
import mary_test

class TestFileIO(unittest.TestCase):
    test_file = "mary.mid"

    def test_mary(self):
        midiio.fileio.write_midifile(self.test_file, mary_test.MARY_MIDI)
        pattern1 = midiio.fileio.read_midifile(self.test_file)
        midiio.fileio.write_midifile(self.test_file, pattern1)
        pattern2 = midiio.fileio.read_midifile(self.test_file)

        self.assertTrue(len(pattern1) > 0)
        self.assertEqual(len(pattern1), len(pattern2))
        for track_idx in range(len(pattern1)):
            self.assertTrue(len(pattern1[track_idx]) > 0)
            self.assertEqual(len(pattern1[track_idx]), len(pattern2[track_idx]))
            for event_idx in range(len(pattern1[track_idx])):
                event1 = pattern1[track_idx][event_idx]
                event2 = pattern2[track_idx][event_idx]
                self.assertEqual(event1.tick, event2.tick)
                self.assertEqual(event1.data, event2.data)

    def tearDown(self):
        try:
            os.remove(self.test_file)
        except:
            pass

if __name__ == '__main__':
    unittest.main()
