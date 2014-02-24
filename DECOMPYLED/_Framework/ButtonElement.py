# emacs-mode: -*- python-*-
import Live
from InputControlElement import *
ON_VALUE = int(127)
OFF_VALUE = int(0)
class ButtonElement(InputControlElement):
    __module__ = __name__
    __doc__ = ' Class representing a button a the controller '

    def __init__(self, is_momentary, msg_type, channel, identifier):
        InputControlElement.__init__(self, msg_type, channel, identifier)
        assert isinstance(is_momentary, type(False))
        self._ButtonElement__is_momentary = is_momentary



    def is_momentary(self):
        """ returns true if the buttons sends a message on being released """
        return self._ButtonElement__is_momentary



    def message_map_mode(self):
        assert (self.message_type() is MIDI_CC_TYPE)
        return Live.MidiMap.MapMode.absolute



    def turn_on(self):
        self.send_value(ON_VALUE)



    def turn_off(self):
        self.send_value(OFF_VALUE)




# local variables:
# tab-width: 4
