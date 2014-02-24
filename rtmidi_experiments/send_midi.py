import time
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

#note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
#note_off = [0x80, 60, 0]
#for note in range(237):
    #midiout.send_message([0x90, note, 112])
    #time.sleep(.1)
    #midiout.send_message([0x80, note, 0])

control_1 = [0xb0, 0x74, 124]
control_2 = [0xb0, 0x74, 0]
#midiout.send_message(control_1)
time.sleep(.5)
midiout.send_message(control_2)


del midiout
