# emacs-mode: -*- python-*-
import Live
from EncoderElement import EncoderElement
from InputControlElement import *
class SliderElement(EncoderElement):
    __module__ = __name__
    __doc__ = ' Class representing a slider on the controller '

    def __init__(self, msg_type, channel, identifier):
        assert (msg_type is not MIDI_NOTE_TYPE)
        EncoderElement.__init__(self, msg_type, channel, identifier, map_mode=Live.MidiMap.MapMode.absolute)




# local variables:
# tab-width: 4
