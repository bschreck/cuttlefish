# emacs-mode: -*- python-*-
import Live
from RemoteSLComponent import RemoteSLComponent
from consts import *
class EffectController(RemoteSLComponent):
    __module__ = __name__
    __doc__ = "Representing the 'left side' of the RemoteSL:\n  The upper two button rows with the encoders, and the row with the poties and drum pads.\n  \n  Only the First Button row with the Encoders are handled by this script. The rest will\n  be forwarded to Live, so that it can be freely mapped with the RemoteMapper.\n  \n  The encoders and buttons are used to control devices in Live, by attaching to\n  the selected one in Live, when the selection is not locked...\n  Switching through more than 8 parameters is done by pressing the up/down bottons next \n  to the left display. This will then shift the selected parameters by 8.\n  "

    def __init__(self, remote_sl_parent, display_controller):
        RemoteSLComponent.__init__(self, remote_sl_parent)
        self._EffectController__display_controller = display_controller
        self._EffectController__parent = remote_sl_parent
        self._EffectController__assigned_device = self._EffectController__parent.song().appointed_device
        self._EffectController__last_selected_track = None
        self._EffectController__assigned_device_is_locked = False
        self._EffectController__strips = [ EffectChannelStrip(self) for x in range(NUM_CONTROLS_PER_ROW) ]
        self._EffectController__bank = 0
        self._EffectController__show_bank = False
        self._EffectController__reassign_strips()



    def disconnect(self):
        pass


    def receive_midi_cc(self, cc_no, cc_value):
        if (cc_no in fx_display_button_ccs):
            self._EffectController__handle_page_up_down_ccs(cc_no, cc_value)
        elif (cc_no in fx_select_button_ccs):
            self._EffectController__handle_select_button_ccs(cc_no, cc_value)
        elif (cc_no in fx_upper_button_row_ccs):
            strip = self._EffectController__strips[(cc_no - FX_UPPER_BUTTON_ROW_BASE_CC)]
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                strip.on_button_pressed()
        elif (cc_no in fx_encoder_row_ccs):
            strip = self._EffectController__strips[(cc_no - FX_ENCODER_ROW_BASE_CC)]
            strip.on_encoder_moved(cc_value)
        elif (cc_no in fx_lower_button_row_ccs):
            assert False, 'Lower Button CCS should be passed to Live!'
        elif (cc_no in fx_poti_row_ccs):
            assert False, 'Poti CCS should be passed to Live!'
        else:
            assert False, 'unknown FX midi message'



    def receive_midi_note(self, note, velocity):
        if (note in fx_drum_pad_row_notes):
            assert False, 'DrumPad CCS should be passed to Live!'
        else:
            assert False, 'unknown FX midi message'



    def build_midi_map(self, script_handle, midi_map_handle):
        for s in self._EffectController__strips:
            cc_no = (FX_ENCODER_ROW_BASE_CC + self._EffectController__strips.index(s))
            if s.assigned_parameter():
                map_mode = Live.MidiMap.MapMode.relative_smooth_signed_bit
                parameter = s.assigned_parameter()
                Live.MidiMap.map_midi_cc(midi_map_handle, parameter, SL_MIDI_CHANNEL, cc_no, map_mode)
            else:
                Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, SL_MIDI_CHANNEL, cc_no)

        for cc_no in fx_forwarded_ccs:
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, SL_MIDI_CHANNEL, cc_no)

        for note in fx_forwarded_notes:
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, SL_MIDI_CHANNEL, note)




    def refresh_state(self):
        self._EffectController__update_select_row_leds()



    def __reassign_strips(self):
        if (not (self._EffectController__assigned_device == None)):
            param_index = 0
            param_names = []
            parameters = []
            for s in self._EffectController__strips:
                param = None
                name = ''
                new_index = (param_index + (self._EffectController__bank * 8))
                if (new_index < len(self._EffectController__assigned_device.parameters)):
                    param = self._EffectController__assigned_device.parameters[new_index]
                if param:
                    name = param.name
                s.set_assigned_parameter(param)
                parameters.append(param)
                param_names.append(name)
                param_index += 1

            self._EffectController__report_bank()
        else:
            for s in self._EffectController__strips:
                s.set_assigned_parameter(None)

            param_names = ['Please select a Device in Live to edit it...']
            parameters = [ None for x in range(NUM_CONTROLS_PER_ROW) ]
        self._EffectController__display_controller.setup_left_display(param_names, parameters)
        self.request_rebuild_midi_map()



    def __handle_page_up_down_ccs(self, cc_no, cc_value):
        new_bank = self._EffectController__bank
        if (cc_no == FX_DISPLAY_PAGE_UP):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                if self._EffectController__assigned_device:
                    param_count = len(list(self._EffectController__assigned_device.parameters))
                    bank_count = (param_count / 8)
                    if (not ((param_count % 8) == 0)):
                        bank_count += 1
                    if ((self._EffectController__bank + 1) < bank_count):
                        new_bank = (self._EffectController__bank + 1)
        elif (cc_no == FX_DISPLAY_PAGE_DOWN):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                if self._EffectController__assigned_device:
                    if (self._EffectController__bank > 0):
                        new_bank = (self._EffectController__bank - 1)
        else:
            assert False, 'unknown Display midi message'
        if (not (self._EffectController__bank == new_bank)):
            self._EffectController__show_bank = True
            if (not self._EffectController__assigned_device_is_locked):
                self._EffectController__bank = new_bank
                self._EffectController__reassign_strips()
            else:
                self._EffectController__assigned_device.store_chosen_bank(self._EffectController__parent.instance_identifier(), new_bank)



    def __handle_select_button_ccs(self, cc_no, cc_value):
        if (cc_no == FX_SELECT_FIRST_BUTTON_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self._EffectController__parent.toggle_lock()
        elif (cc_no == FX_SELECT_ENCODER_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                new_index = min((len(self.song().scenes) - 1), max(0, (list(self.song().scenes).index(self.song().view.selected_scene) - 1)))
                self.song().view.selected_scene = self.song().scenes[new_index]
        elif (cc_no == FX_SELECT_SECOND_BUTTON_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                new_index = min((len(self.song().scenes) - 1), max(0, (list(self.song().scenes).index(self.song().view.selected_scene) + 1)))
                self.song().view.selected_scene = self.song().scenes[new_index]
        elif (cc_no == FX_SELECT_POTIE_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self.song().view.selected_scene.fire_as_selected()
        elif (cc_no == FX_SELECT_DRUM_PAD_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self.song().stop_all_clips()
        else:
            assert False, 'unknown select row midi message'



    def __update_select_row_leds(self):
        if self._EffectController__assigned_device_is_locked:
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             FX_SELECT_FIRST_BUTTON_ROW,
             CC_VAL_BUTTON_PRESSED))
        else:
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             FX_SELECT_FIRST_BUTTON_ROW,
             CC_VAL_BUTTON_RELEASED))



    def lock_to_device(self, device):
        if device:
            self._EffectController__assigned_device_is_locked = True
            if (not (device == self._EffectController__assigned_device)):
                self._EffectController__bank = 0
            self._EffectController__show_bank = False
            self._EffectController__assigned_device = device
            self._EffectController__update_select_row_leds()
            self._EffectController__reassign_strips()



    def unlock_from_device(self, device):
        if (device and (device == self._EffectController__assigned_device)):
            self._EffectController__assigned_device_is_locked = False
            self._EffectController__update_select_row_leds()
            if (not (self._EffectController__parent.song().appointed_device == self._EffectController__assigned_device)):
                self._EffectController__reassign_strips()



    def set_appointed_device(self, device):
        if self._EffectController__assigned_device_is_locked:
            self._EffectController__assigned_device_is_locked = False
        if (not (device == self._EffectController__assigned_device)):
            self._EffectController__bank = 0
        self._EffectController__show_bank = False
        self._EffectController__assigned_device = device
        self._EffectController__update_select_row_leds()
        self._EffectController__reassign_strips()



    def __report_bank(self):
        if self._EffectController__show_bank:
            self._EffectController__show_bank = False
            self._EffectController__show_bank_select(('Bank' + str((self._EffectController__bank + 1))))



    def __show_bank_select(self, bank_name):
        if self._EffectController__assigned_device:
            self._EffectController__parent.show_message(str(((self._EffectController__assigned_device.name + ' Bank: ') + bank_name)))



    def restore_bank(self, bank):
        if self._EffectController__assigned_device_is_locked:
            self._EffectController__bank = bank
            self._EffectController__reassign_strips()



class EffectChannelStrip:
    __module__ = __name__
    __doc__ = 'Represents one of the 8 strips in the Effect controls that we use for parameter \n  controlling (one button, one encoder)\n  '

    def __init__(self, mixer_controller_parent):
        self._EffectChannelStrip__mixer_controller = mixer_controller_parent
        self._EffectChannelStrip__assigned_parameter = None



    def assigned_parameter(self):
        return self._EffectChannelStrip__assigned_parameter



    def set_assigned_parameter(self, parameter):
        self._EffectChannelStrip__assigned_parameter = parameter



    def on_button_pressed(self):
        if self._EffectChannelStrip__assigned_parameter:
            if self._EffectChannelStrip__assigned_parameter.is_quantized:
                if ((self._EffectChannelStrip__assigned_parameter.value + 1) > self._EffectChannelStrip__assigned_parameter.max):
                    self._EffectChannelStrip__assigned_parameter.value = self._EffectChannelStrip__assigned_parameter.min
                else:
                    self._EffectChannelStrip__assigned_parameter.value = (self._EffectChannelStrip__assigned_parameter.value + 1)
            else:
                self._EffectChannelStrip__assigned_parameter.value = self._EffectChannelStrip__assigned_parameter.default_value



    def on_encoder_moved(self, cc_value):
        assert (self._EffectChannelStrip__assigned_parameter is None), 'should only be reached when the encoder was not realtime mapped '




# local variables:
# tab-width: 4
