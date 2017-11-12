import midiio
# Instantiate a MIDI Pattern (contains a list of tracks)
pattern = midiio.Pattern()
# Instantiate a MIDI Track (contains a list of MIDI events)
pattern.append(midiio.Track((
    midiio.TimeSignatureEvent(tick=0,numerator=4,denominator=4,
                            metronome=24,
                            thirtyseconds=8),
    midiio.KeySignatureEvent(tick=0),
    midiio.EndOfTrackEvent(tick=1)
    )))
track = midiio.Track()
pattern.append(track)
#reverb
#track.append(midiio.ControlChangeEvent(tick=0,data=[91,58]))
#track.append(midiio.ControlChangeEvent(tick=0,data=[10,69]))
#msb
#track.append(midiio.ControlChangeEvent(tick=0,channel=0,data=[0,0]))
#lsb
#track.append(midiio.ControlChangeEvent(tick=0,channel=0,data=[32,0]))
#track.append(midiio.ProgramChangeEvent(tick=0,channel=0,data=[24]))
# Instantiate a MIDI note on event, append it to the track
track.append(midiio.NoteOnEvent(tick=0, velocity=200, pitch=midiio.G_4))
# Instantiate a MIDI note off event, append it to the track
track.append(midiio.NoteOffEvent(tick=250, velocity=200, pitch=midiio.G_4))
track.append(midiio.EndOfTrackEvent(tick=100))
# some more notes
pattern.append(midiio.Track((
    midiio.NoteOnEvent(tick=200, velocity=200, pitch=(midiio.F_4+1)),
    midiio.NoteOnEvent(tick=200, velocity=200, pitch=midiio.A_4),
    midiio.NoteOnEvent(tick=200, velocity=200, pitch=midiio.C_5),
    midiio.EndOfTrackEvent(tick=1))))
# Add the end of track event, append it to the track
# Print out the pattern
print(pattern)
# Save the pattern to disk
midiio.write_midifile("example.mid", pattern)
