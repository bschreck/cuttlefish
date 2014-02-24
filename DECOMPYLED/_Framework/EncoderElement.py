# emacs-mode: -*- python-*-
import Live
from InputControlElement import *
class EncoderElement(InputControlElement):
    __module__ = __name__
    __doc__ = ' Class representing a continuous control on the controller '

    def __init__(self, msg_type, channel, identifier, map_mode):
        InputControlElement.__init__(self, msg_type, channel, identifier)
        self._EncoderElement__map_mode = map_mode



    def message_map_mode(self):
        assert (self.message_type() is MIDI_CC_TYPE)
        return self._EncoderElement__map_mode




# local variables:
# tab-width: 4
