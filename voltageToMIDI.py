import serial
import midi
import time
import rtmidi
import midi_protocol as mp

#ser = serial.Serial('/dev/tty.usbmodem1411', 115200)
#ser.flushInput()

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

noteOn = mp.NoteOn(1)
for i in range(15):
    midiout.send_message(noteOn.playNoteFromScale('major', 'A0', i, 100))
    time.sleep(.1)
for i in range(16,-10,-3):
    midiout.send_message(noteOn.playNoteFromScale('major', 'A0', i, 100))
    time.sleep(.07)
afterTouch = mp.MonoAfterTouch(1)
midiout.send_message(afterTouch.getNoteFromScale('major', 'A0', -10))
time.sleep(.5)
notesOff = mp.AllSoundOff(1)
midiout.send_message(notesOff.getMessage())
#midiout.send_message(noteOn.playNoteFromScale('major', 'A1', 0, 100))

# 33 = A0
# 127 = G8
#noteOn.setMessage(36, 100)
#midiout.send_message(noteOn.getMessage())

time.sleep(.5)

while False:
    #data = ser.readline()
    #if data:
        #data = int(data)
        #print data
        ## scale data from 0 to 127
        #data = int(data/(1023./127))
        #note_on = [0x90, data, 112] # channel 1, middle C, velocity 112
        #note_off = [0x80, data, 0]
        #midiout.send_message(note_on)
        #time.sleep(.1)
        #midiout.send_message(note_off)
        #time.sleep(.1)

    majorScale = [2, 2, 1, 2, 2, 2, 1]
    naturalMinorScale = [2, 1, 2, 2, 1, 2, 2]
    harmonicMinorScale = [2, 1, 2, 2, 1, 3, 1]
    jazzMinorScale = [2, 1, 2, 2, 2, 2, 1]
    dorianScale = [2, 1, 2, 2, 2, 1, 2]
    mixolydianScale = [2, 2, 1, 2, 2, 1, 2]
    minorPentaScale = [3, 2, 2, 3, 2]

    tonic = 60
    noteOn = mp.NoteOn(1)
    after = mp.PolyAfterTouch(1, 60, 127)
    pitchWheel = mp.PitchWheelChange(1, 0x2000)

    midiout.send_message(noteOn.getMessage())
    time.sleep(.1)
    midiout.send_message(after.getMessage())
    pitch = 8192
    addition = 50
    for i in range(10):
        addition = -addition
        for j in range(10):
            pitch += addition
            pitchWheel.value = pitch
            midiout.send_message(pitchWheel.getMessage())
            time.sleep(.01)

del midiout






#pattern = midi.Pattern()



#track = midi.Track()
#pattern.append(track)

#controller = midi.ControlChangeEvent(tick=100)
#controller.set_control(5)
#print 'controller: ', controller.get_control()
#controller.set_value(data)
#print 'value: ',controller.get_value()
#track.append(controller)
#eot = midi.EndOfTrackEvent(tick=1)
#track.append(eot)
#print pattern
#midi.write_midifile("test.mid", pattern)
