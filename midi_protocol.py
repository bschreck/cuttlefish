class Message(object):
    def __init__(self, byte_1=None, byte_2=None, byte_3=None):
        self.byte_1 = byte_1
        self.byte_2 = byte_2
        self.byte_3 = byte_3
        self.intervalTable = {'r':0,
                              'm2':1,
                              'M2':2,
                              'm3':3,
                              'M3':4,
                              '4':5,
                              'tt':6,
                              '5':7,
                              'm6':8,
                              'M6':9,
                              'm7':10,
                              'M7':11}
        self.scaleTable = {'major':[0, 2, 4, 5, 7, 9, 11],
                           'naturalMinor': [0, 2, 3, 5, 7, 8, 10],
                           'harmonicMinor': [0, 2, 3, 5, 7, 8, 11],
                           'jazzMinor': [0, 2, 3, 5, 7, 9, 11],
                           'dorian': [0, 2, 3, 5, 7, 9, 10],
                           'mixolydian': [0, 2, 4, 5, 7, 9, 10],
                           'minorPenta': [0, 3, 5, 7, 10]}
        self.noteNames = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

        self.freqArray = [self.noteNames[i%12]+str((i-24)/12) for i in range(128)]
        self.freqTable = {}
        midiNumber = 0
        for freqName in self.freqArray:
            self.freqTable[freqName] = midiNumber
            midiNumber += 1

    def getMessage(self):
        return [self.byte_1, self.byte_2, self.byte_3]

class NoteOn(Message):
    ''' This message is sent when a note is released (ended).
        channel 1-16
        note 0-127
        velocity 0-127'''
    def __init__(self, channel, note=None, velocity=None):
        self.channel = channel-1
        self.note = note
        self.velocity = velocity
        super(NoteOn, self).__init__()
    def setMessage(self, note, velocity):
        self.note = note
        self.velocity = velocity
        self.byte_1 = (0x9 << 4) + self.channel
        self.byte_2 = note
        self.byte_3 = velocity
    def playNoteFromInterval(self, root, interval, intensity):
        note = self.freqTable[root] + self.intervalTable[interval]
        self.setMessage(note, intensity)
        return self.getMessage()
    def playNoteFromScale(self, scale, root, interval, intensity):
        # figure out way to index negatively or more than 7 for scale tables
        root = self.freqTable[root]
        if interval > 6:
            # up an octave
            root += (12 * (interval/7))
            interval %= 7
        elif interval < 0:
            root += (12 * (interval/7))
            interval = (-interval)%7
        note = root + self.scaleTable[scale][interval]
        if note > 0 and note < 127:
            self.setMessage(note, intensity)
        elif note > 127:
            self.setMessage(127, intensity)
        else:
            self.setMessage(0, intensity)
        return self.getMessage()

class NoteOff(Message):
    ''' This message is sent when a note is depressed (start).
        channel 1-16
        note 0-127
        velocity 0-127'''
    def __init__(self, channel, note=None, velocity=None):
        self.channel = channel-1
        self.note = note
        self.velocity = velocity
        super(NoteOn, self).__init__()
    def setMessage(self, note, velocity):
        self.note = note
        self.velocity = velocity
        self.byte_1 = (0x8 << 4) + self.channel
        self.byte_2 = note
        self.byte_3 = velocity

class PolyAfterTouch(Message):
    ''' This message is most often sent by pressing down on the key
        after it "bottoms out".
        channel 1-16
        note 0-127
        velocity 0-127'''
    def __init__(self, channel, note=None, velocity=None):
        self.channel = channel-1
        self.note = note
        self.velocity = velocity
        super(NoteOn, self).__init__()
    def setMessage(self, note, velocity):
        self.note = note
        self.velocity = velocity
        self.byte_1 = (0xa << 4) + self.channel
        self.byte_2 = note
        self.byte_3 = velocity

class ControlChange(Message):
    ''' This message is sent when a controller value changes.
        Controllers include devices such as pedals and levers.
        Controller numbers 120-127 are reserved as
        "Channel Mode Messages" (below).
        channel 1-16
        controller 0-119
        value 0-127'''
    def __init__(self, channel, controller, value=None):
        self.channel = channel-1
        self.controller = controller
        self.value = value
    def changeController(controller):
        self.controller = controller
    def setMessage(self, value):
        self.value = value
        self.byte_1 = (0xb << 4) + self.channel
        self.byte_2 = self.controller
        self.byte_3 = value

class ProgramChange(Message):
    ''' This message sent when the patch number changes.
        channel 1-16
        patch (new program number) 0-127'''
    def __init__(self, channel, patch=None):
        self.channel = channel-1
        self.patch = patch

    def setMessage(self, patch):
        self.patch = patch
        self.byte_1 = (0xc << 4) + self.channel
        self.byte_2 = patch
        self.byte_3 = 0

class MonoAfterTouch(Message):
    ''' This message is most often sent by pressing down on the key
        after it "bottoms out". This message is different from
        polyphonic after-touch. Use this message to send the single
        greatest pressure value (of all the current depressed keys).
        channel 1-16
        value 0-127'''
    def __init__(self, channel, value=None):
        self.channel = channel-1
        self.value = value
        super(MonoAfterTouch, self).__init__()
    def setMessage(self, value):
        self.value = value
        self.byte_1 = (0xd << 4) + self.channel
        self.byte_2 = value
        self.byte_3 = 0

    def getNoteFromScale(self, scale, root, interval):
        # figure out way to index negatively or more than 7 for scale tables
        root = self.freqTable[root]
        if interval > 6:
            # up an octave
            root += (12 * (interval/7))
            interval %= 7
        elif interval < 0:
            root += (12 * (interval/7))
            interval = (-interval)%7
        note = root + self.scaleTable[scale][interval]
        if note > 0 and note < 127:
            self.setMessage(note)
        elif note > 127:
            self.setMessage(127)
        else:
            self.setMessage(0)
        return self.getMessage()


class PitchWheelChange(Message):
    ''' This message is sent to indicate a change in the pitch wheel.
        The pitch wheel is measured by a fourteen bit value.
        Center (no pitch change) is 0x2000.
        Sensitivity is a function of the transmitter.
        (llllll) are the least significant 7 bits. (mmmmmm)
        are the most significant 7 bits.
        channel 1-16
        value 0-16384 (8192 = center)'''
    def __init__(self, channel, value=None):
        self.channel = channel-1
        self.value = value
    def setMessage(self, value):
        self.value = value
        self.byte_1 = (0xe << 4) + self.channel
        self.byte_2 = value & 0x07
        self.byte_3 = (value >> 7)

class ChannelMode(Message):
    ''' This the same code as the Control Change (above),
        but implements Mode control and special message
        by using reserved controller numbers 120-127.
        The commands are defined in the easier inherited classes below.
        channel 1-16
        mode 120-127
        value 0-127'''
    def __init__(self, channel, mode=None, value=None):
        self.channel = channel-1
        self.mode = mode
        self.value = value

    def setMessage(self, mode, value):
        self.value = value
        self.byte_1 = (0xb << 4) + self.channel
        self.byte_2 = mode
        self.byte_3 = value

class AllSoundOff(ChannelMode):
    ''' When All Sound Off is received all oscillators will turn off,
        and their volume envelopes are set to zero as soon as possible.
        channel 1-16'''
    def __init__(self, channel):
        super(AllSoundOff, self).__init__(channel, 120, 0)
        super(AllSoundOff, self).setMessage(120, 0)

class ResetAllControllers(ChannelMode):
    ''' When Reset All Controllers is received, all controller
        values are reset to their default values.
        channel 1-16'''
    def __init__(self, channel):
        super(ResetAllControllers, self).__init__(channel, 121, 0)

class LocalControl(ChannelMode):
    ''' When Local Control is Off, all devices on a given channel
        will respond only to data received over MIDI. Played data,
        etc. will be ignored. Local Control On restores the functions
        of the normal controllers.
        channel 1-16
        control 'on', 'off' '''
    def __init__(self, channel):
        if control == 'on':
            super(LocalControl, self).__init__(channel, 122, 127)
        else:
            super(LocalControl, self).__init__(channel, 122, 0)

    def setMessage(self, mode, control):
        if control == 'on':
            super(LocalControl, self).setMessage(122, 127)
        else:
            super(LocalControl, self).setMessage(122, 0)

class AllNotesOff(ChannelMode):
    ''' When an All Notes Off is received, all oscillators will turn off.
        channel 1-16
        control: 'allNotesOff', 'omniOn', 'omniOff', 'monoOn', 'polyOn'
        value: 0 except for monoOn, where value = the number of channels (Omni
        Off) or 0 (Omni On)'''
    def __init__(self, channel, control=None, value=None):

        super(AllNotesOff, self).__init__(channel, 0, 0)
    def setMessage(self, control, value):
        c = 0
        if control == 'allNotesOff':
            c = 123
            v = 0
        elif control == 'omniOff':
            c = 124
            v = 0
        elif control == 'omniOn':
            c = 125
            v = 0
        elif control == 'monoOn':
            c = 126
            v = value
        else:
            c = 127
            v = 0
        super(AllNotesOff, self).setMessage(c, v)

# not including System Common Messages, see
# http://www.midi.org/techspecs/midimessages.php

class TimingClock(Message):
    '''Sent 24 times per quarter note when synchronization is required'''
    def __init__(self):
        self.byte_1 = 0xf8
        self.byte_2 = 0
        self.byte_3 = 0

class Start(Message):
    '''Start the current sequence playing. (This message will be followed with
    Timing Clocks).'''
    def __init__(self):
        self.byte_1 = 0xfa
        self.byte_2 = 0
        self.byte_3 = 0


class Continue(Message):
    '''Continue at the point the sequence was Stopped.'''
    def __init__(self):
        self.byte_1 = 0xfb
        self.byte_2 = 0
        self.byte_3 = 0


class Stop(Message):
    ''' Stop the current sequence.'''
    def __init__(self):
        self.byte_1 = 0xfc
        self.byte_2 = 0
        self.byte_3 = 0


class ActiveSensing(Message):
    '''This message is intended to be sent repeatedly to tell the receiver that
    a connection is alive. Use of this message is optional. When initially
    received, the receiver will expect to receive another Active Sensing
    message each 300ms (max), and if it does not then it will assume that the
    connection has been terminated. At termination, the receiver will turn off
    all voices and return to normal (non- active sensing) operation. '''
    def __init__(self):
        self.byte_1 = 0xfe
        self.byte_2 = 0
        self.byte_3 = 0


class Reset(Message):
    '''Reset all receivers in the system to power-up status. This should be
    used sparingly, preferably under manual control. In particular, it should
    not be sent on power-up.'''
    def __init__(self):
        self.byte_1 = 0xff
        self.byte_2 = 0
        self.byte_3 = 0
