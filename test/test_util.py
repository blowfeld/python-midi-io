import unittest
import os
import midiio.fileio
import midiio.util
import mary_test

class TestFileIO(unittest.TestCase):
    test_file = "mary.mid"

    def test_varlen(self):
        maxval = 0x0FFFFFFF
        for inval in range(0, maxval, maxval // 1000):
            datum = midiio.util.write_varlen(inval)
            outval = midiio.util.read_varlen(iter(datum))
            self.assertEqual(inval, outval)

if __name__ == '__main__':
    unittest.main()
