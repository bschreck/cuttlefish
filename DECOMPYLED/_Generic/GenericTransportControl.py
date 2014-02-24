# emacs-mode: -*- python-*-
import Live
from GenericComponent import GenericComponent
from consts import *
class GenericTransportControl(GenericComponent):
    __module__ = __name__
    __doc__ = ' Class representing the transport section in Live '

    def __init__(self, parent, controllers):
        self._GenericTransportControl__parent = parent
        self._GenericTransportControl__controllers = controllers
        self._GenericTransportControl__ffwd_held = False
        self._GenericTransportControl__rwd_held = False
        self._GenericTransportControl__delay_counter = 0
        self._GenericTransportControl__parent.song().add_is_playing_listener(self._GenericTransportControl__on_playing_status_changed)
        self._GenericTransportControl__parent.song().add_record_mode_listener(self._GenericTransportControl__on_recording_status_changed)
        self._GenericTransportControl__parent.song().add_loop_listener(self._GenericTransportControl__on_loop_status_changed)



    def build_midi_map(self, script_handle, midi_map_handle):
        for cc_no in self._GenericTransportControl__controllers.values():
            if (cc_no >= 0):
                for channel in range(NUM_CHANNELS):
                    Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, cc_no)





    def receive_midi_cc(self, cc_no, cc_value):
        if (cc_no == self._GenericTransportControl__controllers['STOP']):
            if (cc_value > 0):
                self._GenericTransportControl__parent.song().is_playing = False
        elif (cc_no == self._GenericTransportControl__controllers['PLAY']):
            if (cc_value > 0):
                self._GenericTransportControl__parent.song().is_playing = True
        elif (cc_no == self._GenericTransportControl__controllers['REC']):
            if (cc_value > 0):
                self._GenericTransportControl__parent.song().record_mode = (not self._GenericTransportControl__parent.song().record_mode)
        elif (cc_no == self._GenericTransportControl__controllers['LOOP']):
            if (cc_value > 0):
                self._GenericTransportControl__parent.song().loop = (not self._GenericTransportControl__parent.song().loop)
        elif (cc_no == self._GenericTransportControl__controllers['RWD']):
            if (not self._GenericTransportControl__ffwd_held):
                if (cc_value > 0):
                    if (not ('NORELEASE' in self._GenericTransportControl__controllers.keys())):
                        self._GenericTransportControl__rwd_held = True
                        self._GenericTransportControl__delay_counter = 0
                    self._GenericTransportControl__parent.song().jump_by((-1 * self._GenericTransportControl__parent.song().signature_denominator))
                elif (not ('NORELEASE' in self._GenericTransportControl__controllers.keys())):
                    self._GenericTransportControl__rwd_held = False
        elif (cc_no == self._GenericTransportControl__controllers['FFWD']):
            if (not self._GenericTransportControl__rwd_held):
                if (cc_value > 0):
                    if (not ('NORELEASE' in self._GenericTransportControl__controllers.keys())):
                        self._GenericTransportControl__ffwd_held = True
                        self._GenericTransportControl__delay_counter = 0
                    self._GenericTransportControl__parent.song().jump_by(self._GenericTransportControl__parent.song().signature_denominator)
                elif (not ('NORELEASE' in self._GenericTransportControl__controllers.keys())):
                    self._GenericTransportControl__ffwd_held = False



    def refresh_state(self):
        if self._GenericTransportControl__ffwd_held:
            self._GenericTransportControl__delay_counter += 1
            if ((self._GenericTransportControl__delay_counter > 2) and ((self._GenericTransportControl__delay_counter % 2) == 0)):
                self._GenericTransportControl__parent.song().jump_by(self._GenericTransportControl__parent.song().signature_denominator)
        if self._GenericTransportControl__rwd_held:
            self._GenericTransportControl__delay_counter += 1
            if ((self._GenericTransportControl__delay_counter > 2) and ((self._GenericTransportControl__delay_counter % 2) == 0)):
                self._GenericTransportControl__parent.song().jump_by((-1 * self._GenericTransportControl__parent.song().signature_denominator))



    def disconnect(self):
        self._GenericTransportControl__parent.song().remove_is_playing_listener(self._GenericTransportControl__on_playing_status_changed)
        self._GenericTransportControl__parent.song().remove_record_mode_listener(self._GenericTransportControl__on_recording_status_changed)
        self._GenericTransportControl__parent.song().remove_loop_listener(self._GenericTransportControl__on_loop_status_changed)



    def __on_playing_status_changed(self):
        if (not (self._GenericTransportControl__controllers['PLAY'] == -1)):
            status = STATUS_OFF
            if self._GenericTransportControl__parent.song().is_playing:
                status = STATUS_ON
            self._GenericTransportControl__parent.send_midi((CC_STATUS,
             self._GenericTransportControl__controllers['PLAY'],
             status))



    def __on_recording_status_changed(self):
        if (not (self._GenericTransportControl__controllers['REC'] == -1)):
            status = STATUS_OFF
            if self._GenericTransportControl__parent.song().record_mode:
                status = STATUS_ON
            self._GenericTransportControl__parent.send_midi((CC_STATUS,
             self._GenericTransportControl__controllers['REC'],
             status))



    def __on_loop_status_changed(self):
        if (not (self._GenericTransportControl__controllers['LOOP'] == -1)):
            status = STATUS_OFF
            if self._GenericTransportControl__parent.song().loop:
                status = STATUS_ON
            self._GenericTransportControl__parent.send_midi((CC_STATUS,
             self._GenericTransportControl__controllers['LOOP'],
             status))




# local variables:
# tab-width: 4
