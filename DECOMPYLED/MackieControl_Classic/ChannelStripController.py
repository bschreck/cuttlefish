# emacs-mode: -*- python-*-
from MackieControlComponent import *
from _Generic.Devices import *
class ChannelStripController(MackieControlComponent):
    __module__ = __name__
    __doc__ = '\n     Controls all channel-strips of the Mackie Control and controller extensions \n     (Mackie Control XTs) if available: Maps and controls the faders, VPots and the \n     displays depending on the assignemnt modes (Vol_Pan, PlugIn, IO, Send) and \n     edit and flip mode.\n     \n     stack_offset vs. strip_index vs. bank_channel_offset:\n     \n     When using multiple sets of channel strips (stacking them), we will still only\n     have one ChannelStripController which rules them all. \n     To identify and seperate them, the implementation uses 3 different kind of \n     indices or offsets:\n    \n     - strip_index: is the index of a channel_strip within its controller box, \n       so strip no 1 on an extension (XT) and strip number one on the \'main\' Mackie \n       will both have a strip_index of 1.\n       We need to preserve this index, because every device (extension or main controller\n       will use a unique MIDI port to send out its MIDI messages which uses the \n       strip_index, encoded into the MIDI messages channel, to tell the hardware which \n       channel on the controller is meant.\n       \n     - stack_offset: descibes how many channels are left to the device that a\n       channel_strip belongs to. For example: You have 3 Mackies: First, a XT, then\n       the main Mackie, then another XT. \n       The first XT will have the stack_index 0, the main Mackie, the stack_index 8,\n       because 8 faders are on present before it. The second XT has a stack_index of 16\n       \n     - bank_cha_offset: this shifts all available channel strips within all the tracks\n       that should be controlled. For example: If you have a song with 32 tracks, and \n       a main Mackie Control + a XT on the right, then you want to shift the first fader\n       of the main Mackie to Track 16, to be able to control Track 16 to 32. \n       \n     The master channel strip is hardcoded and not in the list of "normal" channel_strips, \n     because its always mapped to the master_volume.\n  '

    def __init__(self, main_script, channel_strips, master_strip, main_display_controller):
        MackieControlComponent.__init__(self, main_script)
        self._ChannelStripController__left_extensions = []
        self._ChannelStripController__right_extensions = []
        self._ChannelStripController__own_channel_strips = channel_strips
        self._ChannelStripController__master_strip = master_strip
        self._ChannelStripController__channel_strips = channel_strips
        self._ChannelStripController__main_display_controller = main_display_controller
        self._ChannelStripController__meters_enabled = False
        self._ChannelStripController__assignment_mode = CSM_VOLPAN
        self._ChannelStripController__sub_mode_in_io_mode = CSM_IO_FIRST_MODE
        self._ChannelStripController__plugin_mode = PCM_DEVICES
        self._ChannelStripController__plugin_mode_offsets = [ 0 for x in range(PCM_NUMMODES) ]
        self._ChannelStripController__chosen_plugin = None
        self._ChannelStripController__ordered_plugin_parameters = []
        self._ChannelStripController__displayed_plugins = []
        self._ChannelStripController__last_attached_selected_track = None
        self._ChannelStripController__send_mode_offset = 0
        self._ChannelStripController__flip = False
        self._ChannelStripController__view_returns = False
        self._ChannelStripController__bank_cha_offset = 0
        self._ChannelStripController__bank_cha_offset_returns = 0
        self._ChannelStripController__within_track_added_or_deleted = False
        self.song().add_tracks_listener(self._ChannelStripController__on_tracks_added_or_deleted)
        self.song().view.add_selected_track_listener(self._ChannelStripController__on_selected_track_changed)
        for t in (self.song().tracks + self.song().return_tracks):
            if (not t.solo_has_listener(self._ChannelStripController__update_rude_solo_led)):
                t.add_solo_listener(self._ChannelStripController__update_rude_solo_led)
            if (not t.has_audio_output_has_listener(self._ChannelStripController__on_any_tracks_output_type_changed)):
                t.add_has_audio_output_listener(self._ChannelStripController__on_any_tracks_output_type_changed)

        self._ChannelStripController__on_selected_track_changed()
        for s in self._ChannelStripController__own_channel_strips:
            s.set_channel_strip_controller(self)

        self._ChannelStripController__reassign_channel_strip_offsets()
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)



    def destroy(self):
        self.song().remove_tracks_listener(self._ChannelStripController__on_tracks_added_or_deleted)
        self.song().view.remove_selected_track_listener(self._ChannelStripController__on_selected_track_changed)
        for t in (self.song().tracks + self.song().return_tracks):
            if t.solo_has_listener(self._ChannelStripController__update_rude_solo_led):
                t.remove_solo_listener(self._ChannelStripController__update_rude_solo_led)
            if t.has_audio_output_has_listener(self._ChannelStripController__on_any_tracks_output_type_changed):
                t.remove_has_audio_output_listener(self._ChannelStripController__on_any_tracks_output_type_changed)

        st = self._ChannelStripController__last_attached_selected_track
        if (st and st.devices_has_listener(self._ChannelStripController__on_selected_device_chain_changed)):
            st.remove_devices_listener(self._ChannelStripController__on_selected_device_chain_changed)
        for note in channel_strip_assignment_switch_ids:
            self.send_midi((NOTE_ON_STATUS,
             note,
             BUTTON_STATE_OFF))

        for note in channel_strip_control_switch_ids:
            self.send_midi((NOTE_ON_STATUS,
             note,
             BUTTON_STATE_OFF))

        self.send_midi((NOTE_ON_STATUS,
         SELECT_RUDE_SOLO,
         BUTTON_STATE_OFF))
        self.send_midi((CC_STATUS,
         75,
         g7_seg_led_conv_table[' ']))
        self.send_midi((CC_STATUS,
         74,
         g7_seg_led_conv_table[' ']))
        MackieControlComponent.destroy(self)



    def set_controller_extensions(self, left_extensions, right_extensions):
        """ Called from the main script (after all scripts where initialized), to let us 
        know where and how many MackieControlXT are installed. 
        There exists only one ChannelStripController, so we will take care about the 
        extensions channel strips
    """
        self._ChannelStripController__left_extensions = left_extensions
        self._ChannelStripController__right_extensions = right_extensions
        self._ChannelStripController__channel_strips = []
        stack_offset = 0
        for le in left_extensions:
            for s in le.channel_strips():
                self._ChannelStripController__channel_strips.append(s)
                s.set_stack_offset(stack_offset)

            stack_offset += NUM_CHANNEL_STRIPS

        for s in self._ChannelStripController__own_channel_strips:
            self._ChannelStripController__channel_strips.append(s)
            s.set_stack_offset(stack_offset)

        stack_offset += NUM_CHANNEL_STRIPS
        for re in right_extensions:
            for s in re.channel_strips():
                self._ChannelStripController__channel_strips.append(s)
                s.set_stack_offset(stack_offset)

            stack_offset += NUM_CHANNEL_STRIPS

        for s in self._ChannelStripController__channel_strips:
            s.set_channel_strip_controller(self)

        self.refresh_state()



    def refresh_state(self):
        self._ChannelStripController__update_assignment_mode_leds()
        self._ChannelStripController__update_assignment_display()
        self._ChannelStripController__update_rude_solo_led()
        self._ChannelStripController__reassign_channel_strip_offsets()
        self._ChannelStripController__on_flip_changed()
        self._ChannelStripController__update_view_returns_mode()



    def request_rebuild_midi_map(self):
        """ Overridden to call also the extensions request_rebuild_midi_map"""
        MackieControlComponent.request_rebuild_midi_map(self)
        for ex in (self._ChannelStripController__left_extensions + self._ChannelStripController__right_extensions):
            ex.request_rebuild_midi_map()




    def on_update_display_timer(self):
        self._ChannelStripController__update_channel_strip_strings()



    def toggle_meter_mode(self):
        """ called from the main script when the display toggle button was pressed """
        self._ChannelStripController__meters_enabled = (not self._ChannelStripController__meters_enabled)
        self._ChannelStripController__apply_meter_mode()



    def handle_assignment_switch_ids(self, switch_id, value):
        if (switch_id == SID_ASSIGNMENT_IO):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__set_assignment_mode(CSM_IO)
        elif (switch_id == SID_ASSIGNMENT_SENDS):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__set_assignment_mode(CSM_SENDS)
        elif (switch_id == SID_ASSIGNMENT_PAN):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__set_assignment_mode(CSM_VOLPAN)
        elif (switch_id == SID_ASSIGNMENT_PLUG_INS):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__set_assignment_mode(CSM_PLUGINS)
        elif (switch_id == SID_ASSIGNMENT_EQ):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__switch_to_prev_page()
        elif (switch_id == SID_ASSIGNMENT_DYNAMIC):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__switch_to_next_page()
        elif (switch_id == SID_FADERBANK_PREV_BANK):
            if (value == BUTTON_PRESSED):
                if self.shift_is_pressed():
                    self._ChannelStripController__set_channel_offset(0)
                else:
                    self._ChannelStripController__set_channel_offset((self._ChannelStripController__strip_offset() - len(self._ChannelStripController__channel_strips)))
        elif (switch_id == SID_FADERBANK_NEXT_BANK):
            if (value == BUTTON_PRESSED):
                if self.shift_is_pressed():
                    last_possible_offset = ((((self._ChannelStripController__controlled_num_of_tracks() - self._ChannelStripController__strip_offset()) / len(self._ChannelStripController__channel_strips)) * len(self._ChannelStripController__channel_strips)) + self._ChannelStripController__strip_offset())
                    if (last_possible_offset == self._ChannelStripController__controlled_num_of_tracks()):
                        last_possible_offset -= len(self._ChannelStripController__channel_strips)
                    self._ChannelStripController__set_channel_offset(last_possible_offset)
                elif (self._ChannelStripController__strip_offset() < (self._ChannelStripController__controlled_num_of_tracks() - len(self._ChannelStripController__channel_strips))):
                    self._ChannelStripController__set_channel_offset((self._ChannelStripController__strip_offset() + len(self._ChannelStripController__channel_strips)))
        elif (switch_id == SID_FADERBANK_PREV_CH):
            if (value == BUTTON_PRESSED):
                if self.shift_is_pressed():
                    self._ChannelStripController__set_channel_offset(0)
                else:
                    self._ChannelStripController__set_channel_offset((self._ChannelStripController__strip_offset() - 1))
        elif (switch_id == SID_FADERBANK_NEXT_CH):
            if (value == BUTTON_PRESSED):
                if self.shift_is_pressed():
                    self._ChannelStripController__set_channel_offset((self._ChannelStripController__controlled_num_of_tracks() - len(self._ChannelStripController__channel_strips)))
                elif (self._ChannelStripController__strip_offset() < (self._ChannelStripController__controlled_num_of_tracks() - len(self._ChannelStripController__channel_strips))):
                    self._ChannelStripController__set_channel_offset((self._ChannelStripController__strip_offset() + 1))
        elif (switch_id == SID_FADERBANK_FLIP):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__toggle_flip()
        elif (switch_id == SID_FADERBANK_EDIT):
            if (value == BUTTON_PRESSED):
                self._ChannelStripController__toggle_view_returns()



    def handle_vpot_rotation(self, strip_index, stack_offset, cc_value):
        """ forwarded to us by the channel_strips """
        if (self._ChannelStripController__assignment_mode == CSM_IO):
            if (cc_value >= 64):
                direction = -1
            else:
                direction = 1
            channel_strip = self._ChannelStripController__channel_strips[(stack_offset + strip_index)]
            current_routing = self._ChannelStripController__routing_target(channel_strip)
            available_routings = self._ChannelStripController__available_routing_targets(channel_strip)
            if (current_routing and available_routings):
                if (current_routing in available_routings):
                    i = list(available_routings).index(current_routing)
                    if (direction == 1):
                        new_i = min((len(available_routings) - 1), (i + direction))
                    else:
                        new_i = max(0, (i + direction))
                    new_routing = available_routings[new_i]
                elif len(available_routings):
                    new_routing = available_routings[0]
                self._ChannelStripController__set_routing_target(channel_strip, new_routing)
        elif (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
            pass
        else:
            channel_strip = self._ChannelStripController__channel_strips[(stack_offset + strip_index)]
            assert ((not channel_strip.assigned_track()) or (not channel_strip.assigned_track().has_audio_output)), 'in every other mode, the midimap should handle the messages'



    def handle_fader_touch(self, strip_offset, stack_offset, touched):
        """ forwarded to us by the channel_strips """
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=True)



    def handle_pressed_v_pot(self, strip_index, stack_offset):
        """ forwarded to us by the channel_strips """
        if ((self._ChannelStripController__assignment_mode == CSM_VOLPAN) or ((self._ChannelStripController__assignment_mode == CSM_SENDS) or ((self._ChannelStripController__assignment_mode == CSM_PLUGINS) and (self._ChannelStripController__plugin_mode == PCM_PARAMETERS)))):
            if ((stack_offset + strip_index) in range(0, len(self._ChannelStripController__channel_strips))):
                param = self._ChannelStripController__channel_strips[(stack_offset + strip_index)].v_pot_parameter()
            if param:
                if param.is_quantized:
                    if ((param.value + 1) > param.max):
                        param.value = param.min
                    else:
                        param.value = (param.value + 1)
                else:
                    param.value = param.default_value
        elif ((self._ChannelStripController__assignment_mode == CSM_PLUGINS) and (self._ChannelStripController__plugin_mode == PCM_DEVICES)):
            device_index = ((strip_index + stack_offset) + self._ChannelStripController__plugin_mode_offsets[PCM_DEVICES])
            if ((device_index >= 0) and (device_index < len(self.song().view.selected_track.devices))):
                if (self._ChannelStripController__chosen_plugin != None):
                    self._ChannelStripController__chosen_plugin.remove_parameters_listener(self._ChannelStripController__on_parameter_list_of_chosen_plugin_changed)
                self._ChannelStripController__chosen_plugin = self.song().view.selected_track.devices[device_index]
                if (self._ChannelStripController__chosen_plugin != None):
                    self._ChannelStripController__chosen_plugin.add_parameters_listener(self._ChannelStripController__on_parameter_list_of_chosen_plugin_changed)
                self._ChannelStripController__reorder_parameters()
                self._ChannelStripController__plugin_mode_offsets[PCM_PARAMETERS] = 0
                self._ChannelStripController__set_plugin_mode(PCM_PARAMETERS)



    def __strip_offset(self):
        """ return the bank_channel offset depending if we are in return mode or not
    """
        if self._ChannelStripController__view_returns:
            return self._ChannelStripController__bank_cha_offset_returns
        else:
            return self._ChannelStripController__bank_cha_offset



    def __controlled_num_of_tracks(self):
        """ return the number of tracks, depending on if we are in send_track 
        mode or normal track mode
    """
        if self._ChannelStripController__view_returns:
            return len(self.song().return_tracks)
        else:
            return len(self.song().tracks)



    def __send_parameter(self, strip_index, stack_index):
        """ Return the send parameter that is assigned to the given channel strip
    """
        assert (self._ChannelStripController__assignment_mode == CSM_SENDS)
        send_index = ((strip_index + stack_index) + self._ChannelStripController__send_mode_offset)
        if (send_index < len(self.song().view.selected_track.mixer_device.sends)):
            p = self.song().view.selected_track.mixer_device.sends[send_index]
            return (p,
             p.name)
        return (None,
         None)



    def __plugin_parameter(self, strip_index, stack_index):
        """ Return the parameter that is assigned to the given channel strip
    """
        assert (self._ChannelStripController__assignment_mode == CSM_PLUGINS)
        if (self._ChannelStripController__plugin_mode == PCM_DEVICES):
            return (None,
             None)
        elif (self._ChannelStripController__plugin_mode == PCM_PARAMETERS):
            assert self._ChannelStripController__chosen_plugin
            parameters = self._ChannelStripController__ordered_plugin_parameters
            parameter_index = ((strip_index + stack_index) + self._ChannelStripController__plugin_mode_offsets[PCM_PARAMETERS])
            if ((parameter_index >= 0) and (parameter_index < len(parameters))):
                return parameters[parameter_index]
            else:
                return (None,
                 None)
        else:
            assert 0



    def __any_slider_is_touched(self):
        for s in self._ChannelStripController__channel_strips:
            if s.is_touched():
                return True

        return False



    def __can_flip(self):
        if ((self._ChannelStripController__assignment_mode == CSM_PLUGINS) and (self._ChannelStripController__plugin_mode == PCM_DEVICES)):
            return False
        elif (self._ChannelStripController__assignment_mode == CSM_IO):
            return False
        return True



    def __can_switch_to_prev_page(self):
        """ return true if pressing the "next" button will have any effect """
        if (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
            return (self._ChannelStripController__plugin_mode_offsets[self._ChannelStripController__plugin_mode] > 0)
        elif (self._ChannelStripController__assignment_mode == CSM_SENDS):
            return (self._ChannelStripController__send_mode_offset > 0)
        else:
            return False



    def __can_switch_to_next_page(self):
        """ return true if pressing the "prev" button will have any effect """
        if (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
            sel_track = self.song().view.selected_track
            if (self._ChannelStripController__plugin_mode == PCM_DEVICES):
                return ((self._ChannelStripController__plugin_mode_offsets[PCM_DEVICES] + len(self._ChannelStripController__channel_strips)) < len(sel_track.devices))
            elif (self._ChannelStripController__plugin_mode == PCM_PARAMETERS):
                assert self._ChannelStripController__chosen_plugin
                parameters = self._ChannelStripController__ordered_plugin_parameters
                return ((self._ChannelStripController__plugin_mode_offsets[PCM_PARAMETERS] + len(self._ChannelStripController__channel_strips)) < len(parameters))
            else:
                assert 0
        elif (self._ChannelStripController__assignment_mode == CSM_SENDS):
            return ((self._ChannelStripController__send_mode_offset + len(self._ChannelStripController__channel_strips)) < len(self.song().return_tracks))
        else:
            return False



    def __available_routing_targets(self, channel_strip):
        assert (self._ChannelStripController__assignment_mode == CSM_IO)
        t = channel_strip.assigned_track()
        if t:
            if (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_MAIN):
                return t.input_routings
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_SUB):
                return t.input_sub_routings
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_MAIN):
                return t.output_routings
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_SUB):
                return t.output_sub_routings
            else:
                assert 0
        else:
            return None



    def __routing_target(self, channel_strip):
        assert (self._ChannelStripController__assignment_mode == CSM_IO)
        t = channel_strip.assigned_track()
        if t:
            if (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_MAIN):
                return t.current_input_routing
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_SUB):
                return t.current_input_sub_routing
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_MAIN):
                return t.current_output_routing
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_SUB):
                return t.current_output_sub_routing
            else:
                assert 0
        else:
            return None



    def __set_routing_target(self, channel_strip, target_string):
        assert (self._ChannelStripController__assignment_mode == CSM_IO)
        t = channel_strip.assigned_track()
        if t:
            if (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_MAIN):
                t.current_input_routing = target_string
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_SUB):
                t.current_input_sub_routing = target_string
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_MAIN):
                t.current_output_routing = target_string
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_SUB):
                t.current_output_sub_routing = target_string
            else:
                assert 0



    def __set_channel_offset(self, new_offset):
        """ Set and validate a new channel_strip offset, which shifts all available channel
        strips within all the available tracks or reutrn tracks
    """
        if (new_offset < 0):
            new_offset = 0
        elif (new_offset >= self._ChannelStripController__controlled_num_of_tracks()):
            new_offset = (self._ChannelStripController__controlled_num_of_tracks() - 1)
        if self._ChannelStripController__view_returns:
            self._ChannelStripController__bank_cha_offset_returns = new_offset
        else:
            self._ChannelStripController__bank_cha_offset = new_offset
        self._ChannelStripController__main_display_controller.set_channel_offset(new_offset)
        self._ChannelStripController__reassign_channel_strip_offsets()
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
        self._ChannelStripController__update_channel_strip_strings()
        self.request_rebuild_midi_map()



    def __set_assignment_mode(self, mode):
        for plugin in self._ChannelStripController__displayed_plugins:
            if (plugin != None):
                plugin.remove_name_listener(self._ChannelStripController__update_plugin_names)

        self._ChannelStripController__displayed_plugins = []
        if (mode == CSM_PLUGINS):
            self._ChannelStripController__assignment_mode = mode
            self._ChannelStripController__main_display_controller.set_show_parameter_names(True)
            self._ChannelStripController__set_plugin_mode(PCM_DEVICES)
        elif (mode == CSM_SENDS):
            self._ChannelStripController__main_display_controller.set_show_parameter_names(True)
            self._ChannelStripController__assignment_mode = mode
        else:
            if (mode == CSM_IO):
                for s in self._ChannelStripController__channel_strips:
                    s.unlight_vpot_leds()

            self._ChannelStripController__main_display_controller.set_show_parameter_names(False)
            if (self._ChannelStripController__assignment_mode != mode):
                self._ChannelStripController__assignment_mode = mode
            elif (self._ChannelStripController__assignment_mode == CSM_IO):
                self._ChannelStripController__switch_to_next_io_mode()
        self._ChannelStripController__update_assignment_mode_leds()
        self._ChannelStripController__update_assignment_display()
        self._ChannelStripController__apply_meter_mode()
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
        self._ChannelStripController__update_channel_strip_strings()
        self._ChannelStripController__update_page_switch_leds()
        if (mode == CSM_PLUGINS):
            self._ChannelStripController__update_vpot_leds_in_plugins_device_choose_mode()
        self._ChannelStripController__update_flip_led()
        self.request_rebuild_midi_map()



    def __set_plugin_mode(self, new_mode):
        """ Set a new plugin sub-mode, which can be:
        1. Choosing the device to control (PCM_DEVICES)
        2. Controlling the chosen devices parameters (PCM_PARAMETERS)
    """
        assert ((new_mode >= 0) and (new_mode < PCM_NUMMODES))
        if (self._ChannelStripController__plugin_mode != new_mode):
            self._ChannelStripController__plugin_mode = new_mode
            self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
            self.request_rebuild_midi_map()
            if (self._ChannelStripController__plugin_mode == PCM_DEVICES):
                self._ChannelStripController__update_vpot_leds_in_plugins_device_choose_mode()
            else:
                for plugin in self._ChannelStripController__displayed_plugins:
                    if (plugin != None):
                        plugin.remove_name_listener(self._ChannelStripController__update_plugin_names)

                self._ChannelStripController__displayed_plugins = []
            self._ChannelStripController__update_page_switch_leds()
            self._ChannelStripController__update_flip_led()
            self._ChannelStripController__update_page_switch_leds()



    def __switch_to_prev_page(self):
        """ Switch to the previous page in the non track strip modes (choosing plugs, or
        controlling devices)
    """
        if self._ChannelStripController__can_switch_to_prev_page():
            if (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
                self._ChannelStripController__plugin_mode_offsets[self._ChannelStripController__plugin_mode] -= len(self._ChannelStripController__channel_strips)
                if (self._ChannelStripController__plugin_mode == PCM_DEVICES):
                    self._ChannelStripController__update_vpot_leds_in_plugins_device_choose_mode()
            elif (self._ChannelStripController__assignment_mode == CSM_SENDS):
                self._ChannelStripController__send_mode_offset -= len(self._ChannelStripController__channel_strips)
            self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
            self._ChannelStripController__update_channel_strip_strings()
            self._ChannelStripController__update_page_switch_leds()
            self.request_rebuild_midi_map()



    def __switch_to_next_page(self):
        """ Switch to the next page in the non track strip modes (choosing plugs, or
        controlling devices)
    """
        if self._ChannelStripController__can_switch_to_next_page():
            if (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
                self._ChannelStripController__plugin_mode_offsets[self._ChannelStripController__plugin_mode] += len(self._ChannelStripController__channel_strips)
                if (self._ChannelStripController__plugin_mode == PCM_DEVICES):
                    self._ChannelStripController__update_vpot_leds_in_plugins_device_choose_mode()
            elif (self._ChannelStripController__assignment_mode == CSM_SENDS):
                self._ChannelStripController__send_mode_offset += len(self._ChannelStripController__channel_strips)
            else:
                assert 0
            self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
            self._ChannelStripController__update_channel_strip_strings()
            self._ChannelStripController__update_page_switch_leds()
            self.request_rebuild_midi_map()



    def __switch_to_next_io_mode(self):
        """ Step through the available IO modes (In/OutPut//Main/Sub)
    """
        self._ChannelStripController__sub_mode_in_io_mode += 1
        if (self._ChannelStripController__sub_mode_in_io_mode > CSM_IO_LAST_MODE):
            self._ChannelStripController__sub_mode_in_io_mode = CSM_IO_FIRST_MODE



    def __reassign_channel_strip_offsets(self):
        """ Update the channel strips bank_channel offset
    """
        for s in self._ChannelStripController__channel_strips:
            s.set_bank_and_channel_offset(self._ChannelStripController__strip_offset(), self._ChannelStripController__view_returns, self._ChannelStripController__within_track_added_or_deleted)




    def __reassign_channel_strip_parameters(self, for_display_only):
        """ Reevaluate all v-pot/fader -> parameter assignments 
    """
        display_parameters = []
        for s in self._ChannelStripController__channel_strips:
            vpot_param = (None,
             None)
            slider_param = (None,
             None)
            vpot_display_mode = VPOT_DISPLAY_SINGLE_DOT
            slider_display_mode = VPOT_DISPLAY_SINGLE_DOT
            if (self._ChannelStripController__assignment_mode == CSM_VOLPAN):
                if (s.assigned_track() and s.assigned_track().has_audio_output):
                    vpot_param = (s.assigned_track().mixer_device.panning,
                     'Pan')
                    vpot_display_mode = VPOT_DISPLAY_BOOST_CUT
                    slider_param = (s.assigned_track().mixer_device.volume,
                     'Volume')
                    slider_display_mode = VPOT_DISPLAY_WRAP
            elif (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
                vpot_param = self._ChannelStripController__plugin_parameter(s.strip_index(), s.stack_offset())
                vpot_display_mode = VPOT_DISPLAY_WRAP
                if (s.assigned_track() and s.assigned_track().has_audio_output):
                    slider_param = (s.assigned_track().mixer_device.volume,
                     'Volume')
                    slider_display_mode = VPOT_DISPLAY_WRAP
            elif (self._ChannelStripController__assignment_mode == CSM_SENDS):
                vpot_param = self._ChannelStripController__send_parameter(s.strip_index(), s.stack_offset())
                vpot_display_mode = VPOT_DISPLAY_WRAP
                if (s.assigned_track() and s.assigned_track().has_audio_output):
                    slider_param = (s.assigned_track().mixer_device.volume,
                     'Volume')
                    slider_display_mode = VPOT_DISPLAY_WRAP
            elif (self._ChannelStripController__assignment_mode == CSM_IO):
                if (s.assigned_track() and s.assigned_track().has_audio_output):
                    slider_param = (s.assigned_track().mixer_device.volume,
                     'Volume')
            if (self._ChannelStripController__flip and self._ChannelStripController__can_flip()):
                if self._ChannelStripController__any_slider_is_touched():
                    display_parameters.append(vpot_param)
                else:
                    display_parameters.append(slider_param)
                if (not for_display_only):
                    s.set_v_pot_parameter(slider_param[0], slider_display_mode)
                    s.set_fader_parameter(vpot_param[0])
            else:
                if self._ChannelStripController__any_slider_is_touched():
                    display_parameters.append(slider_param)
                else:
                    display_parameters.append(vpot_param)
                if (not for_display_only):
                    s.set_v_pot_parameter(vpot_param[0], vpot_display_mode)
                    s.set_fader_parameter(slider_param[0])

        self._ChannelStripController__main_display_controller.set_channel_offset(self._ChannelStripController__strip_offset())
        if len(display_parameters):
            self._ChannelStripController__main_display_controller.set_parameters(display_parameters)



    def __apply_meter_mode(self):
        """ Update the meter mode in the displays and channel strips """
        enabled = (self._ChannelStripController__meters_enabled and (self._ChannelStripController__assignment_mode is CSM_VOLPAN))
        for s in self._ChannelStripController__channel_strips:
            s.enable_meter_mode(enabled)

        self._ChannelStripController__main_display_controller.enable_meters(enabled)



    def __toggle_flip(self):
        """ En/Disable V-Pot / Fader flipping
    """
        if self._ChannelStripController__can_flip():
            self._ChannelStripController__flip = (not self._ChannelStripController__flip)
            self._ChannelStripController__on_flip_changed()



    def __toggle_view_returns(self):
        """ Toggle if we want to control the return tracks or normal tracks
    """
        self._ChannelStripController__view_returns = (not self._ChannelStripController__view_returns)
        self._ChannelStripController__update_view_returns_mode()



    def __update_assignment_mode_leds(self):
        """ Show which assignment mode is currently active """
        if (self._ChannelStripController__assignment_mode == CSM_IO):
            sid_on_switch = SID_ASSIGNMENT_IO
        elif (self._ChannelStripController__assignment_mode == CSM_SENDS):
            sid_on_switch = SID_ASSIGNMENT_SENDS
        elif (self._ChannelStripController__assignment_mode == CSM_VOLPAN):
            sid_on_switch = SID_ASSIGNMENT_PAN
        elif (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
            sid_on_switch = SID_ASSIGNMENT_PLUG_INS
        else:
            assert 0
            sid_on_switch = None
        for s in (SID_ASSIGNMENT_IO,
         SID_ASSIGNMENT_SENDS,
         SID_ASSIGNMENT_PAN,
         SID_ASSIGNMENT_PLUG_INS):
            if (s == sid_on_switch):
                self.send_midi((NOTE_ON_STATUS,
                 s,
                 BUTTON_STATE_ON))
            else:
                self.send_midi((NOTE_ON_STATUS,
                 s,
                 BUTTON_STATE_OFF))




    def __update_assignment_display(self):
        """ Cryptically label the current assignment mode in the 2char display above 
        the assignment buttons 
    """
        if (self._ChannelStripController__assignment_mode == CSM_VOLPAN):
            ass_string = ['P',
             'N']
        elif ((self._ChannelStripController__assignment_mode == CSM_PLUGINS) or (self._ChannelStripController__assignment_mode == CSM_SENDS)):
            if (self._ChannelStripController__last_attached_selected_track == self.song().master_track):
                ass_string = ['M',
                 'A']
            for t in self.song().return_tracks:
                if (t == self._ChannelStripController__last_attached_selected_track):
                    ass_string = ['R',
                     chr((ord('A') + list(self.song().return_tracks).index(t)))]
                    break

            for t in self.song().tracks:
                if (t == self._ChannelStripController__last_attached_selected_track):
                    ass_string = list(('%.2d' % min(99, (list(self.song().tracks).index(t) + 1))))
                    break

            assert ass_string
        elif (self._ChannelStripController__assignment_mode == CSM_IO):
            if (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_MAIN):
                ass_string = ['I',
                 "'"]
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_INPUT_SUB):
                ass_string = ['I',
                 ',']
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_MAIN):
                ass_string = ['0',
                 "'"]
            elif (self._ChannelStripController__sub_mode_in_io_mode == CSM_IO_MODE_OUTPUT_SUB):
                ass_string = ['0',
                 ',']
            else:
                assert 0
        else:
            assert 0
        self.send_midi((CC_STATUS,
         75,
         g7_seg_led_conv_table[ass_string[0]]))
        self.send_midi((CC_STATUS,
         74,
         g7_seg_led_conv_table[ass_string[1]]))



    def __update_rude_solo_led(self):
        any_track_soloed = False
        for t in (self.song().tracks + self.song().return_tracks):
            if t.solo:
                any_track_soloed = True
                break

        if any_track_soloed:
            self.send_midi((NOTE_ON_STATUS,
             SELECT_RUDE_SOLO,
             BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS,
             SELECT_RUDE_SOLO,
             BUTTON_STATE_OFF))



    def __update_page_switch_leds(self):
        """ visualize if the "prev" an "next" buttons can be pressed """
        if self._ChannelStripController__can_switch_to_prev_page():
            self.send_midi((NOTE_ON_STATUS,
             SID_ASSIGNMENT_EQ,
             BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS,
             SID_ASSIGNMENT_EQ,
             BUTTON_STATE_OFF))
        if self._ChannelStripController__can_switch_to_next_page():
            self.send_midi((NOTE_ON_STATUS,
             SID_ASSIGNMENT_DYNAMIC,
             BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS,
             SID_ASSIGNMENT_DYNAMIC,
             BUTTON_STATE_OFF))



    def __update_flip_led(self):
        if (self._ChannelStripController__flip and self._ChannelStripController__can_flip()):
            self.send_midi((NOTE_ON_STATUS,
             SID_FADERBANK_FLIP,
             BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS,
             SID_FADERBANK_FLIP,
             BUTTON_STATE_OFF))



    def __update_vpot_leds_in_plugins_device_choose_mode(self):
        """ To be called in assignment mode CSM_PLUGINS, submode PCM_DEVICES only:
        This will enlighten all poties which can be pressed to choose a device 
        for editing, and unlight all poties where pressing will have no effect
    """
        assert (self._ChannelStripController__assignment_mode == CSM_PLUGINS)
        assert (self._ChannelStripController__plugin_mode == PCM_DEVICES)
        sel_track = self.song().view.selected_track
        count = 0
        for s in self._ChannelStripController__channel_strips:
            offset = self._ChannelStripController__plugin_mode_offsets[self._ChannelStripController__plugin_mode]
            if (sel_track and (((offset + count) >= 0) and ((offset + count) < len(sel_track.devices)))):
                s.show_full_enlighted_poti()
            else:
                s.unlight_vpot_leds()
            count += 1




    def __update_channel_strip_strings(self):
        """ In IO mode, collect all strings that will be visible in the main display manually
    """
        if (not self._ChannelStripController__any_slider_is_touched()):
            if (self._ChannelStripController__assignment_mode == CSM_IO):
                targets = []
                for s in self._ChannelStripController__channel_strips:
                    if self._ChannelStripController__routing_target(s):
                        targets.append(self._ChannelStripController__routing_target(s))
                    else:
                        targets.append('')

                self._ChannelStripController__main_display_controller.set_channel_strip_strings(targets)
            elif ((self._ChannelStripController__assignment_mode == CSM_PLUGINS) and (self._ChannelStripController__plugin_mode == PCM_DEVICES)):
                for plugin in self._ChannelStripController__displayed_plugins:
                    if (plugin != None):
                        plugin.remove_name_listener(self._ChannelStripController__update_plugin_names)

                self._ChannelStripController__displayed_plugins = []
                sel_track = self.song().view.selected_track
                for i in range(len(self._ChannelStripController__channel_strips)):
                    device_index = (i + self._ChannelStripController__plugin_mode_offsets[PCM_DEVICES])
                    if ((device_index >= 0) and (device_index < len(sel_track.devices))):
                        sel_track.devices[device_index].add_name_listener(self._ChannelStripController__update_plugin_names)
                        self._ChannelStripController__displayed_plugins.append(sel_track.devices[device_index])
                    else:
                        self._ChannelStripController__displayed_plugins.append(None)

                self._ChannelStripController__update_plugin_names()



    def __update_plugin_names(self):
        assert ((self._ChannelStripController__assignment_mode == CSM_PLUGINS) and (self._ChannelStripController__plugin_mode == PCM_DEVICES))
        device_strings = []
        for plugin in self._ChannelStripController__displayed_plugins:
            if (plugin != None):
                device_strings.append(plugin.name)
            else:
                device_strings.append('')

        self._ChannelStripController__main_display_controller.set_channel_strip_strings(device_strings)



    def __update_view_returns_mode(self):
        """ Update the control return tracks LED
    """
        if self._ChannelStripController__view_returns:
            self.send_midi((NOTE_ON_STATUS,
             SID_FADERBANK_EDIT,
             BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS,
             SID_FADERBANK_EDIT,
             BUTTON_STATE_OFF))
        self._ChannelStripController__main_display_controller.set_show_return_track_names(self._ChannelStripController__view_returns)
        self._ChannelStripController__reassign_channel_strip_offsets()
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
        self.request_rebuild_midi_map()



    def __on_selected_track_changed(self):
        """ Notifier, called as soon as the selected track has changed
    """
        st = self._ChannelStripController__last_attached_selected_track
        if (st and st.devices_has_listener(self._ChannelStripController__on_selected_device_chain_changed)):
            st.remove_devices_listener(self._ChannelStripController__on_selected_device_chain_changed)
        self._ChannelStripController__last_attached_selected_track = self.song().view.selected_track
        st = self._ChannelStripController__last_attached_selected_track
        if st:
            st.add_devices_listener(self._ChannelStripController__on_selected_device_chain_changed)
        if (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
            self._ChannelStripController__plugin_mode_offsets = [ 0 for x in range(PCM_NUMMODES) ]
            if (self._ChannelStripController__chosen_plugin != None):
                self._ChannelStripController__chosen_plugin.remove_parameters_listener(self._ChannelStripController__on_parameter_list_of_chosen_plugin_changed)
            self._ChannelStripController__chosen_plugin = None
            self._ChannelStripController__ordered_plugin_parameters = []
            self._ChannelStripController__update_assignment_display()
            if (self._ChannelStripController__plugin_mode == PCM_DEVICES):
                self._ChannelStripController__update_vpot_leds_in_plugins_device_choose_mode()
            else:
                self._ChannelStripController__set_plugin_mode(PCM_DEVICES)
        elif (self._ChannelStripController__assignment_mode == CSM_SENDS):
            self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
            self._ChannelStripController__update_assignment_display()
            self.request_rebuild_midi_map()



    def __on_flip_changed(self):
        """ Update the flip button LED when the flip mode changed
    """
        self._ChannelStripController__update_flip_led()
        if self._ChannelStripController__can_flip():
            self._ChannelStripController__update_assignment_display()
            self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
            self.request_rebuild_midi_map()



    def __on_selected_device_chain_changed(self):
        if (self._ChannelStripController__assignment_mode == CSM_PLUGINS):
            if (self._ChannelStripController__plugin_mode == PCM_DEVICES):
                self._ChannelStripController__update_vpot_leds_in_plugins_device_choose_mode()
                self._ChannelStripController__update_page_switch_leds()
            elif (self._ChannelStripController__plugin_mode == PCM_PARAMETERS):
                if (not self._ChannelStripController__chosen_plugin):
                    self._ChannelStripController__set_plugin_mode(PCM_DEVICES)
                elif (not (delf._ChannelStripController__chosen_plugin in self._ChannelStripController__last_attached_selected_track.devices)):
                    if (self._ChannelStripController__chosen_plugin != None):
                        self._ChannelStripController__chosen_plugin.remove_parameters_listener(self._ChannelStripController__on_parameter_list_of_chosen_plugin_changed)
                    self._ChannelStripController__chosen_plugin = None
                    self._ChannelStripController__set_plugin_mode(PCM_DEVICES)



    def __on_tracks_added_or_deleted(self):
        """ Notifier, called as soon as tracks where added, removed or moved
    """
        self._ChannelStripController__within_track_added_or_deleted = True
        for t in (self.song().tracks + self.song().return_tracks):
            if (not t.solo_has_listener(self._ChannelStripController__update_rude_solo_led)):
                t.add_solo_listener(self._ChannelStripController__update_rude_solo_led)
            if (not t.has_audio_output_has_listener(self._ChannelStripController__on_any_tracks_output_type_changed)):
                t.add_has_audio_output_listener(self._ChannelStripController__on_any_tracks_output_type_changed)

        if (self._ChannelStripController__send_mode_offset >= len(self.song().return_tracks)):
            self._ChannelStripController__send_mode_offset = 0
            self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
            self._ChannelStripController__update_channel_strip_strings()
        if ((self._ChannelStripController__strip_offset() + len(self._ChannelStripController__channel_strips)) >= self._ChannelStripController__controlled_num_of_tracks()):
            self._ChannelStripController__set_channel_offset(max(0, (self._ChannelStripController__controlled_num_of_tracks() - len(self._ChannelStripController__channel_strips))))
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
        self._ChannelStripController__update_channel_strip_strings()
        if (self._ChannelStripController__assignment_mode == CSM_SENDS):
            self._ChannelStripController__update_page_switch_leds()
        self.refresh_state()
        self._ChannelStripController__main_display_controller.refresh_state()
        self._ChannelStripController__within_track_added_or_deleted = False
        self.request_rebuild_midi_map()



    def __on_any_tracks_output_type_changed(self):
        """ called as soon as any device chain has changed (devices where
        added/removed/swapped...)
    """
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
        self.request_rebuild_midi_map()



    def __on_parameter_list_of_chosen_plugin_changed(self):
        assert (self._ChannelStripController__chosen_plugin != None)
        assert (self._ChannelStripController__plugin_mode == PCM_PARAMETERS)
        self._ChannelStripController__reorder_parameters()
        self._ChannelStripController__reassign_channel_strip_parameters(for_display_only=False)
        self.request_rebuild_midi_map()



    def __reorder_parameters(self):
        result = []
        if self._ChannelStripController__chosen_plugin:
            result = [ (p,
             p.name) for p in self._ChannelStripController__chosen_plugin.parameters ]
        self._ChannelStripController__ordered_plugin_parameters = result




# local variables:
# tab-width: 4
