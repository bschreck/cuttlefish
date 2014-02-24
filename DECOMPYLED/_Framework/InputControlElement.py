# emacs-mode: -*- python-*-
import Live
from NotifyingControlElement import NotifyingControlElement
from ControlElement import ControlElement
MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE,
 MIDI_CC_TYPE,
 MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224
class InputControlElement(NotifyingControlElement):
    __module__ = __name__
    __doc__ = ' Base class for all classes representing control elements on a controller '
    _mapping_callback = None
    _forwarding_callback = None
    _translation_callback = None

    def set_mapping_callback(callback):
        """ set callback for installing mappings """
        assert (dir(callback).count('im_func') is 1)
        InputControlElement._mapping_callback = callback


    set_mapping_callback = staticmethod(set_mapping_callback)

    def set_forwarding_callback(callback):
        """ set callback for installing forwardings """
        assert (dir(callback).count('im_func') is 1)
        InputControlElement._forwarding_callback = callback


    set_forwarding_callback = staticmethod(set_forwarding_callback)

    def set_translation_callback(callback):
        """ set callback for installing translations """
        assert (dir(callback).count('im_func') is 1)
        InputControlElement._translation_callback = callback


    set_translation_callback = staticmethod(set_translation_callback)

    def release_class_attributes():
        """ release all set objects to not have dependencies """
        InputControlElement._mapping_callback = None
        InputControlElement._forwarding_callback = None
        InputControlElement._translation_callback = None


    release_class_attributes = staticmethod(release_class_attributes)

    def __init__(self, msg_type, channel, identifier):
        assert (msg_type in MIDI_MSG_TYPES)
        assert (channel in range(16))
        assert ((identifier in range(128)) or (identifier is -1))
        NotifyingControlElement.__init__(self)
        assert (InputControlElement._mapping_callback != None)
        assert (InputControlElement._forwarding_callback != None)
        assert (InputControlElement._translation_callback != None)
        self._msg_type = msg_type
        self._msg_channel = channel
        self._msg_identifier = identifier
        self._original_channel = channel
        self._original_identifier = identifier
        self._parameter_to_map_to = None
        self._last_sent_value = -1
        self._install_mapping = InputControlElement._mapping_callback
        self._install_forwarding = InputControlElement._forwarding_callback
        self._install_translation = InputControlElement._translation_callback



    def disconnect(self):
        NotifyingControlElement.disconnect(self)
        self._parameter_to_map_to = None



    def message_type(self):
        return self._msg_type



    def message_channel(self):
        return self._msg_channel



    def message_identifier(self):
        return self._msg_identifier



    def message_map_mode(self):
        debug_print('message_map_mode() is abstract. Forgot to override it?')
        assert False



    def set_channel(self, channel):
        assert (channel in range(16))
        self._msg_channel = channel



    def set_identifier(self, identifier):
        assert ((identifier in range(128)) or (identifier is -1))
        self._msg_identifier = identifier



    def use_default_message(self):
        self._msg_channel = self._original_channel
        self._msg_identifier = self._original_identifier



    def install_connections(self):
        if ((self._msg_channel != self._original_channel) or (self._msg_identifier != self._original_identifier)):
            self._install_translation(self._msg_type, self._original_identifier, self._original_channel, self._msg_identifier, self._msg_channel)
        if (self._parameter_to_map_to != None):
            self._install_mapping(self, self._parameter_to_map_to)
        if (len(self._value_notifications) > 0):
            self._install_forwarding(self)



    def connect_to(self, parameter):
        assert (parameter != None)
        assert isinstance(parameter, Live.DeviceParameter.DeviceParameter)
        self._parameter_to_map_to = parameter



    def release_parameter(self):
        self._parameter_to_map_to = None



    def mapped_parameter(self):
        return self._parameter_to_map_to



    def status_byte(self):
        status_byte = self._msg_channel
        if (self._msg_type == MIDI_NOTE_TYPE):
            status_byte += MIDI_NOTE_ON_STATUS
        elif (self._msg_type == MIDI_CC_TYPE):
            status_byte += MIDI_CC_STATUS
        else:
            status_byte += MIDI_PB_STATUS
        return status_byte



    def send_value(self, value):
        assert (value != None)
        assert isinstance(value, int)
        assert (value in range(128))
        if (value != self._last_sent_value):
            data_byte1 = self._original_identifier
            data_byte2 = value
            status_byte = self._original_channel
            if (self._msg_type == MIDI_NOTE_TYPE):
                status_byte += MIDI_NOTE_ON_STATUS
            elif (self._msg_type == MIDI_CC_TYPE):
                status_byte += MIDI_CC_STATUS
            else:
                assert False
            self.send_midi((status_byte,
             data_byte1,
             data_byte2))
            self._last_sent_value = value



    def clear_send_cache(self):
        self._last_sent_value = -1



    def reset(self):
        """ Send 0 to reset motorized faders and turn off LEDs """
        self.send_value(0)



    def receive_value(self, value):
        assert isinstance(value, int)
        assert (value in range(128))
        self._last_sent_value = -1
        for notification in self._value_notifications:
            callback = notification['Callback']
            if notification['Identify']:
                callback(value, self)
            else:
                callback(value)





# local variables:
# tab-width: 4
