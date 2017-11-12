#!/usr/bin/env pypy
import midiio
import subprocess as s

def main():
    p = s.Popen(["timidity"]+['--verbose']*1+["-"],stdin=s.PIPE)
    writer = midiio.FileWriter(p.stdin)
    writer.write_file_header(midiio.Pattern(),2)
    track = midiio.Track((
        midiio.TimeSignatureEvent(tick=0,numerator=4,denominator=4,
                metronome=24,
                thirtyseconds=8),
        midiio.KeySignatureEvent(tick=0),
        midiio.EndOfTrackEvent(tick=1)
    ))
    writer.write_track(track)

    def song():
        for i in range(5):
            yield midiio.NoteOnEvent(tick=i*100, velocity=200, pitch=(midiio.G_5+i))
        yield midiio.EndOfTrackEvent(tick=1)
    writer.write_track(midiio.Track(song()))
    p.stdin.flush()
    p.stdin.close()
    p.wait()



if __name__ == '__main__':
    main()
